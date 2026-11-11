from src.clients.base import LLMClient


class ChatService:
    def __init__(self, client: LLMClient) -> None:
        self.client = client

    def reply(self, question: str) -> str:
        answer = self.client.generate(question)
        return answer
