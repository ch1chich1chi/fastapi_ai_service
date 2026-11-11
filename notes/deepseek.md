# DeepSeek Client 笔记

## 1. 安全读取 API Key

```python
import os

api_key = os.getenv("DEEPSEEK_API_KEY")
if not api_key:
    raise ValueError("缺少环境变量 DEEPSEEK_API_KEY")
```

密钥放在操作系统环境变量或被 Git 忽略的 `.env` 中，不写死在 Python 代码里。

## 2. 发送模型请求

```python
response = requests.post(
    "https://api.deepseek.com/chat/completions",
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
```

- `headers` 负责身份验证和数据格式。
- `json` 是发给模型的请求体。
- `timeout` 防止程序无限等待。
- `raise_for_status()` 在 4xx/5xx 时抛出异常，避免把错误响应当成正常数据。

## 3. 读取模型回答

```python
data = response.json()
answer = data["choices"][0]["message"]["content"]
```

DeepSeek 返回 JSON。此路径依次取出第一个候选结果、消息和文本内容。

## 4. Protocol 与依赖注入

```python
class LLMClient(Protocol):
    def generate(self, prompt: str) -> str:
        ...
```

`ChatService` 只要求 Client 提供 `generate()`，不关心它是 `FakeLLMClient` 还是 `DeepSeekClient`。这样替换模型时，Service 和 Router 的业务流程不用重写。

## 5. 完整调用链

```text
POST /chat
    -> ChatRequest 校验
    -> ChatService.reply()
    -> DeepSeekClient.generate()
    -> DeepSeek API
    -> ChatResponse
```

## 6. 验证结果

- Client 单独请求 DeepSeek：成功返回 `OK`。
- 通过 `POST /chat` 请求：返回 HTTP 200 和真实模型回答。
- 测试不读取真实密钥，也不发起网络请求。
