import json
from typing import Any, Dict, List

import requests


QWEN_API_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
DEFAULT_MODEL = "qwen-turbo"


def load_api_key() -> str:
    """Load API key from qwen_key.txt."""
    try:
        with open("qwen_key.txt", "r", encoding="utf-8") as f:
            api_key = f.read().strip()
    except FileNotFoundError:
        raise ValueError("qwen_key.txt not found. Please create it in the project root.")

    if not api_key:
        raise ValueError("qwen_key.txt is empty.")

    if not api_key.startswith("sk-"):
        raise ValueError("Invalid API key. It must start with sk-.")

    if any(c.isspace() for c in api_key):
        raise ValueError("Invalid API key. Remove spaces or line breaks in qwen_key.txt.")

    return api_key


def call_qwen(
    messages: List[Dict[str, str]],
    model: str = DEFAULT_MODEL,
    max_tokens: int = 4000,
    temperature: float = 0.2,
    stage: str = "qwen_api",
) -> Dict[str, Any]:
    """Call Alibaba Cloud Bailian Qwen API with OpenAI-compatible endpoint.

    The function records real Qwen attempts into src.qwen_usage when that module
    is available. It never stores prompt contents or API keys in the log.
    """
    api_key = load_api_key()

    try:
        max_tokens = int(max_tokens)
    except Exception:
        max_tokens = 4000

    max_tokens = max(1, min(max_tokens, 8000))

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    session = requests.Session()
    session.trust_env = False

    def _log(success: bool, purpose: str = "qwen_api_call") -> None:
        try:
            from src.qwen_usage import log_call
            log_call(
                stage=stage,
                model_name=model,
                input_type="messages_without_content",
                output_type="chat_completion" if success else "error",
                purpose=purpose,
                success=success,
            )
        except Exception:
            pass

    try:
        response = session.post(
            QWEN_API_URL,
            headers=headers,
            json=payload,
            timeout=120,
        )
        if response.status_code != 200:
            _log(False, f"http_{response.status_code}")
            raise RuntimeError(
                f"Qwen API error: HTTP {response.status_code}\n{response.text[:1000]}"
            )
        _log(True)
        return response.json()
    except Exception:
        _log(False, "request_exception")
        raise


def extract_qwen_text(result: Dict[str, Any]) -> str:
    """Extract text from Qwen OpenAI-compatible response."""
    try:
        return result["choices"][0]["message"]["content"]
    except Exception:
        return json.dumps(result, ensure_ascii=False, indent=2)


def call_qwen_text(
    prompt: str,
    model: str = DEFAULT_MODEL,
    max_tokens: int = 4000,
    temperature: float = 0.2,
    stage: str = "qwen_api",
) -> str:
    """Call Qwen with a prompt and return text."""
    messages = [{"role": "user", "content": prompt}]
    result = call_qwen(
        messages=messages,
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
        stage=stage,
    )
    return extract_qwen_text(result)


def test_api_connection() -> bool:
    """Test Qwen API connection."""
    try:
        result = call_qwen(
            messages=[{"role": "user", "content": "Hello. Reply OK only."}],
            model=DEFAULT_MODEL,
            max_tokens=20,
            temperature=0.1,
        )
        text = extract_qwen_text(result)
        print("Qwen API test success:", text)
        return True
    except Exception as e:
        print("Qwen API test failed:", str(e))
        return False


if __name__ == "__main__":
    print("API status:", test_api_connection())