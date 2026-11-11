# HTTP 学习记录

日期：2026-10-04

## 1. HTTP 请求与响应

客户端向服务器发送 HTTP 请求，服务器处理后返回 HTTP 响应。

一次请求通常包括：

- 请求方法
- URL
- 请求头
- 请求数据

响应通常包括：

- 状态码
- 响应头
- 响应数据

## 2. GET 与 POST

- GET：从服务器获取数据。
- POST：向服务器提交数据，让服务器处理。

Python 可以使用 `requests` 发送请求：

```python
requests.get(url)
requests.post(url, json=data)
```

`curl`、Postman 和 Python `requests` 都能发送 HTTP 请求，只是使用方式不同。

## 3. 常见状态码

- 200：请求成功。
- 400：客户端提交的请求有问题。
- 404：请求的资源不存在。
- 500：服务器内部发生错误。

## 4. 今天的测试结果

### GET 请求

请求地址：`https://httpbin.org/get`

结果：状态码为 200，成功获得 JSON 响应。

### POST 请求

请求地址：`https://httpbin.org/post`

发送了 `question` 和 `model`，状态码为 200，服务器成功收到 JSON 数据。

### 失败响应

- `/status/400` 返回 400。
- `/status/500` 返回 500。

## 5. 与 Agent 项目的关系

Agent 通常使用 POST 请求，把问题、消息和模型参数作为 JSON 发送给模型 API。

FastAPI 接收请求并返回响应时，也需要正确设置状态码和响应数据。
