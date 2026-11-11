# FastAPI 项目分层与依赖注入

日期：2026-10-09

## 1. 为什么拆分代码

项目较小时，可以把接口和处理逻辑都写在 `main.py` 中。

以后加入模型 API、环境变量、超时、日志、异常和数据库后，全部写在一个文件中会很难阅读和修改。

因此把聊天功能拆为 `Router -> Service -> Client` 三层。

## 2. 三层职责

### Router

文件：`src/routers/chat.py`

负责：

- 定义 `POST /chat`。
- 接收 `ChatRequest`。
- 取出 `request.question`。
- 调用 `ChatService`。
- 返回 `ChatResponse`。

Router 只处理 HTTP 接口数据，不负责直接生成模型回答。

### Service

文件：`src/services/chat_service.py`

负责：

- 处理聊天业务流程。
- 接收用户问题。
- 调用 Client 获取回答。
- 把回答返回给 Router。

Service 不关心 `/chat`、JSON 或 HTTP 状态码。

### Client

文件：`src/clients/fake_llm.py`

负责：

- 与外部模型服务交互。
- 接收 prompt。
- 返回模型生成的字符串。

当前的 `FakeLLMClient` 不联网，只返回模拟回答。后面再替换为真实模型 Client。

## 3. 当前目录结构

```text
src/
├── main.py
├── schemas.py
├── clients/
│   ├── __init__.py
│   └── fake_llm.py
├── services/
│   ├── __init__.py
│   └── chat_service.py
└── routers/
    ├── __init__.py
    └── chat.py
```

`__init__.py` 表示该目录可作为 Python 包使用。

## 4. Client 层

```python
class FakeLLMClient:
    def generate(self, prompt: str) -> str:
        return f"收到你的问题：{prompt}"
```

`generate()` 表示生成回答。

```python
client.generate(question)
```

表示调用 `client` 对象中的 `generate()` 方法，并把 `question` 传给参数 `prompt`。

## 5. Service 层

```python
from src.clients.fake_llm import FakeLLMClient


class ChatService:
    def __init__(self, client: FakeLLMClient) -> None:
        self.client = client

    def reply(self, question: str) -> str:
        answer = self.client.generate(question)
        return answer
```

`ChatService` 不自己创建 Client，而是通过构造函数接收 Client。

## 6. 依赖注入

依赖是一个对象完成工作时需要的另一个对象。

`ChatService` 需要 Client 才能获取回答，所以 Client 是 `ChatService` 的依赖。

不使用依赖注入：

```python
class ChatService:
    def __init__(self) -> None:
        self.client = FakeLLMClient()
```

`ChatService` 自己创建 Client，两者绑在一起。

使用依赖注入：

```python
client = FakeLLMClient()
service = ChatService(client)
```

Client 在外部创建，然后传给 `ChatService`。后面替换真实 Client 时，`ChatService` 和路由处理函数的主要逻辑无需重写。

## 7. Router 层

```python
router = APIRouter()

client = FakeLLMClient()
service = ChatService(client)


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    answer = service.reply(request.question)
    return ChatResponse(answer=answer)
```

`APIRouter` 可以理解为专门管理一类接口的小型 FastAPI。

Router 从 `request.question` 取出问题，交给 `service.reply()`，再把回答包装成 `ChatResponse`。

## 8. 完整调用链

```text
客户端发送 POST /chat
          ↓
Router 接收 ChatRequest
          ↓
Router 调用 service.reply(question)
          ↓
ChatService 调用 client.generate(question)
          ↓
FakeLLMClient 返回模拟回答
          ↓
ChatService 把回答返回 Router
          ↓
Router 创建 ChatResponse
          ↓
FastAPI 返回 JSON
```

## 9. main.py 的职责

`main.py` 只保留应用入口和全局接口，然后挂载 Router：

```python
from src.routers.chat import router as chat_router

app.include_router(chat_router)
```

这样 `main.py` 不需要包含聊天功能的具体处理逻辑。
