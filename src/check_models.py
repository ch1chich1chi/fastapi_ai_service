from errors import ValidationError
from models import Conversation, Message


def run_valid_test() -> None:
    conversation = Conversation("Python 学习")

    user_message = Message("user", "什么是类？")
    assistant_message = Message("assistant", "类是创建对象的模板。")

    conversation.add_message(user_message)
    conversation.add_message(assistant_message)

    print("测试一：正常对话")
    print("对话标题：", conversation.title)

    for message in conversation.messages:
        print(message.role, "->", message.content)


def run_invalid_test() -> None:
    print("测试二：错误角色")

    try:
        Message("student", "这条消息能够创建吗？")
    except ValidationError as error:
        print("成功拦截错误：", error)


if __name__ == "__main__":
    run_valid_test()
    run_invalid_test()