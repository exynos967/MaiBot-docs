import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    # GitHub
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "").strip()
    REPO_NAME = os.getenv("UPSTREAM_REPO", "Mai-with-u/MaiBot").strip()
    UPSTREAM_BRANCH = os.getenv("UPSTREAM_BRANCH", "main").strip()

    # LLM (Gemini or OpenAI-compatible)
    GEMINI_API_KEY = (os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY") or "").strip()
    BASE_URL = (
        os.getenv("BASE_URL")
        or os.getenv("OPENAI_API_BASE")
        or "https://generativelanguage.googleapis.com"
    ).strip()
    GEMINI_API_VERSION = os.getenv("GEMINI_API_VERSION", "v1beta").strip()
    MODEL_NAME = (os.getenv("MODEL_NAME") or "gemini-1.5-flash").strip()
    LLM_API_STYLE = os.getenv("LLM_API_STYLE", "auto").strip()
    SHOW_BASE_URL_IN_LOGS = os.getenv("SHOW_BASE_URL_IN_LOGS", "0").strip() == "1"

    # Sync behavior
    STATE_FILE = os.getenv("STATE_FILE", "scripts/state.json").strip()
    DOCS_ROOT = os.getenv("DOCS_ROOT", "develop/llm/maibot/main").strip()
    ENABLE_SNAPSHOTS = os.getenv("ENABLE_SNAPSHOTS", "0").strip() == "1"
    SYNC_LOOKBACK_HOURS = int(os.getenv("SYNC_LOOKBACK_HOURS", "6") or "6")


config = Config()
