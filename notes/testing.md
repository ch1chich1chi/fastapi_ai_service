# Python 与 FastAPI 测试笔记

## 1. 测试是什么

测试可以理解为：让 Python 自动运行一段代码，再检查实际结果是否符合预期。

一条测试通常包含三步：

```text
准备数据
-> 执行代码
-> 检查结果
```

## 2. pytest

`pytest` 是用来寻找和运行 Python 测试的工具。它默认会识别：

- 名字以 `test_` 开头的 Python 文件。
- 名字以 `test_` 开头的测试函数。

例如：

```python
def test_add():
    result = 1 + 1
    assert result == 2
```

`test_add` 表示这是一个检查加法结果的测试函数。

## 3. assert

`assert` 是 Python 语法，可以理解为“确认后面的条件为真”。

```python
assert result == 2
```

表示确认 `result` 等于 `2`。

- 条件为真：测试继续并通过。
- 条件为假：抛出 `AssertionError`，测试失败。

## 4. 测试 FastAPI 接口的思路

以 `GET /health` 为例：

```text
准备：创建 TestClient
执行：请求 GET /health
检查：状态码是 200，JSON 是 {"status": "ok"}
```

- `TestClient` 用于在测试中模拟浏览器、curl 或其他客户端请求 FastAPI。
- 使用 `TestClient` 时不需要手动启动浏览器。
- 后续学到的新测试语法继续记录在本文件。

## 5. TestClient 基础代码

```python
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)
```

`TestClient(app)` 使用当前 FastAPI 应用创建测试客户端。测试时它直接在 Python 进程内请求应用，不需要启动 Uvicorn。

```python
response = client.get("/health")

assert response.status_code == 200
assert response.json() == {"status": "ok"}
```

- `client.get()` 模拟发送 GET 请求。
- `response.status_code` 读取 HTTP 状态码。
- `response.json()` 把 JSON 响应转换为 Python 数据。

## 6. os.environ.setdefault

```python
os.environ.setdefault("DEEPSEEK_API_KEY", "test-key")
```

`setdefault()` 表示：

- 如果 `DEEPSEEK_API_KEY` 已经存在，保留原值。
- 如果不存在，在当前测试进程中使用 `"test-key"`。

这样导入 FastAPI 应用时不会因缺少密钥而失败。测试使用的是假值，不是真实 API Key。

## 7. POST 请求与 json 参数

```python
response = client.post(
    "/chat",
    json={"question": "什么是 FastAPI？"},
)
```

- `client.post()` 模拟 POST 请求。
- `json={...}` 把 Python 字典作为 JSON 请求体发送给 FastAPI。

## 8. patch 临时替换依赖

```python
with patch(
    "src.routers.chat.service.reply",
    return_value="这是测试回答",
):
    response = client.post(...)
```

`patch()` 在 `with` 代码块内临时替换 `service.reply()`。

- `return_value`：调用被替换的方法时，直接返回指定结果。
- 离开 `with` 代码块后，原方法自动恢复。
- 因此测试不会真正请求 DeepSeek，不消耗额度。

模拟上游异常：

```python
with patch(
    "src.routers.chat.service.reply",
    side_effect=requests.Timeout("upstream timeout"),
):
    response = client.post(...)
```

`side_effect` 表示调用被替换的方法时抛出指定异常。这可以稳定地验证 504 处理，不需要真的等待网络超时。

## 9. 当前四类接口测试

- `GET /health` 返回 200 和 `{"status": "ok"}`。
- `POST /chat` 正常返回 200 和回答。
- 空 `question` 被 Pydantic 拦截并返回 422。
- 上游超时被统一异常处理转换为 504。

## 10. 运行命令

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

`-q` 是 quiet 的缩写，让输出更简洁。
