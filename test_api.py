"""Make a small, secret-safe connectivity test against a DeepSeek-compatible API."""

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from openai import APIStatusError, OpenAI


def first_configured(*names: str) -> str | None:
    for name in names:
        value = os.getenv(name)
        if value and value.strip():
            return value.strip()
    return None


def main() -> int:
    load_dotenv(Path(__file__).with_name(".env"))

    api_key = first_configured("DEEPSEEK_API_KEY", "OPENAI_API_KEY", "API_KEY")
    base_url = first_configured("DEEPSEEK_BASE_URL", "BASE_URL")
    model = first_configured("DEEPSEEK_MODEL", "MODEL")

    missing = [
        name
        for name, value in (
            ("API key", api_key),
            ("BASE_URL", base_url),
            ("MODEL", model),
        )
        if value is None
    ]
    if missing:
        print("Configuration missing: " + ", ".join(missing))
        print("Check the variable names in your .env; values are not displayed.")
        return 2

    try:
        client = OpenAI(api_key=api_key, base_url=base_url, max_retries=0)
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "你好，请用一句话介绍自己"}],
        )
        answer = response.choices[0].message.content
        if not answer:
            print("The API returned an empty response.")
            return 1
        print("API connection succeeded. Response:")
        print(answer.replace(api_key, "[REDACTED]"))
        return 0
    except APIStatusError as exc:
        status_code = exc.status_code
        print(f"API request failed with HTTP {status_code}; response details are suppressed.")
        if status_code == 401:
            print("The service rejected authentication; verify the API key and account status.")
        elif status_code == 402:
            print("The service reports a billing or quota issue; check the account balance/quota.")
        elif status_code == 404:
            print("The endpoint or model was not found; verify BASE_URL and MODEL.")
        elif status_code == 429:
            print("The service rate-limited the request or quota is exhausted; retry later/check quota.")
        else:
            print("Check BASE_URL, MODEL, provider status, and account configuration.")
        return 1
    except Exception as exc:
        # Do not print exception details: an upstream error could include credentials.
        print(f"API request failed ({type(exc).__name__}); details are suppressed to protect secrets.")
        print("Check network access, BASE_URL, MODEL, and that the API key is valid.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
