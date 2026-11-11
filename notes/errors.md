# FastAPI 统一异常处理

## 1. 为什么要统一处理

路由是 HTTP 方法和路径与 Python 函数之间的对应关系，例如：

```text
POST /chat -> chat()
GET /health -> health()
```

如果每个路由函数都自己写 `try/except`，错误格式容易不一致，也会出现重复代码。FastAPI 的异常处理器可以集中处理多个路由中的同类错误。

## 2. 统一错误响应

```python
class ErrorResponse(BaseModel):
    code: int
    message: str
    request_id: str
```

三类错误都返回相同的字段：

```json
{
  "code": 500,
  "message": "服务器内部错误",
  "request_id": "request-500"
}
```

- `code`：HTTP 错误状态。
- `message`：可以给用户看的安全说明。
- `request_id`：用于查找这次请求的日志。

## 3. 错误与状态码

- `AppError` -> `400`：用户或业务请求不正确。
- `requests.Timeout` -> `504`：服务等待 DeepSeek 等上游服务超时。
- 其他 `Exception` -> `500`：未知的服务器内部错误。

## 4. 异常处理器

```python
@app.exception_handler(AppError)
async def handle_app_error(
    request: Request,
    exc: AppError,
) -> JSONResponse:
```

`@app.exception_handler(AppError)` 表示：当路由处理过程中出现 `AppError`，FastAPI 就调用这个函数。

- `request`：发生错误的 HTTP 请求。
- `exc`：被捕获的异常对象。
- `JSONResponse`：可以同时指定 HTTP 状态码、JSON 内容和响应头。

## 5. request.state

请求日志中间件先保存请求编号：

```python
request.state.request_id = request_id
```

`request.state` 可以理解为“只属于当前这次请求的临时收纳盒”。中间件放入 `request_id`，后面的异常处理器可以取出同一个编号。

```python
getattr(request.state, "request_id", "unknown")
```

`getattr()` 读取对象属性；如果 `request_id` 不存在，就使用默认值 `"unknown"`。

## 6. model_dump 和 JSONResponse

```python
body = ErrorResponse(...)

return JSONResponse(
    status_code=status_code,
    content=body.model_dump(),
    headers={"X-Request-ID": request_id},
)
```

`model_dump()` 把 Pydantic 对象转换为 Python 字典，交给 `JSONResponse` 变成 JSON 响应。

## 7. 不泄露内部信息

上游超时不直接返回 `str(exc)`，未知错误也只返回“服务器内部错误”。真实错误和堆栈仅留在服务器日志中，不返回给用户。

## 8. 当天验证

- `AppError` 返回统一 `400` JSON。
- `requests.Timeout` 返回统一 `504` JSON，不泄露上游错误细节。
- `RuntimeError` 返回统一 `500` JSON，不泄露内部敏感内容。
