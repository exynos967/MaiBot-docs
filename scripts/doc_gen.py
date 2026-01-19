import json
import os
import re
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

from config import config
from llm_client import HttpError, detect_api_style, generate_text


class DocGenerator:
    def __init__(self):
        if not config.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY (or OPENAI_API_KEY) is not set in environment variables.")

        self.__api_key = config.GEMINI_API_KEY
        self.base_url = config.BASE_URL.rstrip("/")
        self.model_name = config.MODEL_NAME
        self.api_style = config.LLM_API_STYLE
        self.docs_root = config.DOCS_ROOT
        self.show_base_url_in_logs = config.SHOW_BASE_URL_IN_LOGS

        # LLM docs are organized into modular categories (AstrBot-docs-like).
        # For maim_message we do NOT predefine categories; the LLM will decide them during bootstrap.
        repo_key = f"{(config.REPO_NAME or '').lower()}|{(self.docs_root or '').lower()}"
        if "maim_message" in repo_key:
            self.categories: List[str] = []
            self.default_category = "modules"
        else:
            self.categories = [
                "ai_integration",
                "design_standards",
                "messages",
                "platform_adapters",
                "plugin_system",
                "plugin_system/api",
                "learning_system",
                "storage_utils",
            ]
            self.default_category = "design_standards"

        self._category_segment_re = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9_-]*$")

    def _get_max_tokens(self, per_call_env: str, default: int) -> int:
        """Resolve max_tokens from env, prioritizing a single global knob."""
        raw_global = (os.getenv("LLM_MAX_OUTPUT_TOKENS") or os.getenv("LLM_MAX_TOKENS") or "").strip()
        raw_specific = (os.getenv(per_call_env) or "").strip() if per_call_env else ""

        def parse_int(raw: str) -> int:
            try:
                return int(raw)
            except Exception:
                return 0

        v = parse_int(raw_global) if raw_global else 0
        if v <= 0:
            v = parse_int(raw_specific) if raw_specific else 0
        if v <= 0:
            v = int(default)
        return max(1, v)

    def _get_temperature(self, env_var: str = "LLM_TEMPERATURE", default: float = 0.2) -> float:
        """Resolve temperature from env with clamping to a safe range."""
        raw = (os.getenv(env_var) or "").strip()
        if not raw:
            return float(default)
        try:
            v = float(raw)
        except Exception:
            return float(default)
        if v < 0:
            v = 0.0
        if v > 2:
            v = 2.0
        return v

    def _quote_yaml_string(self, value: str) -> str:
        v = (value or "").strip()
        if not v:
            return '""'
        if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
            return v
        if '"' not in v:
            return f'"{v}"'
        if "'" not in v:
            return f"'{v}'"
        esc = v.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{esc}"'

    def _sanitize_frontmatter(self, content: str) -> str:
        """Best-effort sanitize YAML frontmatter to avoid VitePress build failures."""
        if not isinstance(content, str) or not content.strip():
            return content

        # Strip BOM if present (some editors / model outputs may include it).
        if content.startswith("\ufeff"):
            content = content.lstrip("\ufeff")

        lines = content.splitlines()
        if not lines or lines[0].strip() != "---":
            return content

        end = None
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                end = i
                break
        if end is None:
            return content

        fm = lines[1:end]
        changed = False
        for idx, line in enumerate(fm):
            m = re.match(r"^(\s*title\s*:\s*)(.+?)\s*$", line)
            if not m:
                continue
            prefix = m.group(1)
            value = m.group(2).strip()
            if not value:
                continue
            if value.startswith(("'", '"')) and value.endswith(("'", '"')):
                continue
            fm[idx] = f"{prefix}{self._quote_yaml_string(value)}"
            changed = True

        if not changed:
            return content

        new_lines = [lines[0]] + fm + [lines[end]] + lines[end + 1 :]
        out = "\n".join(new_lines)
        if content.endswith("\n"):
            out += "\n"
        return out

    def _schema_repo_map(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "repo": {"type": "string"},
                "branch": {"type": "string"},
                "generated_at": {"type": "string"},
                "summary": {"type": "string"},
                "module_groups": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "name": {"type": "string"},
                            "path_prefixes": {"type": "array", "items": {"type": "string"}},
                            "responsibility": {"type": "string"},
                        },
                        "required": ["name", "path_prefixes", "responsibility"],
                    },
                },
                "public_surfaces": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "name": {"type": "string"},
                            "kind": {"type": "string"},
                            "location": {"type": "string"},
                            "notes": {"type": "string"},
                        },
                        "required": ["name", "kind", "location", "notes"],
                    },
                },
                "doc_group_suggestions": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "group_path": {"type": "string"},
                            "rationale": {"type": "string"},
                            "related_paths": {"type": "array", "items": {"type": "string"}},
                        },
                        "required": ["group_path", "rationale", "related_paths"],
                    },
                },
                "limitations": {"type": "string"},
                "evidence": {"type": "array", "items": {"type": "string"}},
            },
            "required": [
                "repo",
                "branch",
                "generated_at",
                "summary",
                "module_groups",
                "public_surfaces",
                "doc_group_suggestions",
                "limitations",
                "evidence",
            ],
        }

    def _schema_dir_analysis(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "dir": {"type": "string"},
                "chunk_index": {"type": "number"},
                "chunk_total": {"type": "number"},
                "files": {"type": "array", "items": {"type": "string"}},
                "summary": {"type": "string"},
                "public_contracts": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "name": {"type": "string"},
                            "kind": {"type": "string"},
                            "defined_in": {"type": "string"},
                            "signature": {"type": "string"},
                            "notes": {"type": "string"},
                        },
                        "required": ["name", "kind", "defined_in", "signature", "notes"],
                    },
                },
                "key_components": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "name": {"type": "string"},
                            "defined_in": {"type": "string"},
                            "responsibility": {"type": "string"},
                        },
                        "required": ["name", "defined_in", "responsibility"],
                    },
                },
                "configs": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "name": {"type": "string"},
                            "defined_in": {"type": "string"},
                            "type": {"type": "string"},
                            "notes": {"type": "string"},
                        },
                        "required": ["name", "defined_in", "type", "notes"],
                    },
                },
                "dependencies": {"type": "array", "items": {"type": "string"}},
                "risks": {"type": "array", "items": {"type": "string"}},
                "limitations": {"type": "string"},
                "evidence": {"type": "array", "items": {"type": "string"}},
            },
            "required": [
                "dir",
                "chunk_index",
                "chunk_total",
                "files",
                "summary",
                "public_contracts",
                "key_components",
                "configs",
                "dependencies",
                "risks",
                "limitations",
                "evidence",
            ],
        }

    def _schema_bootstrap_doc_plan(self) -> Dict[str, Any]:
        return {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "target_category": {"type": "string"},
                    "file_name": {"type": "string"},
                    "title": {"type": "string"},
                    "source_dirs": {"type": "array", "items": {"type": "string"}},
                    "reason": {"type": "string"},
                    "evidence": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["target_category", "file_name", "title", "source_dirs", "reason", "evidence"],
            },
        }

    def _schema_doc_page(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "target_category": {"type": "string"},
                "file_name": {"type": "string"},
                "content": {"type": "string"},
                "evidence": {"type": "array", "items": {"type": "string"}},
                "reason": {"type": "string"},
            },
            "required": ["target_category", "file_name", "content", "evidence", "reason"],
        }

    def _schema_doc_update(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "action": {"type": "string"},
                "target_category": {"type": "string"},
                "file_name": {"type": "string"},
                "content": {"type": "string"},
                "evidence": {"type": "array", "items": {"type": "string"}},
                "reason": {"type": "string"},
            },
            "required": ["action", "target_category", "file_name", "content", "evidence", "reason"],
        }

    def _schema_bootstrap_docs(self) -> Dict[str, Any]:
        return {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "target_category": {"type": "string"},
                    "file_name": {"type": "string"},
                    "content": {"type": "string"},
                    "evidence": {"type": "array", "items": {"type": "string"}},
                    "reason": {"type": "string"},
                },
                "required": ["target_category", "file_name", "content", "evidence", "reason"],
            },
        }

    def _is_safe_category_path(self, category: str) -> bool:
        category = (category or "").strip().strip("/")
        if not category:
            return False
        if category.startswith(("/", "\\")):
            return False
        if "\\" in category or ":" in category:
            return False
        parts = [p for p in category.split("/") if p]
        if not parts:
            return False
        for part in parts:
            if part in {".", ".."}:
                return False
            if part.startswith("."):
                return False
            if part == "snapshots":
                return False
            if not self._category_segment_re.match(part):
                return False
        return True

    def _normalize_category_path(self, category: str) -> str:
        category = (category or "").strip().replace("\\", "/").strip("/")
        return category

    def _get_base_context(self) -> str:
        """递归读取 docs_root 下的 md 文件作为上下文（排除 snapshots/，并做长度限制）。"""
        if not os.path.exists(self.docs_root):
            return ""

        max_files = int(os.getenv("DOC_CONTEXT_MAX_FILES", "40") or "40")
        max_chars_per_file = int(os.getenv("DOC_CONTEXT_MAX_CHARS_PER_FILE", "2000") or "2000")
        max_total_chars = int(os.getenv("DOC_CONTEXT_MAX_TOTAL_CHARS", "40000") or "40000")

        context: List[str] = []
        total_chars = 0
        included = 0
        for root, _, files in os.walk(self.docs_root):
            if "snapshots" in root.split(os.sep):
                continue
            for filename in sorted(files):
                if not filename.endswith(".md"):
                    continue
                full_path = os.path.join(root, filename)
                rel_path = os.path.relpath(full_path, self.docs_root)
                with open(full_path, "r", encoding="utf-8") as f:
                    text = f.read() or ""
                    if len(text) > max_chars_per_file:
                        text = text[:max_chars_per_file] + "\n\n...[truncated]..."
                    chunk = f"--- Doc: {rel_path} ---\n{text}"
                    if total_chars + len(chunk) > max_total_chars:
                        return "\n\n".join(context)
                    context.append(chunk)
                    total_chars += len(chunk)
                    included += 1
                    if included >= max_files:
                        return "\n\n".join(context)

        return "\n\n".join(context)

    def _mask_sensitive(self, text: str) -> str:
        if not self.__api_key:
            return text
        return (text or "").replace(self.__api_key, "***")

    def _handle_exception(self, e: Exception, context: str) -> None:
        error_msg = self._mask_sensitive(str(e))
        print(f"{context} 出错: {error_msg}")

        if isinstance(e, HttpError):
            print(f"API 诊断: 状态码={e.status_code}, 消息={error_msg}")
            if e.status_code == 401:
                print("诊断建议: API Key 无效，请检查环境变量 GEMINI_API_KEY。")
            elif e.status_code == 403:
                print("诊断建议: 权限不足或被封禁，请检查 API Key 权限或 IP 区域。")
            elif e.status_code == 429:
                print("诊断建议: 触发频率限制，请稍后再试或更换 API Key。")
            elif e.status_code >= 500:
                print("诊断建议: 上游服务端错误，请稍后重试。")

        print("提示: 如需排查连通性，可运行 `python scripts/test_api.py`。")

    def _call_llm(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
        response_schema: Optional[Dict[str, Any]] = None,
        response_schema_name: str = "output",
    ) -> str:
        print(f"发起请求: model={self.model_name}")
        if self.show_base_url_in_logs:
            print(f"  - Base URL: {self._mask_sensitive(self.base_url)}")
        else:
            print("  - Base URL: (hidden)")
        print(f"  - API Style: {self.api_style}")
        print(f"  - Temperature: {temperature}")

        # Global output token cap (optional).
        raw_cap = os.getenv("LLM_MAX_OUTPUT_TOKENS") or os.getenv("LLM_MAX_TOKENS") or ""
        try:
            cap = int(raw_cap) if raw_cap.strip() else 0
        except Exception:
            cap = 0
        if cap > 0:
            max_tokens = max(1, min(int(max_tokens), cap))

        response_format = None
        structured_enabled = (os.getenv("LLM_STRUCTURED_OUTPUT") or "1").strip().lower() not in {"0", "false", "no"}
        if structured_enabled:
            try:
                style = detect_api_style(self.base_url, self.api_style)
            except Exception:
                style = "auto"

            if style == "openai" and response_schema is not None:
                schema_name = (response_schema_name or "output").strip()
                schema_name = re.sub(r"[^a-zA-Z0-9_-]+", "_", schema_name)[:64] or "output"
                response_format = {
                    "type": "json_schema",
                    "json_schema": {
                        "name": schema_name,
                        "strict": True,
                        "schema": response_schema,
                    },
                }
            elif style == "openai" and response_schema is None and "json" in (prompt or "").lower():
                # Best-effort JSON mode when no schema is provided but the prompt expects JSON.
                response_format = {"type": "json_object"}

        max_retries = 3
        for attempt in range(max_retries):
            try:
                return generate_text(
                    api_key=self.__api_key,
                    base_url=self.base_url,
                    model_name=self.model_name,
                    prompt=prompt,
                    system_instruction=system_instruction,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    response_format=response_format,
                    api_version=config.GEMINI_API_VERSION,
                    api_style=self.api_style,
                    timeout_seconds=600,
                )
            except HttpError as e:
                if e.status_code in [403, 429] and attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 2
                    print(f"收到 API 错误 {e.status_code}，正在进行第 {attempt + 1} 次重试，等待 {wait_time} 秒...")
                    time.sleep(wait_time)
                    continue
                raise e
            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 2
                    print(f"请求发生异常: {self._mask_sensitive(str(e))}，正在进行第 {attempt + 1} 次重试...")
                    time.sleep(wait_time)
                    continue
                raise e

        raise RuntimeError("unreachable")

    @dataclass
    class _JsonParseError(Exception):
        message: str
        raw_preview: str = ""

        def __str__(self) -> str:  # pragma: no cover
            if self.raw_preview:
                return f"{self.message} | preview={self.raw_preview}"
            return self.message

    def _escape_newlines_in_json_strings(self, s: str) -> str:
        """Escape raw newlines inside double-quoted JSON strings (LLM often outputs invalid JSON)."""
        if not s:
            return s

        out: List[str] = []
        in_string = False
        escape = False
        for ch in s:
            if in_string:
                if escape:
                    out.append(ch)
                    escape = False
                    continue
                if ch == "\\":
                    out.append(ch)
                    escape = True
                    continue
                if ch == '"':
                    out.append(ch)
                    in_string = False
                    continue
                if ch == "\n":
                    out.append("\\n")
                    continue
                if ch == "\r":
                    out.append("\\r")
                    continue
                out.append(ch)
                continue

            if ch == '"':
                out.append(ch)
                in_string = True
                continue
            out.append(ch)

        return "".join(out)

    def _sanitize_json_like(self, s: str) -> str:
        """Best-effort sanitize common LLM JSON issues without changing semantics too much."""
        if not isinstance(s, str):
            return ""
        s = s.strip()
        if not s:
            return s

        # Normalize common smart quotes.
        s = (
            s.replace("\u201c", '"')
            .replace("\u201d", '"')
            .replace("\u2018", "'")
            .replace("\u2019", "'")
        )

        # Escape raw newlines inside quoted strings (invalid JSON otherwise).
        s = self._escape_newlines_in_json_strings(s)

        # Remove trailing commas before object/array close.
        for _ in range(5):
            new = re.sub(r",\s*([}\]])", r"\1", s)
            if new == s:
                break
            s = new

        return s

    def _raw_decode_first_json(self, s: str) -> Any:
        """Decode the first JSON value from a string (allows trailing text)."""
        decoder = json.JSONDecoder()
        s = (s or "").lstrip()
        if not s:
            raise self._JsonParseError("Empty response", raw_preview="")

        obj, _ = decoder.raw_decode(s)
        return obj

    def _try_parse_json(self, s: str) -> Any:
        s = self._sanitize_json_like(s)
        if not s:
            raise self._JsonParseError("Empty response after sanitize", raw_preview="")

        # 1) strict loads
        try:
            return json.loads(s)
        except Exception:
            pass

        # 2) raw decode (tolerate trailing text)
        try:
            return self._raw_decode_first_json(s)
        except Exception:
            pass

        # 3) scan for a plausible JSON start and raw decode from there
        starts = [m.start() for m in re.finditer(r"[\[{]", s)]
        for pos in starts[:50]:
            try:
                return self._raw_decode_first_json(s[pos:])
            except Exception:
                continue

        preview = s[:300].replace("\n", "\\n")
        raise self._JsonParseError("Failed to parse JSON from model output", raw_preview=preview)

    def _coerce_object_keys(
        self,
        obj: Dict[str, Any],
        required_keys: List[str],
        *,
        defaults: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Coerce near-miss keys into a fixed schema; drop unknown keys; fill missing with defaults."""
        required = list(required_keys)
        defaults = defaults or {}

        def canon(k: str) -> str:
            return re.sub(r"[^a-z0-9]", "", (k or "").lower())

        required_canon_to_key = {canon(k): k for k in required}
        out: Dict[str, Any] = {}

        # First pass: exact key or canonical match
        for k, v in (obj or {}).items():
            if k in required:
                out[k] = v
                continue
            ck = canon(str(k))
            if ck in required_canon_to_key:
                out[required_canon_to_key[ck]] = v
                continue

        # Second pass: substring match for common LLM typos (e.g. "ris risks" -> "risks")
        for k, v in (obj or {}).items():
            if k in out:
                continue
            ck = canon(str(k))
            if not ck:
                continue
            candidates = [rk for rk in required if canon(rk) and canon(rk) in ck]
            candidates = sorted(set(candidates), key=lambda x: len(canon(x)), reverse=True)
            if len(candidates) == 1 and candidates[0] not in out:
                out[candidates[0]] = v

        # Fill missing keys with safe defaults
        for k in required:
            if k not in out:
                out[k] = defaults.get(k, "")

        return out

    def _extract_json(self, text: str) -> Any:
        if not isinstance(text, str):
            raise self._JsonParseError("Model output is not a string", raw_preview=str(type(text)))

        # Prefer explicit json code fence, but still parse robustly.
        fence = re.search(r"```json\s*(.*?)\s*```", text, re.DOTALL | re.IGNORECASE)
        if fence:
            return self._try_parse_json(fence.group(1))

        # Otherwise parse from the first JSON value in the response.
        return self._try_parse_json(text)

    def _extract_changed_paths(self, diff: str) -> List[str]:
        paths: List[str] = []
        if not diff:
            return paths
        for match in re.finditer(r"^diff --git a/(.+?) b/(.+?)$", diff, flags=re.MULTILINE):
            a_path = match.group(1).strip()
            b_path = match.group(2).strip()
            if a_path and a_path not in paths:
                paths.append(a_path)
            if b_path and b_path not in paths:
                paths.append(b_path)
        return paths

    def _should_skip_by_paths(self, paths: List[str]) -> bool:
        ignore_prefixes = (
            ".github/",
            ".vscode/",
            "docs/",
            "doc/",
            "website/",
            "web/",
            "dashboard/",
            "frontend/",
            "front/",
            "ui/",
            "assets/",
        )
        ignore_exact = {
            "README.md",
            "README.zh.md",
            "CHANGELOG.md",
            "pnpm-lock.yaml",
            "package-lock.json",
            "yarn.lock",
            "package.json",
        }
        ignore_suffixes = (
            ".png",
            ".jpg",
            ".jpeg",
            ".gif",
            ".svg",
            ".ico",
            ".lock",
        )

        def is_ignored(path: str) -> bool:
            p = (path or "").lstrip("./")
            if p in ignore_exact:
                return True
            if p.startswith(ignore_prefixes):
                return True
            if p.endswith(ignore_suffixes):
                return True
            if p.endswith((".vue", ".ts", ".tsx", ".js", ".jsx", ".css", ".scss", ".less", ".html")):
                return True
            return False

        if paths and all(is_ignored(p) for p in paths):
            return True
        if paths and all(
            p.endswith((".vue", ".ts", ".tsx", ".js", ".jsx", ".css", ".scss", ".less", ".html")) for p in paths
        ):
            return True
        return False

    def should_update_docs(self, commit_message: str, diff: str) -> bool:
        changed_paths = self._extract_changed_paths(diff)
        if changed_paths and self._should_skip_by_paths(changed_paths):
            print("AI filtering skipped: only non-dev-doc relevant paths changed.")
            return False

        system_instruction = "你是一个文档维护助手，只能根据给定的 Commit Message 和 Diff 做判断。"
        prompt = f"""
你是一个文档维护助手。请判断以下代码变更（Commit/PR）是否会影响第三方开发者（插件/适配器/接口调用方），从而需要更新开发文档。

Commit Message:
{commit_message}

Diff Snippet:
{diff[:2000]}

规则：
1. 仅当变更影响对外契约（如对外 API、事件/消息模型、配置 schema、插件/适配器接口、兼容性与对外行为）时，才需要更新文档。
2. 如果只是内部重构、WebUI/前端细节、日志/注释、CI 配置、测试用例、纯格式调整，通常不需要更新文档。

请仅回答 "YES" 或 "NO"（可以在 YES 后面附带 1 句极短理由/证据）。
        """
        try:
            result = self._call_llm(
                prompt,
                system_instruction=system_instruction,
                temperature=0,
                max_tokens=min(64, self._get_max_tokens("", 10)),
            ).strip().upper()
            return "YES" in result
        except Exception as e:
            self._handle_exception(e, "AI filtering")
            return False

    def _preprocess_diff(self, diff: str) -> str:
        line_count = diff.count("\n")
        if line_count < 500:
            return diff

        print(f"检测到变更量较大 ({line_count} 行)。正在生成技术摘要以供 AI 分析...")
        system_instruction = "你是一个专业的技术摘要生成器，擅长将冗长的代码 Diff 转换为紧凑的技术摘要。"
        summary_prompt = f"""
	你是一个资深系统架构师。以下是一个巨大的代码变更 Diff。
	由于 Diff 过长，请你将其压缩为一个**高密度的技术摘要**。

要求：
1. 必须保留所有新增/修改的类名、接口定义、重要方法签名、新增配置项。
2. 清晰描述数据流或调用链路的变化。
3. 剔除样板代码、简单导入变化、纯格式调整。

	--- Diff ---
	{diff[:30000]}
	"""
        try:
            summary = self._call_llm(
                summary_prompt,
                system_instruction=system_instruction,
                temperature=self._get_temperature(),
                max_tokens=self._get_max_tokens("LLM_DIFF_SUMMARY_MAX_TOKENS", 8192),
            )
            return f"[Large Diff Summary]\n{summary}\n\n[Note: Original diff was {line_count} lines and was summarized.]"
        except Exception as e:
            self._handle_exception(e, "summarizing diff")
            return diff[:10000]

    def _validate_change(self, change: Dict, processed_diff: str, commit_message: str) -> Optional[str]:
        action = (change.get("action") or "").strip().lower()
        if action not in {"create", "update", "noop"}:
            return "action must be one of: create/update/noop"

        if action == "noop":
            return None

        file_name = (change.get("file_name") or "").strip()
        if not file_name.endswith(".md"):
            return "file_name must end with .md"
        if action == "create" and file_name == "index.md":
            return "file_name must not be index.md for create"
        if any(x in file_name for x in ["/", "\\", ".."]):
            return "file_name must be a plain filename (no path)"

        target_category = self._normalize_category_path(change.get("target_category") or "")
        if action == "create":
            if not target_category:
                return "target_category is required"
            if not self._is_safe_category_path(target_category):
                return "target_category must be a safe relative path under docs root (e.g. plugin_system/api)"

        content = change.get("content")
        if not isinstance(content, str) or not content.strip():
            return "content must be a non-empty string"
        if not content.lstrip().startswith("---"):
            return "content must start with YAML frontmatter ('---')"

        evidence = change.get("evidence")
        if not isinstance(evidence, list) or len(evidence) < 2:
            return "evidence must be a list with at least 2 items"

        haystack = f"{commit_message}\n{processed_diff}"
        matched = 0
        for item in evidence:
            if not isinstance(item, str):
                continue
            token = item.strip().strip("`")
            if token and token in haystack:
                matched += 1
        if matched < 2:
            return "evidence items must appear in commit message or diff"

        return None

    def _validate_bootstrap_item(self, item: Dict, repo_context: str) -> Optional[str]:
        file_name = (item.get("file_name") or "").strip()
        if not file_name.endswith(".md"):
            return "file_name must end with .md"
        if file_name == "index.md":
            return "file_name must not be index.md"
        if any(x in file_name for x in ["/", "\\", ".."]):
            return "file_name must be a plain filename (no path)"

        target_category = self._normalize_category_path(item.get("target_category") or "")
        if not target_category:
            return "target_category is required"
        if not self._is_safe_category_path(target_category):
            return "target_category must be a safe relative path under docs root (e.g. plugin_system/api)"

        content = item.get("content")
        if not isinstance(content, str) or not content.strip():
            return "content must be a non-empty string"
        if not content.lstrip().startswith("---"):
            return "content must start with YAML frontmatter ('---')"

        required_sections = ("## 概述", "## 目录/结构", "## 适用范围", "## 变更影响分析")
        for sec in required_sections:
            if sec not in content:
                return f"content must include section: {sec}"

        evidence = item.get("evidence")
        if not isinstance(evidence, list) or len(evidence) < 2:
            return "evidence must be a list with at least 2 items"

        matched = 0
        for ev in evidence:
            if not isinstance(ev, str):
                continue
            token = ev.strip().strip("`")
            if token and token in repo_context:
                matched += 1
        if matched < 2:
            return "evidence items must appear in provided repo context"

        return None

    def generate_bootstrap_docs(self, repo_context: str) -> List[Dict]:
        """基于仓库结构与 README 的快照生成初始文档（用于首次建档/重建基线）。"""
        base_context = self._get_base_context()
        today = datetime.now().strftime("%Y-%m-%d")
        categories_str = ", ".join(self.categories) if self.categories else "（无预设分类：请根据仓库结构自行创建 docs_root 下的分组目录）"
        repo_name = config.REPO_NAME
        branch = config.UPSTREAM_BRANCH

        system_instruction = "你是一个只输出 JSON 的文档助手。禁止编造，不得输出非 JSON 内容。"
        prompt = f"""
你是一个高级软件工程师和技术文档专家。你的任务是为 `{repo_name}` 的 `{branch}` 分支生成**初始**开发文档（按模块分组，面向 AI/RAG）。

注意：你只能基于下面提供的“仓库信息”与“现有文档”，输出**概括性、可验证**的文档。若缺少细节，请明确写“需要以源码验证/需要补充信息”，不要猜测接口。

--- 可用分类 ---
推荐分类（可直接使用，也可在 docs_root 下创建新的子目录作为分类）：
{categories_str}

--- 仓库信息（快照） ---
{repo_context}

--- 现有文档（可能为空） ---
{base_context}

--- 输出要求 ---
1) 只输出一个 JSON 数组（最多 12 项），每一项是一个对象，仅包含这些 key：
   - target_category: 文档落盘目录（相对 docs_root）。可以使用推荐分类，也可以创建新目录（允许多级，如 plugin_system/api）。
     路径规则：只能包含字母/数字/下划线/短横线与 `/`，不能以 `.` 开头、不能包含 `..`、不能是 `snapshots`。
   - file_name: 纯文件名，以 .md 结尾，禁止包含路径/..，且不能是 index.md
   - content: Markdown，必须以 YAML frontmatter 开头，且至少包含以下章节：
       - ## 概述
       - ## 目录/结构（可用任意标题，但要清晰描述目录/模块）
       - ## 适用范围与边界（标题中必须包含“适用范围”）
       - ## 变更影响分析（初始建档也需要此章节）
   - evidence: 字符串数组（至少 2 条），每条必须能在“仓库信息（快照）”中找到原样子串（建议使用路径/文件名/目录名/README 中的专有名词）
   - reason: 1 句理由（为什么需要这些文档作为初始基线）
2) frontmatter 字段必须包含：
   ---
   title: (简洁标题)
   type: (feature | improvement | refactor)
   status: (stable | experimental)
   last_updated: {today}
   related_base: (可为空)
   ---
3) 尽量覆盖多个分类（至少 4 个不同分类）；文档尽量短（每篇不超过 200 行），用于后续增量迭代完善。
"""

        created: List[Dict] = []
        try:
            raw_response = self._call_llm(
                prompt,
                system_instruction=system_instruction,
                temperature=self._get_temperature(),
                max_tokens=self._get_max_tokens("LLM_BOOTSTRAP_DOCS_MAX_TOKENS", 8192),
                response_schema=self._schema_bootstrap_docs(),
                response_schema_name="bootstrap_docs",
            )
            result = self._extract_json(raw_response)
            items = result if isinstance(result, list) else [result]

            for item in items:
                if not isinstance(item, dict):
                    continue
                validation_error = self._validate_bootstrap_item(item, repo_context)
                if validation_error:
                    print(f"Bootstrap AI output validation failed: {validation_error}")
                    continue

                change = {
                    "action": "create",
                    "target_category": item.get("target_category") or self.default_category,
                    "file_name": item.get("file_name"),
                    "content": item.get("content"),
                }
                file_path = self._apply_change(change)
                if file_path:
                    title = item.get("file_name") or ""
                    content = item.get("content") or ""
                    for line in content.splitlines():
                        if line.startswith("title:"):
                            title = line.replace("title:", "").strip()
                            break
                    created.append({"file_path": file_path, "action": "create", "title": title})
        except Exception as e:
            self._handle_exception(e, "Bootstrap 生成")

        return created

    def generate_doc_update(self, commit_message: str, diff: str) -> Optional[Dict]:
        base_context = self._get_base_context()
        processed_diff = self._preprocess_diff(diff)
        today = datetime.now().strftime("%Y-%m-%d")
        categories_str = ", ".join(self.categories) if self.categories else "（无预设分类：请根据仓库结构与现有文档自行决定分组目录）"
        repo_name = config.REPO_NAME
        branch = config.UPSTREAM_BRANCH

        system_instruction = "你是一个只输出 JSON 的文档助手。禁止编造，不得引入 Diff/Summary 中不存在的符号或行为。"
        prompt = f"""
你是一个高级软件工程师和技术文档专家。你的任务是维护 `{repo_name}` 的 `{branch}` 分支开发文档（按模块分组，面向 AI/RAG）。

--- 当前分类结构 ---
推荐分类（可直接使用，也可在 docs_root 下创建新的子目录作为分类）：
{categories_str}

--- 上下文（现有文档） ---
{base_context}

--- 当前变更（Diff or Summary） ---
{processed_diff}

--- Commit Message ---
{commit_message}

--- 任务要求 ---
0. 禁止编造：只允许描述上面 Diff/Summary 中可以直接佐证的变更。
1. 判断操作：
   - 若变更不影响第三方开发者（对外契约/行为未变），返回 action: \"noop\" 并给出 reason（1 句）。
   - 全新对外契约/行为：action 为 \"create\"。
   - 对现有文档的显著修订：action 为 \"update\"。
2. 证据约束（必须满足，否则用 noop）：
   - 必须提供 evidence 数组（至少 2 条），每条为原样字符串（建议使用文件路径/符号名），且必须能在 Diff/Summary 或 Commit Message 中找到。
3. 生成内容规范：
   - Markdown 必须以 YAML frontmatter 开头：
     ---
     title: (简洁的功能名称)
     type: (feature | improvement | refactor)
     status: (stable | experimental)
     last_updated: {today}
     related_base: (关联基础文档文件名，可为空)
     ---
   - 必须包含一个名为 \"## 变更影响分析\" 的区块，说明边界情况/兼容性/最佳实践。
4. 输出格式：
   - 只能返回 JSON 对象，且只能包含这些 key：action, target_category, file_name, content, evidence, reason

补充约束：
- 若 action 为 create，target_category 为文档落盘目录（相对 docs_root），允许多级（如 plugin_system/api）。
  路径规则：只能包含字母/数字/下划线/短横线与 `/`，不能以 `.` 开头、不能包含 `..`、不能是 `snapshots`。

--- 示例输出结构 ---
{{
  \"action\": \"create\",
  \"target_category\": \"design_standards\",
  \"file_name\": \"new_feature.md\",
  \"content\": \"---\\ntitle: ...\\n...\\n---\\n\\n## 概述\\n...\\n## 关键实现\\n...\\n## 变更影响分析\\n...\",\n  \"evidence\": [\"path/to/file.py\", \"ClassName.method\"],\n  \"reason\": \"\"\n}}
        """
        try:
            raw_response = self._call_llm(
                prompt,
                system_instruction=system_instruction,
                temperature=self._get_temperature(),
                response_schema=self._schema_doc_update(),
                response_schema_name="doc_update",
            )
            result = self._extract_json(raw_response)
            validation_error = self._validate_change(result, processed_diff, commit_message)
            if validation_error:
                if (result.get("action") or "").strip().lower() == "noop":
                    print(f"AI returned noop: {result.get('reason', '').strip()}")
                    return None
                print(f"AI output validation failed: {validation_error}")
                return None

            if (result.get("action") or "").strip().lower() == "noop":
                print(f"AI returned noop: {result.get('reason', '').strip()}")
                return None

            file_path = self._apply_change(result)
            if file_path:
                title = result.get("file_name") or ""
                content = result.get("content") or ""
                for line in content.splitlines():
                    if line.startswith("title:"):
                        title = line.replace("title:", "").strip()
                        break
                return {"file_path": file_path, "action": result.get("action"), "title": title}
            return None
        except Exception as e:
            self._handle_exception(e, "AI 生成")
            return None

    def _apply_change(self, change: Dict) -> Optional[str]:
        action = (change.get("action") or "").strip().lower()
        target_category = self._normalize_category_path(change.get("target_category") or self.default_category)
        file_name = (change.get("file_name") or "").strip()
        content = self._sanitize_frontmatter(change.get("content"))

        if not file_name or not isinstance(content, str) or not content.strip():
            print("Invalid change format from AI.")
            return None

        if not self._is_safe_category_path(target_category):
            print(f"Warning: Unsafe category path {target_category!r}. Using default.")
            target_category = self.default_category

        file_path: Optional[str] = None
        if action == "update":
            # Prefer the provided target_category if it already exists.
            if self._is_safe_category_path(target_category):
                preferred = os.path.join(self.docs_root, target_category, file_name)
                if os.path.exists(preferred):
                    file_path = preferred

            if not file_path:
                matches: List[str] = []
                for root, _, files in os.walk(self.docs_root):
                    if "snapshots" in root.split(os.sep):
                        continue
                    if file_name in files:
                        matches.append(os.path.join(root, file_name))
                if matches:
                    matches = sorted(set(matches))
                    if len(matches) > 1:
                        print(f"Warning: multiple matches for {file_name}; picking {matches[0]}")
                    file_path = matches[0]

            if not file_path:
                print(f"警告：请求更新 {file_name} 但未找到。将回退到创建操作。")
                action = "create"

        if action == "create" or not file_path:
            file_path = os.path.join(self.docs_root, target_category, file_name)

        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"已应用文档{action}：{file_path}")
        return file_path

    def write_markdown(self, *, target_category: str, file_name: str, content: str) -> str:
        """Write a markdown file under docs_root/target_category."""
        target_category = self._normalize_category_path(target_category)
        file_name = (file_name or "").strip()
        content = self._sanitize_frontmatter(content or "")

        if not self._is_safe_category_path(target_category):
            raise ValueError(f"Unsafe category path: {target_category!r}")
        if not file_name.endswith(".md"):
            raise ValueError("file_name must end with .md")
        if any(x in file_name for x in ["/", "\\", ".."]):
            raise ValueError("file_name must be a plain filename (no path)")
        if not content.strip():
            raise ValueError("content must be non-empty")

        file_path = os.path.join(self.docs_root, target_category, file_name)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return file_path

    def generate_repo_map(self, repo_context: str) -> Dict[str, Any]:
        """Stage 1: build a repo-level map used by later directory/page generation."""
        today = datetime.now().strftime("%Y-%m-%d")
        repo_name = config.REPO_NAME
        branch = config.UPSTREAM_BRANCH
        max_tokens = self._get_max_tokens("LLM_REPO_MAP_MAX_TOKENS", 8192)

        system_instruction = "你是一个只输出 JSON 的文档助手。禁止编造，不得输出非 JSON 内容。"
        prompt = f"""
你是一个资深软件架构师。请基于提供的“仓库信息（快照）”生成一个可复用的 RepoMap（用于后续逐目录分析与文档生成）。

约束：
- 禁止编造：只允许引用快照中可直接佐证的内容（路径、顶层签名、片段）。
- 需要标注不确定性：看不到实现细节时写清楚“需要以源码验证”。
- 输出必须是 JSON 对象，且必须包含以下 key（不得多、不得少）：
  - repo: string
  - branch: string
  - generated_at: string (YYYY-MM-DD)
  - summary: string
  - module_groups: array (each item: {{name, path_prefixes, responsibility}})
  - public_surfaces: array (each item: {{name, kind, location, notes}})
  - doc_group_suggestions: array (each item: {{group_path, rationale, related_paths}})
  - limitations: string
  - evidence: array (>= 5 items; every item must appear verbatim in the repo snapshot text)

--- 仓库信息（快照） ---
{repo_context}
        """
        try:
            raw = self._call_llm(
                prompt,
                system_instruction=system_instruction,
                temperature=self._get_temperature(),
                max_tokens=max_tokens,
                response_schema=self._schema_repo_map(),
                response_schema_name="repo_map",
            )
            obj = self._extract_json(raw)
            if not isinstance(obj, dict):
                raise ValueError("repo_map must be a JSON object")

            required_keys = [
                "repo",
                "branch",
                "generated_at",
                "summary",
                "module_groups",
                "public_surfaces",
                "doc_group_suggestions",
                "limitations",
                "evidence",
            ]
            defaults: Dict[str, Any] = {
                "repo": repo_name,
                "branch": branch,
                "generated_at": today,
                "summary": "",
                "module_groups": [],
                "public_surfaces": [],
                "doc_group_suggestions": [],
                "limitations": "",
                "evidence": [],
            }
            obj = self._coerce_object_keys(obj, required_keys, defaults=defaults)

            obj["repo"] = (obj.get("repo") or repo_name).strip()
            obj["branch"] = (obj.get("branch") or branch).strip()
            obj["generated_at"] = (obj.get("generated_at") or today).strip()

            evidence = obj.get("evidence")
            if not isinstance(evidence, list) or len(evidence) < 5:
                raise ValueError("repo_map.evidence must be a list with >= 5 items")

            matched = 0
            for ev in evidence:
                if isinstance(ev, str) and ev.strip() and ev.strip() in repo_context:
                    matched += 1
            if matched < 3:
                raise ValueError("repo_map.evidence must include at least 3 substrings present in repo_context")

            return obj
        except Exception as e:
            self._handle_exception(e, "RepoMap 生成")
            # Fall back to a minimal map (still valid JSON shape for later steps).
            return {
                "repo": repo_name,
                "branch": branch,
                "generated_at": today,
                "summary": "",
                "module_groups": [],
                "public_surfaces": [],
                "doc_group_suggestions": [],
                "limitations": "RepoMap generation failed; downstream steps will have reduced quality.",
                "evidence": [],
            }

    def analyze_directory_chunk(
        self,
        *,
        repo_map: Dict[str, Any],
        dir_path: str,
        chunk_index: int,
        chunk_total: int,
        files_block: str,
    ) -> Optional[Dict[str, Any]]:
        """Stage 2: analyze one directory chunk (fixed schema)."""
        max_tokens = self._get_max_tokens("LLM_DIR_ANALYSIS_MAX_TOKENS", 8192)
        repo_map_text = json.dumps(repo_map or {}, ensure_ascii=False)

        def extract_files_from_block(block: str) -> List[str]:
            """Extract file list from the chunk header (avoid regex to keep it robust)."""
            if not block:
                return []
            lines = (block or "").splitlines()
            files: List[str] = []
            in_list = False
            for line in lines:
                s = line.rstrip("\n")
                if not in_list:
                    if s.strip() == "Files in this chunk:":
                        in_list = True
                    continue
                # Stop at the first blank line after the list.
                if not s.strip():
                    break
                if s.lstrip().startswith("- "):
                    p = s.strip()[2:].strip()
                    if p:
                        files.append(p)
            return sorted(set(files))

        system_instruction = "你是一个只输出 JSON 的文档助手。禁止编造，不得输出非 JSON 内容。"
        prompt = f"""
	你是一个资深软件工程师。请基于以下上下文，对目录 `{dir_path}` 的这一个“分片”做结构化分析。

	重要规则：
	- 禁止编造：只能引用 files_block 中出现的内容（路径/符号/字面量）。
	- 每个结论必须可追溯：evidence 至少 2 条，且必须是 files_block 中出现的原样子串（建议用文件路径/类名/函数名）。
	- 严格输出纯 JSON：不要使用 ```json 代码块，不要输出任何解释文字。
	- 控制输出体积：不要枚举大量文件/符号。除 `files` 外，所有数组最多保留 5 个元素。
	- `files` 字段固定输出为空数组 `[]`（脚本会从 files_block 自动填充真实文件列表，避免输出过长导致截断）。

	输出必须是 JSON 对象，且 key 必须严格等于下面列表（不得多、不得少）：
	- dir: string
	- chunk_index: number
	- chunk_total: number
- files: array[string]
- summary: string
- public_contracts: array[{{name, kind, defined_in, signature, notes}}]
- key_components: array[{{name, defined_in, responsibility}}]
- configs: array[{{name, defined_in, type, notes}}]
- dependencies: array[string]
- risks: array[string]
- limitations: string
- evidence: array[string]

--- RepoMap ---
{repo_map_text}

--- files_block ---
{files_block}
        """
        try:
            raw = self._call_llm(
                prompt,
                system_instruction=system_instruction,
                temperature=self._get_temperature(),
                max_tokens=max_tokens,
                response_schema=self._schema_dir_analysis(),
                response_schema_name="dir_analysis",
            )
            obj = self._extract_json(raw)
            if isinstance(obj, list):
                # Some models may wrap the object in a single-item array.
                for it in obj:
                    if isinstance(it, dict):
                        obj = it
                        break
            if not isinstance(obj, dict):
                raise ValueError("directory analysis must be a JSON object")

            required_keys = [
                "dir",
                "chunk_index",
                "chunk_total",
                "files",
                "summary",
                "public_contracts",
                "key_components",
                "configs",
                "dependencies",
                "risks",
                "limitations",
                "evidence",
            ]
            defaults: Dict[str, Any] = {
                "dir": dir_path,
                "chunk_index": int(chunk_index),
                "chunk_total": int(chunk_total),
                "files": [],
                "summary": "",
                "public_contracts": [],
                "key_components": [],
                "configs": [],
                "dependencies": [],
                "risks": [],
                "limitations": "",
                "evidence": [],
            }
            obj = self._coerce_object_keys(obj, required_keys, defaults=defaults)

            # Enforce fixed schema control fields.
            obj["dir"] = dir_path
            obj["chunk_index"] = int(chunk_index)
            obj["chunk_total"] = int(chunk_total)

            files = obj.get("files")
            if isinstance(files, str) and files.strip():
                files = [files.strip()]
                obj["files"] = files
            if not isinstance(files, list):
                obj["files"] = []
                files = obj["files"]
            if not files:
                obj["files"] = extract_files_from_block(files_block)
                files = obj["files"]
            if files and not all(isinstance(x, str) and x.strip() for x in files):
                raise ValueError("analysis.files must be a list of strings")

            for key in ("public_contracts", "key_components", "configs"):
                if not isinstance(obj.get(key), list):
                    obj[key] = []

            for key in ("dependencies", "risks", "evidence"):
                if isinstance(obj.get(key), str) and obj.get(key).strip():
                    obj[key] = [obj.get(key).strip()]
                if not isinstance(obj.get(key), list):
                    obj[key] = []

            evidence = obj.get("evidence")
            if not isinstance(evidence, list):
                evidence = []
                obj["evidence"] = evidence

            normalized_evidence: List[str] = []
            for ev in evidence:
                if not isinstance(ev, str):
                    continue
                token = ev.strip().strip("`")
                if token and token in files_block:
                    normalized_evidence.append(token)
            normalized_evidence = sorted(set(normalized_evidence))
            if len(normalized_evidence) < 2:
                # Auto-fill evidence with file paths from the provided context to avoid dropping the analysis.
                fallback = extract_files_from_block(files_block)[:5]
                header_token = f"Directory: {dir_path}"
                if header_token in (files_block or ""):
                    fallback.append(header_token)
                normalized_evidence = fallback[:2] if len(fallback) >= 2 else fallback
            if len(normalized_evidence) < 2:
                raise ValueError("analysis.evidence must include >= 2 substrings present in files_block")

            obj["evidence"] = normalized_evidence[:10]

            return obj
        except Exception as e:
            self._handle_exception(e, f"目录分析({dir_path}#{chunk_index}/{chunk_total})")
            return None

    def generate_bootstrap_doc_plan(
        self,
        *,
        repo_map: Dict[str, Any],
        dir_briefs: List[Dict[str, Any]],
        max_pages: int,
    ) -> List[Dict[str, Any]]:
        """Stage 3a: generate a doc plan from directory briefs."""
        max_tokens = self._get_max_tokens("LLM_DOC_PLAN_MAX_TOKENS", 8192)
        repo_map_text = json.dumps(repo_map or {}, ensure_ascii=False)
        dir_briefs_text = json.dumps(dir_briefs or [], ensure_ascii=False)

        system_instruction = "你是一个只输出 JSON 的文档助手。禁止编造，不得输出非 JSON 内容。"
        prompt = f"""
你是一个技术文档信息架构师。请基于 RepoMap 与逐目录摘要，为 `{config.REPO_NAME}`@`{config.UPSTREAM_BRANCH}` 生成“初始文档规划”（模块化分组，多入口）。

要求：
- 允许新增/重排分组目录：target_category 是 docs_root 下的相对路径，可多级（如 plugin_system/api）。
- 每一篇文档必须能追溯来源：evidence 至少 2 条，必须出现在 dir_briefs 或 repo_map 中的原样子串（建议用路径/符号名）。
- 文档数量上限：最多 {int(max_pages)} 篇（超过则优先保留“对外契约/API/插件开发”相关文档）。

输出必须是 JSON 数组，每一项仅包含这些 key（不得多、不得少）：
- target_category: string
- file_name: string (.md, 纯文件名，无路径)
- title: string
- source_dirs: array[string] (从 dir_briefs 中选择)
- reason: string
- evidence: array[string]

--- RepoMap ---
{repo_map_text}

--- dir_briefs ---
{dir_briefs_text}
        """
        try:
            raw = self._call_llm(
                prompt,
                system_instruction=system_instruction,
                temperature=self._get_temperature(),
                max_tokens=max_tokens,
                response_schema=self._schema_bootstrap_doc_plan(),
                response_schema_name="doc_plan",
            )
            data = self._extract_json(raw)
            items = data if isinstance(data, list) else [data]
            plan: List[Dict[str, Any]] = []
            dir_set = {str(d.get("dir")).strip() for d in (dir_briefs or []) if isinstance(d, dict) and d.get("dir")}
            haystack = f"{repo_map_text}\n{dir_briefs_text}"
            required_item_keys = ["target_category", "file_name", "title", "source_dirs", "reason", "evidence"]

            for item in items:
                if not isinstance(item, dict):
                    continue
                item = self._coerce_object_keys(
                    item,
                    required_item_keys,
                    defaults={
                        "target_category": "",
                        "file_name": "",
                        "title": "",
                        "source_dirs": [],
                        "reason": "",
                        "evidence": [],
                    },
                )

                target_category = self._normalize_category_path(item.get("target_category") or "")
                file_name = (item.get("file_name") or "").strip()
                if not self._is_safe_category_path(target_category):
                    continue
                if not file_name.endswith(".md") or any(x in file_name for x in ["/", "\\", ".."]):
                    continue

                source_dirs = item.get("source_dirs")
                if not isinstance(source_dirs, list) or not source_dirs:
                    continue
                if not all(isinstance(d, str) and d.strip() for d in source_dirs):
                    continue
                if any(d.strip() not in dir_set for d in source_dirs):
                    continue

                evidence = item.get("evidence")
                if not isinstance(evidence, list):
                    evidence = []
                normalized_evidence: List[str] = []
                for ev in evidence:
                    if not isinstance(ev, str):
                        continue
                    token = ev.strip().strip("`")
                    if token:
                        normalized_evidence.append(token)
                normalized_evidence = sorted(set(normalized_evidence))

                matched = 0
                for ev in normalized_evidence:
                    if ev in haystack:
                        matched += 1
                if matched < 2:
                    # Auto-fill evidence with safe tokens that are guaranteed to exist in haystack.
                    fallback: List[str] = []
                    if source_dirs:
                        fallback.append(source_dirs[0].strip())
                    if source_dirs and source_dirs[-1].strip() != (source_dirs[0].strip() if source_dirs else ""):
                        fallback.append(source_dirs[-1].strip())
                    if repo_map.get("repo"):
                        fallback.append(str(repo_map.get("repo")).strip())
                    fallback = [x for x in fallback if x and x in haystack]
                    normalized_evidence = fallback[:2]
                if len(normalized_evidence) < 2:
                    continue

                plan.append(
                    {
                        "target_category": target_category,
                        "file_name": file_name,
                        "title": (item.get("title") or "").strip(),
                        "source_dirs": [d.strip() for d in source_dirs],
                        "reason": (item.get("reason") or "").strip(),
                        "evidence": normalized_evidence,
                    }
                )

                if len(plan) >= int(max_pages):
                    break

            return plan
        except Exception as e:
            self._handle_exception(e, "文档规划生成")
            return []

    def generate_bootstrap_doc_page(
        self,
        *,
        repo_map: Dict[str, Any],
        dir_summaries: List[Dict[str, Any]],
        spec: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """Stage 3b: generate one markdown page from a plan spec."""
        max_tokens = self._get_max_tokens("LLM_DOC_PAGE_MAX_TOKENS", 8192)
        today = datetime.now().strftime("%Y-%m-%d")

        target_category = self._normalize_category_path(spec.get("target_category") or "")
        file_name = (spec.get("file_name") or "").strip()
        source_dirs = [d.strip() for d in (spec.get("source_dirs") or []) if isinstance(d, str) and d.strip()]
        if not source_dirs:
            return None

        repo_map_text = json.dumps(repo_map or {}, ensure_ascii=False)

        selected = [
            s
            for s in (dir_summaries or [])
            if isinstance(s, dict) and str(s.get("dir") or "").strip() in set(source_dirs)
        ]
        selected_text = json.dumps(selected, ensure_ascii=False)
        evidence_haystack = f"{repo_map_text}\n{selected_text}"

        system_instruction = "你是一个只输出 JSON 的文档助手。禁止编造，不得输出非 JSON 内容。"
        prompt = f"""
你是一个高级软件工程师和技术文档专家。请根据 RepoMap + 目录分析结果，为当前 spec 生成一篇可发布的 Markdown 文档。

约束：
- 禁止编造：只能引用下面上下文中出现的路径/符号/字段。
- 必须包含 YAML frontmatter，且必须包含 last_updated: {today}
- 必须包含章节：## 概述 / ## 目录/结构 / ## 适用范围 / ## 变更影响分析 / ## 证据
- “证据”章节中需要列出 evidence（至少 2 条，原样字符串）

输出必须是 JSON 对象，且 key 必须严格等于下面列表（不得多、不得少）：
- target_category
- file_name
- content
- evidence
- reason

--- spec ---
{json.dumps(spec, ensure_ascii=False)}

--- RepoMap ---
{repo_map_text}

--- Directory analyses (selected) ---
{selected_text}
        """
        try:
            raw = self._call_llm(
                prompt,
                system_instruction=system_instruction,
                temperature=self._get_temperature(),
                max_tokens=max_tokens,
                response_schema=self._schema_doc_page(),
                response_schema_name="doc_page",
            )
            obj = self._extract_json(raw)
            if not isinstance(obj, dict):
                raise ValueError("doc page must be a JSON object")
            obj = self._coerce_object_keys(
                obj,
                ["target_category", "file_name", "content", "evidence", "reason"],
                defaults={
                    "target_category": target_category,
                    "file_name": file_name,
                    "content": "",
                    "evidence": [],
                    "reason": "",
                },
            )

            out_category = self._normalize_category_path(obj.get("target_category") or target_category)
            out_file_name = (obj.get("file_name") or file_name).strip()
            content = obj.get("content") or ""
            evidence = obj.get("evidence")

            if not self._is_safe_category_path(out_category):
                raise ValueError("unsafe target_category")
            if not out_file_name.endswith(".md") or any(x in out_file_name for x in ["/", "\\", ".."]):
                raise ValueError("invalid file_name")
            if not isinstance(content, str) or not content.strip():
                raise ValueError("content must be non-empty")
            if not content.lstrip().startswith("---"):
                raise ValueError("content must start with frontmatter")
            for sec in ("## 概述", "## 目录/结构", "## 适用范围", "## 变更影响分析", "## 证据"):
                if sec not in content:
                    raise ValueError(f"missing section: {sec}")

            if not isinstance(evidence, list):
                evidence = []
            normalized_evidence: List[str] = []
            for ev in evidence:
                if not isinstance(ev, str):
                    continue
                token = ev.strip().strip("`")
                if token:
                    normalized_evidence.append(token)
            normalized_evidence = sorted(set(normalized_evidence))

            matched = 0
            for ev in normalized_evidence:
                if ev in evidence_haystack:
                    matched += 1
            if matched < 2:
                fallback: List[str] = []
                if source_dirs:
                    fallback.append(source_dirs[0])
                if source_dirs and source_dirs[-1] != source_dirs[0]:
                    fallback.append(source_dirs[-1])
                if repo_map.get("repo"):
                    fallback.append(str(repo_map.get("repo")).strip())
                fallback = [x for x in fallback if x and x in evidence_haystack]
                normalized_evidence = fallback[:2]
            if len(normalized_evidence) < 2:
                raise ValueError("evidence must include >= 2 substrings present in provided context")

            return {
                "target_category": out_category,
                "file_name": out_file_name,
                "content": content,
                "evidence": normalized_evidence,
                "reason": (obj.get("reason") or "").strip(),
            }
        except Exception as e:
            self._handle_exception(e, f"文档生成({target_category}/{file_name})")
            return None

    def generate_plugin_api_doc_page(
        self,
        *,
        repo_map: Dict[str, Any],
        module_path: str,
        module_text: str,
        target_category: str,
        file_name: str,
    ) -> Optional[Dict[str, Any]]:
        """Stage 4: generate one plugin API page from a single source module."""
        max_tokens = self._get_max_tokens("LLM_API_PAGE_MAX_TOKENS", 8192)
        today = datetime.now().strftime("%Y-%m-%d")
        repo_map_text = json.dumps(repo_map or {}, ensure_ascii=False)

        system_instruction = "你是一个只输出 JSON 的文档助手。禁止编造，不得输出非 JSON 内容。"
        prompt = f"""
你是一个插件开发文档维护助手。请基于 RepoMap + 单文件源码，为插件系统 API 生成一篇 Markdown 文档。

约束：
- 禁止编造：只允许描述源码中可直接佐证的符号、签名与行为。
- 必须包含 YAML frontmatter，且必须包含 last_updated: {today}
- 必须包含章节：## 概述 / ## API 列表 / ## 调用约定 / ## 变更影响分析 / ## 证据
- evidence 至少 2 条，且必须出现在源码片段中（建议用 `{module_path}` 或函数/类名）

输出必须是 JSON 对象，且 key 必须严格等于下面列表（不得多、不得少）：
- target_category
- file_name
- content
- evidence
- reason

目标输出路径（固定）：
- target_category: {target_category}
- file_name: {file_name}

--- RepoMap ---
{repo_map_text}

--- Source: {module_path} ---
```python
{module_text}
```
        """
        try:
            raw = self._call_llm(
                prompt,
                system_instruction=system_instruction,
                temperature=self._get_temperature(),
                max_tokens=max_tokens,
                response_schema=self._schema_doc_page(),
                response_schema_name="api_page",
            )
            obj = self._extract_json(raw)
            if not isinstance(obj, dict):
                raise ValueError("api page must be a JSON object")
            obj = self._coerce_object_keys(
                obj,
                ["target_category", "file_name", "content", "evidence", "reason"],
                defaults={
                    "target_category": target_category,
                    "file_name": file_name,
                    "content": "",
                    "evidence": [],
                    "reason": "",
                },
            )

            out_category = self._normalize_category_path(obj.get("target_category") or target_category)
            out_file_name = (obj.get("file_name") or file_name).strip()
            content = obj.get("content") or ""
            evidence = obj.get("evidence") or []

            if out_category != self._normalize_category_path(target_category):
                raise ValueError("api page target_category mismatch")
            if out_file_name != file_name:
                raise ValueError("api page file_name mismatch")
            if not self._is_safe_category_path(out_category):
                raise ValueError("unsafe target_category")
            if not isinstance(content, str) or not content.strip() or not content.lstrip().startswith("---"):
                raise ValueError("invalid content")
            for sec in ("## 概述", "## API 列表", "## 调用约定", "## 变更影响分析", "## 证据"):
                if sec not in content:
                    raise ValueError(f"missing section: {sec}")

            if not isinstance(evidence, list):
                evidence = []
            normalized_evidence: List[str] = []
            for ev in evidence:
                if not isinstance(ev, str):
                    continue
                token = ev.strip().strip("`")
                if token:
                    normalized_evidence.append(token)
            normalized_evidence = sorted(set(normalized_evidence))

            haystack = f"{module_path}\n{module_text}"
            matched = 0
            for ev in normalized_evidence:
                if ev in haystack:
                    matched += 1
            if matched < 2:
                sig = ""
                for line in (module_text or "").splitlines():
                    if line.startswith(("def ", "async def ", "class ")):
                        sig = line.strip()
                        break
                fallback = [module_path]
                if sig:
                    fallback.append(sig)
                fallback = [x for x in fallback if x and x in haystack]
                normalized_evidence = fallback[:2]
            if len(normalized_evidence) < 2:
                raise ValueError("evidence must include >= 2 substrings present in source module")

            return {
                "target_category": out_category,
                "file_name": out_file_name,
                "content": content,
                "evidence": normalized_evidence,
                "reason": (obj.get("reason") or "").strip(),
            }
        except Exception as e:
            self._handle_exception(e, f"API 文档生成({module_path})")
            return None
