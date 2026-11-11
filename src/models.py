from errors import ValidationError


class Message:
    def __init__(self, role: str, content: str) -> None:
        if role not in ("system", "user", "assistant"):
            raise ValidationError(
                "role 必须是 system、user 或 assistant"
            )

        if not content.strip():
            raise ValidationError("content 不能为空")

        self.role = role
        self.content = content

class Conversation:
    def __init__(self, title: str) -> None:
        if not title.strip():
            raise ValidationError("title 不能为空")

        self.title = title
        self.messages: list[Message] = []

    def add_message(self, message: Message) -> None:
        self.messages.append(message)