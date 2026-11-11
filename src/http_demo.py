import requests


url = "https://httpbin.org/get"

response = requests.get(url, timeout=10)
data = response.json() # 服务器返回的是JSON数据 .json() 将其转换成Python字典

print("请求方法:GET")
print("状态码:", response.status_code)
print("响应数据:", data)
print("服务器收到的 URL:", data["url"])



print("\n---------------- POST 请求 ----------------")

post_url = "https://httpbin.org/post"

request_data = {
    "question": "什么是 HTTP?",
    "model": "demo-model"
}

post_response = requests.post(
    post_url,
    json=request_data,
    timeout=10
)

post_data = post_response.json()

print("请求方法:POST")
print("状态码:", post_response.status_code)
print("我们发送的数据:", request_data)
print("服务器收到的数据:", post_data["json"])



print("\n---------------- 失败响应 ----------------")

bad_request_response = requests.get(
    "https://httpbin.org/status/400",
    timeout=10
)

server_error_response = requests.get(
    "https://httpbin.org/status/500",
    timeout=10
)

print("模拟错误请求的状态码:", bad_request_response.status_code)
print("模拟服务器错误的状态码:", server_error_response.status_code)