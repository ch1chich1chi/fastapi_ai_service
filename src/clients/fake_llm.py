class FakeLLMClient:
    def generate(self, prompt: str) -> str:
        return f"收到你的问题：{prompt}"