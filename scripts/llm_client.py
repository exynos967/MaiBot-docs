import json
import re
import subprocess
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple
from urllib.parse import urlparse


@dataclass
class HttpError(RuntimeError):
    status_code: int
    body: str

    def __str__(self) -> str:  # pragma: no cover
        preview = (self.body or "").strip()
        if len(preview) > 500:
            preview = preview[:500] + "..."
        return f"HTTP {self.status_code}: {preview}"


def _normalize_base_url(base_url: str) -> str:
    return (base_url or "").strip().rstrip("/")


def _join_url(base_url: str, path: str) -> str:
    return f"{base_url.rstrip('/')}/{path.lstrip('/')}"


def detect_api_style(base_url: str, explicit: str = "auto") -> str:
    explicit = (explicit or "auto").strip().lower()
    if explicit in {"openai", "gemini"}:
        return explicit
    if explicit != "auto":
        raise ValueError("LLM_API_STYLE must be one of: auto/openai/gemini")

    parsed = urlparse(_normalize_base_url(base_url))
    host = (parsed.netloc or "").lower()
    if "generativelanguage.googleapis.com" in host or host.endswith(".googleapis.com"):
        return "gemini"
    return "openai"


def _curl_post_json(
    *,
    url: str,
    headers: Dict[str, str],
    payload: Dict[str, Any],
    timeout_seconds: int = 60,
) -> Tuple[int, Dict[str, Any]]:
    marker = "__CURL_HTTP_STATUS__:"
    cmd = [
        "curl",
        "-sS",
        "-X",
        "POST",
        url,
        "--max-time",
        str(int(timeout_seconds)),
        "-H",
        "Accept: application/json",
        "-H",
        "Content-Type: application/json",
        "--data-binary",
        "@-",
        "-w",
        f"\n{marker}%{{http_code}}",
    ]

    for header_name, header_value in headers.items():
        if header_value:
            cmd.extend(["-H", f"{header_name}: {header_value}"])

    result = subprocess.run(
        cmd,
        input=json.dumps(payload, ensure_ascii=False),
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
    )

    stdout = result.stdout or ""
    if marker not in stdout:
        raise RuntimeError(
            f"curl did not return an HTTP status marker (rc={result.returncode}): {(result.stderr or '').strip()}"
        )

    body_text, status_text = stdout.rsplit(marker, 1)
    body_text = body_text.strip()
    status_code = int(status_text.strip() or "0")

    if status_code < 200 or status_code >= 300:
        raise HttpError(status_code=status_code, body=body_text)

    try:
        return status_code, json.loads(body_text) if body_text else {}
    except json.JSONDecodeError:
        raise RuntimeError(f"Non-JSON response (HTTP {status_code}): {body_text[:500]}")


def build_openai_chat_completions_url(base_url: str) -> str:
    base_url = _normalize_base_url(base_url)
    parsed = urlparse(base_url)
    if re.search(r"/v1/?$", parsed.path or ""):
        v1_base = base_url
    else:
        v1_base = _join_url(base_url, "v1")
    return _join_url(v1_base, "chat/completions")


def build_gemini_generate_content_url(base_url: str, api_version: str, model_name: str) -> str:
    base_url = _normalize_base_url(base_url)
    api_version = (api_version or "v1beta").strip().strip("/")

    if re.search(r"/v1(beta)?/?$", urlparse(base_url).path or ""):
        url_prefix = base_url
    else:
        url_prefix = _join_url(base_url, api_version)

    return _join_url(url_prefix, f"models/{model_name}:generateContent")


def generate_text(
    *,
    api_key: str,
    base_url: str,
    model_name: str,
    prompt: str,
    system_instruction: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 2048,
    response_format: Optional[Dict[str, Any]] = None,
    api_version: str = "v1beta",
    api_style: str = "auto",
    timeout_seconds: int = 60,
) -> str:
    style = detect_api_style(base_url, api_style)

    if style == "openai":
        url = build_openai_chat_completions_url(base_url)
        messages = []
        if system_instruction:
            messages.append({"role": "system", "content": system_instruction})
        messages.append({"role": "user", "content": prompt})
        payload = {
            "model": model_name,
            "messages": messages,
            "temperature": float(temperature),
            "max_tokens": int(max_tokens),
        }
        if response_format is not None:
            payload["response_format"] = response_format

        def _looks_like_response_format_error(body_text: str) -> bool:
            t = (body_text or "").lower()
            needles = [
                "response_format",
                "json_schema",
                "json_object",
                "unknown parameter",
                "unrecognized",
                "unsupported",
                "not supported",
                "invalid",
            ]
            return any(n in t for n in needles)

        def _schema_root_type(fmt: Dict[str, Any]) -> str:
            try:
                if (fmt or {}).get("type") != "json_schema":
                    return ""
                js = (fmt or {}).get("json_schema") or {}
                schema = js.get("schema") or {}
                return str(schema.get("type") or "").strip().lower()
            except Exception:
                return ""

        def _post(p: Dict[str, Any]) -> Dict[str, Any]:
            _, data = _curl_post_json(
                url=url,
                headers={"Authorization": f"Bearer {api_key}"},
                payload=p,
                timeout_seconds=timeout_seconds,
            )
            return data or {}

        try:
            data = _post(payload)
        except HttpError as e:
            # Some OpenAI-compatible endpoints (or older models) don't support response_format/json_schema.
            if response_format is None or e.status_code not in {400, 422} or not _looks_like_response_format_error(e.body):
                raise

            fallback_payload = dict(payload)
            fmt = response_format or {}
            if fmt.get("type") == "json_schema" and _schema_root_type(fmt) == "object":
                # Try JSON mode as a best-effort fallback for object responses.
                fallback_payload["response_format"] = {"type": "json_object"}
            else:
                # Arrays can't use json_object; fall back to prompt-only JSON.
                fallback_payload.pop("response_format", None)

            try:
                data = _post(fallback_payload)
            except HttpError as e2:
                if (
                    "response_format" in (e2.body or "").lower()
                    and fallback_payload.get("response_format") is not None
                    and e2.status_code in {400, 422}
                ):
                    fallback_payload.pop("response_format", None)
                    data = _post(fallback_payload)
                else:
                    raise
        try:
            return (data["choices"][0]["message"]["content"] or "").strip()
        except Exception:
            raise RuntimeError(f"Unexpected OpenAI response shape: {json.dumps(data, ensure_ascii=False)[:500]}")

    url = build_gemini_generate_content_url(base_url, api_version, model_name)
    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [{"text": prompt}],
            }
        ],
        "generationConfig": {
            "temperature": float(temperature),
            "maxOutputTokens": int(max_tokens),
        },
    }
    if system_instruction:
        payload["systemInstruction"] = {"parts": [{"text": system_instruction}]}

    _, data = _curl_post_json(
        url=url,
        headers={"x-goog-api-key": api_key},
        payload=payload,
        timeout_seconds=timeout_seconds,
    )
    try:
        candidates = data.get("candidates") or []
        if not candidates:
            raise RuntimeError(f"Gemini returned no candidates: {json.dumps(data, ensure_ascii=False)[:500]}")
        parts = ((candidates[0].get("content") or {}).get("parts") or [])
        return "".join((part.get("text") or "") for part in parts).strip()
    except Exception:
        raise RuntimeError(f"Unexpected Gemini response shape: {json.dumps(data, ensure_ascii=False)[:500]}")
