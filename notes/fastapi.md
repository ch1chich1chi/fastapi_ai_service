# FastAPI 学习记录

日期：2026-10-08

## 1. 启动项目

在项目根目录运行：

```powershell
.\.venv\Scripts\python.exe -m uvicorn src.main:app --reload
```

启动后可以访问：

- 健康检查：`http://127.0.0.1:8000/health`
- 接口文档：`http://127.0.0.1:8000/docs`
- 接口描述：`http://127.0.0.1:8000/openapi.json`

## 2. 使用 /docs 调试接口

`/docs` 是 FastAPI 自动生成的接口文档和人工调试页面。

调用 `POST /chat` 的步骤：

1. 点击绿色的 `POST /chat` 展开接口。
2. 点击 `Try it out`。
3. 在 `Request body` 中填写 JSON。
4. 点击 `Execute` 发送请求。
5. 在 `Server response` 中查看状态码和返回数据。

## 3. 页面内容

- `Curl`：这次请求对应的 curl 命令。
- `Request URL`：请求的接口地址。
- `Code`：服务器返回的 HTTP 状态码。
- `Response body`：服务器返回的 JSON 数据。
- `Response headers`：服务器返回的响应头。

## 4. POST /chat 正常测试

请求体：

```json
{
  "question": "什么是 FastAPI？"
}
```

预期状态码：`200`

预期返回：

```json
{
  "answer": "收到你的问题：什么是 FastAPI？"
}
```

## 5. POST /chat 校验失败测试

以下请求应返回 `422 Unprocessable Entity`：

### 缺少 question

```json
{}
```

### question 为空字符串

```json
{
  "question": ""
}
```

### question 超过 500 个字符

Pydantic 会按照 `ChatRequest` 中的字段规则拒绝错误数据，FastAPI 会在执行 `chat()` 之前自动返回 422。

## 6. 请求和响应过程

```text
客户端发送 JSON
        ↓
ChatRequest 检查请求数据
        ↓
chat() 处理问题
        ↓
ChatResponse 组织响应数据
        ↓
FastAPI 返回 JSON
```
