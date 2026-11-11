# FastAPI AI Service

Python AI 后端学习项目：FastAPI 单次模型问答、SQLite 会话CRUD、统一异常、请求日志和Docker/Compose；另有独立的MySQL连接练习。

## 安装依赖

在项目根目录操作。新环境先创建虚拟环境（已有 `.venv` 可跳过）：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip install pytest httpx
```

## DeepSeek 配置

项目从环境变量 `DEEPSEEK_API_KEY` 读取密钥，不要把真实密钥写入代码或提交到 Git。

默认模型和请求超时时间保存在 `config.json`。

若本机尚未设置密钥，可在当前PowerShell中隐藏输入，再启动应用或Compose：

```powershell
$modelPracticeSecret = Read-Host "输入DeepSeek API Key" -AsSecureString
$env:DEEPSEEK_API_KEY = [System.Net.NetworkCredential]::new("", $modelPracticeSecret).Password
Remove-Variable modelPracticeSecret
```

## 启动服务

首次使用空SQLite数据库时先初始化，已有数据无需每次重复：

```powershell
.\.venv\Scripts\python.exe -c "from src.database import initialize_database; initialize_database()"
```

```powershell
.\.venv\Scripts\python.exe -m uvicorn src.main:app --reload
```

## 验证服务

- 健康检查：`http://127.0.0.1:8000/health`
- 接口文档：`http://127.0.0.1:8000/docs`
- OpenAPI：`http://127.0.0.1:8000/openapi.json`

命令行验证：

```powershell
curl.exe -i http://127.0.0.1:8000/health
```

聊天接口：

```powershell
$chatBody = @{ question = "什么是 FastAPI？" } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/chat -ContentType "application/json; charset=utf-8" -Body ([System.Text.Encoding]::UTF8.GetBytes($chatBody))
```

正常响应示例：

```json
{
  "answer": "FastAPI 是一个 Python Web 框架。"
}
```

统一错误响应示例：

```json
{
  "code": 504,
  "message": "模型服务响应超时",
  "request_id": "abc123"
}
```

## 运行测试

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

## Docker 与 Compose（Windows PowerShell）

以下命令在项目根目录（包含 Dockerfile、compose.yaml 的目录）执行，需要 Docker Desktop 引擎已启动。

### 1. 准备环境变量

在当前 PowerShell 中配置有效的 `DEEPSEEK_API_KEY`，再运行 Compose。检查是否为空，不显示密钥内容：

```powershell
[string]::IsNullOrWhiteSpace($env:DEEPSEEK_API_KEY)
```

`False` 表示有值，是否有效还需真实调用验证。Compose 通过 `${DEEPSEEK_API_KEY:?请先设置环境变量}` 读取该值；未设置或为空时停止并提示。不要把真实密钥写入配置文件或提交到 Git。

### 2. 构建并启动

```powershell
docker build -t fastapi-ai-service:learning .
docker compose up -d api
docker compose ps
```

`docker build` 按 Dockerfile 构建镜像；末尾的 `.` 指当前目录为构建上下文。Compose 当前只有 `image`、没有 `build` 配置，因此首次使用或更新应用代码后先执行构建。

API 在容器内监听 `0.0.0.0:8000`，Compose 将本机 `127.0.0.1:9000` 转发至容器8000端口；此绑定仅供本机访问。

修改传入容器的环境变量后，在设置了新值的同一个 PowerShell 中执行：

```powershell
docker compose up -d --force-recreate api
```

已有容器不会自动同步宿主机后来修改的环境变量；`docker start` 只启动原容器，重建才会应用新配置。

### 3. 首次初始化 SQLite

首次使用空数据卷时执行一次；已有数据库无需因每次重启而重复初始化：

```powershell
docker compose exec api python -c "from src.database import initialize_database; initialize_database()"
```

SQLite 文件位于容器 `/app/data/chat.db`。Compose 的 `sqlite-learning-data` 命名卷挂载到 `/app/data`，用于保留会话数据。

### 4. 验证接口和持久化

```powershell
curl.exe -i http://127.0.0.1:9000/health
```

预期返回200和 `{"status":"ok"}`。这只证明健康检查可访问，不证明数据库或真实模型调用成功。

打开 `http://127.0.0.1:9000/docs`，在 `POST /chat` 中提交 `{"question":"请只回复：连接成功"}`，检查 **Server response** 的实际状态码和回答；这是一次真实模型调用，产生相应Token用量。

持久化检查：在 `/docs` 创建练习会话，记下实际返回的id和title；执行上述 `--force-recreate` 命令后，按该id查询，确认仍返回同一会话。

### 5. 日志与停止

```powershell
docker compose logs --tail 50 api
docker compose stop api
```

第一条读取最后最多50行日志，不重启容器；可按响应头 `X-Request-ID` 的值查找同一次请求的记录。第二条停止服务，保留容器和卷；下次用 `docker compose up -d api` 启动。

`docker compose down` 删除容器和网络，默认保留命名卷；`docker compose down -v` 会删除本项目声明的命名卷及其中数据，持久化验证时不要使用 `-v`。

## 会话 API（SQLite）

本机 Uvicorn 默认地址为 `http://127.0.0.1:8000`；上述 Compose 配置使用 `http://127.0.0.1:9000`。打开对应地址的 `/docs`，选择接口后点击 **Try it out → Execute**，在 **Server response** 查看实际结果。

| 操作 | 方法与路径 | JSON请求体 | 成功响应 |
|---|---|---|---|
| 创建会话 | `POST /conversations` | `{"title":"练习会话"}` | 201，返回实际分配的id和title |
| 列出会话 | `GET /conversations` | 无 | 200，返回会话列表；无会话时为 `[]` |
| 查询单个会话 | `GET /conversations/{conversation_id}` | 无 | 200，返回id和title |
| 修改会话标题 | `PATCH /conversations/{conversation_id}` | `{"title":"修改后的标题"}` | 200，返回id和新title |
| 删除会话 | `DELETE /conversations/{conversation_id}` | 无 | 204，无响应正文 |

`{conversation_id}` 是路径参数，使用创建接口实际返回的id替换，不要固定假定为1。查询、改名或删除不存在的会话均返回404和 `{"detail":"会话不存在"}`。

创建/改名的 `title` 必填，长度为1–100字符；缺字段、空字符串或超长输入返回422，纯空白标题通过长度校验后由业务代码拒绝，返回400。

完整操作示例（下列id仅作示例）：

1. 创建 `{"title":"练习会话"}`，假设实际返回 `{"id":7,"title":"练习会话"}`。
2. 查询 `GET /conversations/7`，应得到同一id和title。
3. 向 `PATCH /conversations/7` 提交 `{"title":"修改后的标题"}`，再查询确认新标题。
4. 删除 `DELETE /conversations/7`，预期204且正文为空；再次查询同一id应返回404。

删除会话时，应用在同一事务中先删除该会话的消息，再删除会话；成功后提交，数据库异常时回滚并重抛异常。删除操作仅用于自己新建的练习会话。

当前会话接口负责SQLite会话记录的增删改查；`POST /chat` 是单次模型问答，没有接收会话id，也不会自动把问答保存到这些会话记录中。

## MySQL 最小 Python 连接练习

会话API仍使用SQLite；`src/mysql_demo.py` 是单独运行的PyMySQL练习，没有将API切换为MySQL。它从环境变量读取连接配置，参数化插入一条记录、提交，再按id查询。

### 前置环境

- 已按MySQL练习建立容器 `mysql-learning`，本机 `127.0.0.1:3307` 映射至容器3306端口，数据卷 `mysql-learning-data` 挂载到 `/var/lib/mysql`。
- 练习库 `agent_practice` 已有 `practice_tasks` 表，字段包含整数主键 `id`、文本 `title` 和 `status`。
- 练习账户 `agent_reader@%` 仅有该练习表的SELECT、INSERT权限；它与已删除的 `agent_reader@localhost` 不是同一账户。密码由使用者配置，不随仓库提供。
- 这部分需要额外安装驱动：`requirements.txt` 当前仅列API运行依赖，不包含PyMySQL。

在项目根目录执行：

```powershell
.\.venv\Scripts\python.exe -m pip install pymysql
docker start mysql-learning
$env:MYSQL_HOST = "127.0.0.1"
$env:MYSQL_PORT = "3307"
$env:MYSQL_DATABASE = "agent_practice"
$env:MYSQL_USER = "agent_reader"
```

在本机设置 `MYSQL_PASSWORD`。可用下列隐藏输入方式，不将密码直接写入命令历史：

```powershell
$mysqlPracticeSecret = Read-Host "输入练习账户密码" -AsSecureString
$env:MYSQL_PASSWORD = [System.Net.NetworkCredential]::new("", $mysqlPracticeSecret).Password
Remove-Variable mysqlPracticeSecret
```

也可使用已在本机配置的VS Code「Python: MySQL练习」启动项，运行时输入密码；该本地启动配置不能假定其他人克隆仓库后就有。

### 首次写入与重复查询

**先检查数据状态再运行脚本：当前脚本固定插入id=2，不能直接重复执行。** 本学习环境已经有id2，重复运行会触发主键冲突；不要为了重跑删除原有记录。

只在确认id2不存在、需要首次插入时运行：

```powershell
.\.venv\Scripts\python.exe -m src.mysql_demo
```

预期先输出连接地址及「MySQL连接成功」，再查询得到 `(2, 'Python连接练习', 'todo')`。INSERT用 `%s` 绑定数据，`conn.commit()` 提交写入；SELECT后用 `fetchone()` 取回一行。

在已有id2的环境复查时，用已有查询方式执行 `SELECT id, title, status FROM practice_tasks WHERE id = 2;`；如果要让Python脚本只查询，先跳过脚本中的INSERT及紧接它的commit，再运行，保留连接和SELECT部分。

终端练习结束后清除当前窗口的密码变量：

```powershell
Remove-Item Env:MYSQL_PASSWORD
```

这只清除当前终端的变量，不撤销数据库账户，不改变已有连接或容器内的配置。本文记录已有练习环境的接续方法；全新机器还需先完成MySQL容器、练习表及最小权限账户的准备。

## 当前进度

- 完成 Python 项目配置与环境变量练习。
- 完成消息、对话模型与自定义异常练习。
- 完成 HTTP GET、POST 和状态码练习。
- 完成 Router、Service、Client 分层，并接入真实 DeepSeek 聊天接口。
- 完成 HTTP 请求日志，可按 `X-Request-ID` 查看请求状态和耗时。
- 完成统一异常处理，业务错误、上游超时和未知错误分别返回 400、504 和 500。
- 完成 `/health` 和 `/chat` 的 pytest + TestClient 基础接口测试。
- 完成 SQLite 会话数据库设计、建表初始化和外键约束测试。
- 已实现SQLite会话创建、列表、单条查询、改名和删除接口；API测试使用临时数据库。
- 已本人验证Compose保卷重建后会话可读，以及容器内真实模型调用返回200。
- 已本人完成独立MySQL练习的参数化写入、提交和查询；API暂未接入MySQL。

## 当前边界

- `/chat`尚未串联会话历史与消息持久化；本项目还没有RAG或Agent功能。
- MySQL示例使用固定练习id，不是可直接重复执行的生产导入工具。
- 已有代码和助手测试结果不等于学习者独立掌握；删除失败回滚的本人局部验证仍待完成。
