import os

import requests


class DeepSeekClient:
    API_URL = "https://api.deepseek.com/chat/completions"

    def __init__(
        self,
        api_key: str | None = None,
        model: str = "deepseek-flash",
        timeout: int = 30,
    ) -> None:
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError("缺少环境变量 DEEPSEEK_API_KEY")

        self.model = model
        self.timeout = timeout

    def generate(self, prompt: str) -> str:
        response = requests.post(
            self.API_URL,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "thinking": {"type": "disabled"},
            },
            timeout=self.timeout,
        )
        response.raise_for_status()

        data = response.json()
        return data["choices"][0]["message"]["content"]
