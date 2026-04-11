import os
import sys
import requests
from openai import OpenAI


NIM_BASE_URL = "https://integrate.api.nvidia.com/v1"
GPT_OSS_MODEL = "openai/gpt-oss-120b"
GEMMA_MODEL = "google/gemma-4-31b-it"


def _get_key(name: str) -> str | None:
    value = os.getenv(name)
    if value:
        return value
    return None


def check_gpt_oss() -> None:
    api_key = _get_key("GOVBREIFER_NIM_API_KEY_FINAL") or _get_key("NVIDIA_NIM_API_KEY")
    if not api_key:
        print("GPT-OSS check skipped: missing GOVBREIFER_NIM_API_KEY_FINAL/NVIDIA_NIM_API_KEY")
        return

    client = OpenAI(base_url=NIM_BASE_URL, api_key=api_key)
    response = client.chat.completions.create(
        model=GPT_OSS_MODEL,
        messages=[{"role": "user", "content": "Reply with OK"}],
        temperature=0,
        max_tokens=5,
    )
    print("GPT-OSS OK:", response.choices[0].message.content)


def check_gemma() -> None:
    api_key = _get_key("GOVBREIFER_NIM_API_KEY_FAST")
    if not api_key:
        print("Gemma check skipped: missing GOVBREIFER_NIM_API_KEY_FAST")
        return

    headers = {"Authorization": f"Bearer {api_key}"}
    payload = {
        "model": GEMMA_MODEL,
        "messages": [{"role": "user", "content": "Reply with OK"}],
        "temperature": 0,
        "max_tokens": 5,
        "stream": False,
    }
    response = requests.post(
        f"{NIM_BASE_URL}/chat/completions",
        headers=headers,
        json=payload,
        timeout=30,
    )
    if response.status_code != 200:
        print("Gemma check failed:", response.status_code, response.text)
        return
    data = response.json()
    print("Gemma OK:", data["choices"][0]["message"]["content"])


if __name__ == "__main__":
    try:
        check_gpt_oss()
        check_gemma()
    except Exception as exc:
        print("NIM key check failed:", exc)
        sys.exit(1)
