# W2 FastAPI 核心复盘

## 1. 本周完成的完整链路

```text
POST /chat
-> ChatRequest 校验请求
-> Router 接收 HTTP 数据
-> ChatService 组织聊天流程
-> DeepSeekClient 请求真实模型
-> ChatResponse 返回结构化 JSON
```

请求的外层还有：

```text
请求日志中间件
-> request_id / method / path / status / elapsed_ms
-> 统一异常处理
-> 400 / 504 / 500 安全 JSON
```

## 2. 分层职责

- Router：接收请求和返回响应。
- Service：组织业务流程。
- Client：调用 DeepSeek 等外部服务。

通过依赖注入和 `LLMClient` Protocol，Service 只依赖 `generate()` 能力，不绑定某个具体模型。

## 3. 状态码

- `200`：请求正常完成。
- `400`：业务或请求内容不正确。
- `422`：Pydantic 请求数据校验失败。
- `500`：未知服务器内部错误。
- `504`：等待 DeepSeek 等上游服务超时。

## 4. 安全原则

- API Key 只从环境变量读取，不进入 Git。
- 日志不记录完整 API Key、请求头和用户问题正文。
- 500/504 响应不返回 Python 堆栈和内部错误细节。
- 测试通过 `patch()` 使用假回答和假异常，不请求真实 DeepSeek。

## 5. 测试覆盖

- Client 的请求格式与密钥缺失。
- 请求日志的 `request_id`、状态和耗时。
- 400/504/500 统一异常响应。
- `/health`、`/chat` 正常请求、空问题和上游超时。

## 6. 当前需要继续熟悉的内容

- `async/await`：当前达到“见过并能识别等待流程”，后续通过更多 FastAPI 代码继续熟悉。
- FastAPI 中间件和异常处理器：当前要能说出职责和调用顺序，不要求从空白默写。
- pytest `patch()`：当前要能看懂“临时替换真实依赖”，后续在数据库和 Agent 测试中继续使用。

## 7. 本周口述

### 为什么分 Router / Service / Client

三层分别处理 HTTP、业务流程和外部模型调用，避免所有代码堆在路由函数中，也便于替换模型和单独测试。

### 422、400、500、504 的区别

422 是 Pydantic 发现请求结构不合格；400 是请求已进入业务流程但不符合业务要求；500 是未知的服务器内部错误；504 是本服务等待上游服务超时。

## 8. W2 面试口述练习

### 第一题：为什么分 Router / Service / Client

练习结果：已经能够说出三层的基本职责。

```text
Router：接收 HTTP 请求并返回响应。
Service：组织业务流程。
Client：请求 DeepSeek 等外部服务。
```

拆分后的好处：职责更清楚，便于维护、测试和替换模型客户端。

### 第二题：422、400、500、504 的区别

练习结果：第一次未能回忆起来；经过讲解后，能够正确对应 422、400、500、504，并分清 502 与 504，复测通过。

记忆顺序：

```text
422：请求数据校验失败，例如缺少 question 或 question 为空。
400：请求通过了格式校验，但不符合业务规则。
500：程序发生未预料到的内部错误。
504：本服务等待 DeepSeek 等上游服务超时。
```

可以先记成：

```text
422 数据不合格
400 业务不接受
500 自己出故障
504 等上游超时
```

## 9. AI Agent 实习 JD 高频词汇

根据近期 AI 应用开发实习岗位中反复出现的要求，整理为以下 10 项：

| 分类 | 高频词汇 | 当前状态 | 后续安排 |
| --- | --- | --- | --- |
| Python/FastAPI | Python | 已会基础 | 在后续项目中继续练习类、异常、类型标注和异步代码 |
| Python/FastAPI | FastAPI / REST API | 已会基础 | 已实现路由、Pydantic、日志、异常和测试 |
| Python/FastAPI | SQL / MySQL / PostgreSQL | 未学 | W3 学习 SQLite、SQLAlchemy 和会话 CRUD |
| RAG | RAG | 未学 | W5 开始学习文档导入、切分与检索 |
| RAG | Embedding / 向量数据库 | 未学 | W5 学习向量化与 Chroma |
| RAG | LangChain / LlamaIndex | 未学 | 在 RAG 和 Agent 阶段按项目需要学习 |
| Agent | LLM API / Prompt Engineering | 部分会 | 已调用 DeepSeek API，后续补系统提示词和效果优化 |
| Agent | Agent / LangGraph / Tool Calling | 未学 | W7-W9 逐步学习工具调用与工作流 |
| 工程化 | Linux / Git | 已会基础 | 已掌握基础命令、提交、分支和合并，后续结合部署加强 |
| 工程化 | Docker | 未学 | W4 学习镜像、容器、Dockerfile 和 Compose |

当前判断：不用因为大部分词汇标记为“未学”而着急。它们本来就安排在后续周次；W2 只需要知道岗位会要求这些能力，并确认学习路线正在覆盖它们。

## 10. W2 最终状态

- D1-D6 技术任务：完成。
- 面试口述：完成。
- 10 条 JD 高频词汇整理：完成。
- W2：正式完成。

### JD 样本来源

- [DXC Technology - AI 应用开发实习生](https://dxctechnology.wd1.myworkdayjobs.com/en-US/DXCJobs/job/AI_51589643)
- [富利建设集团 - 大模型应用开发实习生](https://www.zhaopin.com/jobdetail/CC148211770J40909195203.htm)
- [天津恩恩科技 - AI 开发实习生](https://career.hebut.edu.cn/home/correcruit/content/id/76611.html)
- [蔚来大模型应用开发实习岗位信息](https://www.applysquare.com/opportunity-cn/o9y2Q9kNv6p8UV/)
