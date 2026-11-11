# Python logging 学习笔记

## 1. logging 是什么

`logging` 是 Python 自带的日志工具，可以理解为“更专业的 `print()`”。

`print()` 只输出文字：

```python
print("程序启动了")
```

`logging` 还可以标记这条消息是正常信息还是错误：

```python
import logging

logging.basicConfig(level=logging.INFO)
logging.info("程序启动了")
```

输出类似：

```text
INFO:root:程序启动了
```

## 2. 三行代码的含义

```python
import logging
```

导入 Python 自带的日志工具，不需要另外安装。

```python
logging.basicConfig(level=logging.INFO)
```

完成最基本的日志配置，并允许显示 `INFO` 及更严重级别的日志。

```python
logging.info("程序启动了")
```

记录一条正常运行信息。

## 3. 与 print 的区别

```python
logging.info("调用成功")
logging.error("调用失败")
```

`info()` 用于正常情况，`error()` 用于失败情况。日志级别可以帮助开发者快速区分不同类型的运行消息。

## 4. 常用日志级别

- `DEBUG`：调试细节。
- `INFO`：程序正常运行。
- `WARNING`：出现异常迹象，但程序还能继续。
- `ERROR`：本次操作失败。

```python
logging.basicConfig(level=logging.INFO)
```

`INFO` 是显示门槛：`DEBUG` 不显示，`INFO`、`WARNING` 和 `ERROR` 会显示。

## 5. 当前模块的 logger

```python
logger = logging.getLogger(__name__)
```

`getLogger()` 获取一个日志记录器，`__name__` 是当前 Python 模块名。项目中一般使用 `logger.info()`，这样能从日志看出消息来自哪个模块。

## 6. 日志格式与占位符

```python
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
```

占位符是模板中预留的位置，运行时由 `logging` 填入真实内容：

- `%(asctime)s`：时间。
- `%(levelname)s`：日志级别。
- `%(name)s`：模块名。
- `%(message)s`：记录的消息。

`format="...",` 末尾的逗号在字符串外面，是多行函数参数中允许保留的尾随逗号，不属于日志内容。

## 7. 项目中的统一日志配置

`src/logging_config.py` 为 `src` 下的项目日志设置 `INFO` 级别和统一格式。

```python
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter(LOG_FORMAT))
project_logger.addHandler(handler)
```

- `StreamHandler()` 把日志输出到终端。
- `Formatter` 规定每条日志的展示格式。
- `addHandler()` 把输出方式交给项目 logger。

## 8. FastAPI 请求日志中间件

```python
@app.middleware("http")
async def log_requests(request: Request, call_next):
```

中间件会包住每一次 HTTP 请求。`request` 是当前请求，`call_next(request)` 把请求交给真正的路由函数。

```python
request_id = request.headers.get("X-Request-ID") or uuid4().hex
```

客户端如果携带了请求编号就使用它，否则用 `uuid4()` 自动生成唯一编号。

```python
start_time = perf_counter()
elapsed_ms = (perf_counter() - start_time) * 1000
```

`perf_counter()` 用于测量一段代码用了多少时间，乘以 `1000` 把秒换算成毫秒。

正常日志示例：

```text
request_started request_id=manual-check-001 method=POST path=/chat
request_finished request_id=manual-check-001 method=POST path=/chat status=200 elapsed_ms=821.57
```

异常时使用 `logger.exception()` 记录 `ERROR` 和内部堆栈，然后继续抛出异常，交给 FastAPI 的异常处理流程。

### async 和 await 的当前理解

```python
async def log_requests(request: Request, call_next):
    response = await call_next(request)
```

`async` 和 `await` 属于 Python 异步语法。在当前阶段，可以先把 `await` 理解为：等待路由函数、模型请求或其他耗时操作完成，再继续使用其返回结果。当前只需认出这个流程，后续再专门学习异步原理。

### 日志数值占位符

```python
logger.info("status=%s elapsed_ms=%.2f", status, elapsed_ms)
```

- `%s`：填入普通数据，并按字符串形式显示。
- `%.2f`：填入小数，并保留小数点后两位。

例如 `elapsed_ms=821.567` 使用 `%.2f` 后会显示为 `821.57`。

### 这段代码中不同知识的分类

- `async def` / `await` / `try` / `except` / `raise`：Python 语法。
- `%s` / `%.2f`：日志消息中的格式化占位符。
- `@app.middleware("http")`：FastAPI 提供的中间件装饰器。
- `Request` / `call_next`：FastAPI/Starlette 请求处理流程中的对象。
- `uuid4()` / `perf_counter()`：Python 标准库提供的工具。

## 9. 日志安全

项目只记录 `request_id`、HTTP 方法、路径、状态码和耗时。不记录 API Key、完整请求头或用户问题正文，避免敏感信息进入日志。
