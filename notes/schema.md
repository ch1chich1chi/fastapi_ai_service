# SQLite 会话数据库设计

## 为什么需要数据库

当前 `Conversation` 和 `Message` 是 Python 内存对象。程序关闭后，内存中的会话和消息会消失。SQLite 可以把数据保存到本地 `.db` 文件中，让程序重启后仍能读取。

## conversations 表

一行表示一次聊天会话。

| 字段 | SQLite 类型 | 规则 | 含义 |
| --- | --- | --- | --- |
| `id` | `INTEGER` | 主键、自动编号 | 会话的唯一编号 |
| `title` | `TEXT` | 非空、不能是空字符串 | 会话标题 |
| `created_at` | `TEXT` | 默认当前时间 | 创建时间 |

## messages 表

一行表示一条聊天消息。

| 字段 | SQLite 类型 | 规则 | 含义 |
| --- | --- | --- | --- |
| `id` | `INTEGER` | 主键、自动编号 | 消息的唯一编号 |
| `conversation_id` | `INTEGER` | 非空、外键 | 所属会话的编号 |
| `role` | `TEXT` | 只能是 `system`、`user`、`assistant` | 消息角色 |
| `content` | `TEXT` | 非空、不能是空字符串 | 消息正文 |
| `created_at` | `TEXT` | 默认当前时间 | 创建时间 |

## 两张表的关系

```text
conversations.id  <---  messages.conversation_id
       主键                       外键
```

一个会话可以拥有多条消息，一条消息只能属于一个会话，这叫一对多关系。

如果 `conversations` 中不存在 `id = 8`，就不能插入 `conversation_id = 8` 的消息。连接 SQLite 时需要执行 `PRAGMA foreign_keys = ON`，外键检查才会生效。

## MySQL 与 SQLite 的基础差异

| 用途 | MySQL 常见写法 | SQLite 写法 |
| --- | --- | --- |
| 整数 | `INT` | `INTEGER` |
| 字符串 | `VARCHAR(100)` | `TEXT` |
| 自动编号 | `AUTO_INCREMENT` | `AUTOINCREMENT` |
| 字段注释 | `COMMENT` | 使用 `--` 或单独文档说明 |

项目当前使用 SQLite。W4 学习 Docker Compose 时再启动 MySQL，并通过 `DATABASE_URL` 切换数据库。
