from config import config
from llm_client import (
    HttpError,
    build_gemini_generate_content_url,
    build_openai_chat_completions_url,
    detect_api_style,
    generate_text,
)


def mask_sensitive(text: str, key: str) -> str:
    if not key:
        return text
    return (text or "").replace(key, "***")


def test_api() -> None:
    print("=== LLM API Connectivity Test (curl) ===")

    api_key = config.GEMINI_API_KEY
    base_url = config.BASE_URL.rstrip("/")
    api_version = config.GEMINI_API_VERSION
    model_name = config.MODEL_NAME
    api_style = config.LLM_API_STYLE
    show_base_url_in_logs = config.SHOW_BASE_URL_IN_LOGS

    if not api_key:
        print("Error: GEMINI_API_KEY is not set.")
        return

    style = detect_api_style(base_url, api_style)
    if style == "openai":
        url = build_openai_chat_completions_url(base_url)
    else:
        url = build_gemini_generate_content_url(base_url, api_version, model_name)

    print("Request Detail (masked):")
    print(f"  - LLM_API_STYLE: {api_style}")
    print(f"  - Detected style: {style}")
    if show_base_url_in_logs:
        print(f"  - Base URL: {mask_sensitive(base_url, api_key)}")
        print(f"  - Target URL: {mask_sensitive(url, api_key)}")
    else:
        print("  - Base URL: (hidden)")
        print("  - Target URL: (hidden)")
    print(f"  - API Version: {api_version}")
    print(f"  - Model: {model_name}")

    print("\n[Sending Request via curl...]")
    try:
        text = generate_text(
            api_key=api_key,
            base_url=base_url,
            model_name=model_name,
            prompt="Hello, this is a connectivity test. Please reply with 'OK'.",
            temperature=0.1,
            max_tokens=16,
            api_version=api_version,
            api_style=api_style,
            timeout_seconds=60,
        )
        print("\n[Response Text]")
        print(mask_sensitive(text, api_key))
        print("\nConnectivity test PASSED!")
    except HttpError as e:
        print(f"\nConnectivity test FAILED: HTTP {e.status_code}")
        print(mask_sensitive(e.body, api_key)[:800])
    except Exception as e:
        print(f"\nRequest Exception: {mask_sensitive(str(e), api_key)}")


if __name__ == "__main__":
    test_api()

