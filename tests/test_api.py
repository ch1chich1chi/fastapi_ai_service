import os
from unittest.mock import patch

import requests
from fastapi.testclient import TestClient


os.environ.setdefault("DEEPSEEK_API_KEY", "test-key")

from src.main import app

from src.database import (
    connect_database,
    create_message,
    initialize_database,
    list_messages,
)

client = TestClient(app)


def test_health_returns_ok():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_chat_returns_answer():
    with patch(
        "src.routers.chat.service.reply",
        return_value="这是测试回答",
    ):
        response = client.post(
            "/chat",
            json={"question": "什么是 FastAPI?"},
        )

    assert response.status_code == 200
    assert response.json() == {"answer": "这是测试回答"}


def test_chat_rejects_empty_question():
    with patch("src.routers.chat.service.reply") as mock_reply:
        response = client.post(
            "/chat",
            json={"question": ""},
        )

    assert response.status_code == 422
    mock_reply.assert_not_called()


def test_chat_returns_504_when_upstream_times_out():
    with patch(
        "src.routers.chat.service.reply",
        side_effect=requests.Timeout("upstream timeout"),
    ):
        response = client.post(
            "/chat",
            json={"question": "hello"},
        )

    assert response.status_code == 504
    assert response.json()["message"] == "模型服务响应超时"

def test_create_conversation(tmp_path):
    database_path = tmp_path / "test_chat.db"
    initialize_database(database_path)

    def open_test_database():
        return connect_database(database_path)

    with patch(
        "src.routers.conversations.connect_database",
        side_effect=open_test_database,
    ):
        response = client.post(
            "/conversations",
            json={"title": "SQL学习"},
        )

    assert response.status_code == 201
    assert response.json() == {"id": 1, "title": "SQL学习"}

def test_list_conversations(tmp_path):
    database_path = tmp_path / "test_chat.db"
    initialize_database(database_path)

    def open_test_database():
        return connect_database(database_path)

    with patch(
        "src.routers.conversations.connect_database",
        side_effect=open_test_database,
    ):
        empty_response = client.get("/conversations")
        assert empty_response.status_code == 200
        assert empty_response.json() == []

        first = client.post(
            "/conversations",
            json={"title": "SQL学习"},
        )
        second = client.post(
            "/conversations",
            json={"title": "Python学习"},
        )
        assert first.status_code == 201
        assert second.status_code == 201

        response = client.get("/conversations")

    assert response.status_code == 200
    assert response.json() == [
        {"id": 1, "title": "SQL学习"},
        {"id": 2, "title": "Python学习"},
    ]


def test_get_conversation(tmp_path):
    # 一、准备临时数据库
    database_path = tmp_path / "test_chat.db"
    initialize_database(database_path)

    def open_test_database():
        return connect_database(database_path)

    # 二、让接口使用临时库，然后发请求
    with patch(
        "src.routers.conversations.connect_database",
        side_effect=open_test_database,
    ):
        client.post(
            "/conversations",
            json={"title": "SQL学习"},
        )
        response = client.get("/conversations/1")

    # 三、检查刚才收到的响应
    assert response.status_code == 200
    assert response.json() == {"id": 1, "title": "SQL学习"}


def test_get_missing_conversation_returns_404(tmp_path):
    database_path = tmp_path / "test_chat.db"
    initialize_database(database_path)

    def open_test_database():
        return connect_database(database_path)

    with patch(
        "src.routers.conversations.connect_database",
        side_effect=open_test_database,
    ):
        response = client.get("/conversations/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "会话不存在"}


def test_rename_conversation(tmp_path):
    database_path = tmp_path / "test_chat.db"
    initialize_database(database_path)

    def open_test_database():
        return connect_database(database_path)

    with patch(
        "src.routers.conversations.connect_database",
        side_effect=open_test_database,
    ):
        created = client.post(
            "/conversations",
            json={"title": "SQL学习"},
        )
        assert created.status_code == 201

        renamed = client.patch(
            "/conversations/1",
            json={"title": "数据库复习"},
        )
        assert renamed.status_code == 200
        expected = {"id": 1, "title": "数据库复习"}
        assert renamed.json() == expected

        fetched = client.get("/conversations/1")
        assert fetched.status_code == 200
        assert fetched.json() == expected

        listed = client.get("/conversations")
        assert listed.status_code == 200
        assert listed.json() == [expected]


def test_rename_missing_conversation_returns_404(tmp_path):
    database_path = tmp_path / "test_chat.db"
    initialize_database(database_path)

    def open_test_database():
        return connect_database(database_path)

    with patch(
        "src.routers.conversations.connect_database",
        side_effect=open_test_database,
    ):
        response = client.patch(
            "/conversations/999",
            json={"title": "数据库复习"},
        )

    assert response.status_code == 404  
    assert response.json() == {"detail": "会话不存在"}


def test_delete_conversation_removes_its_messages_only(tmp_path):
    database_path = tmp_path / "test_chat.db"
    initialize_database(database_path)

    def open_test_database():
        return connect_database(database_path)

    with patch(
        "src.routers.conversations.connect_database",
        side_effect=open_test_database,
    ):
        first = client.post("/conversations", json={"title": "待删除"})
        second = client.post("/conversations", json={"title": "保留"})
        assert first.status_code == 201
        assert second.status_code == 201

        conn = connect_database(database_path)
        try:
            create_message(conn, 1, "user", "待删除的消息")
            create_message(conn, 2, "user", "保留的消息")
        finally:
            conn.close()

        deleted = client.delete("/conversations/1")
        assert deleted.status_code == 204
        assert deleted.content == b""

        assert client.get("/conversations/1").status_code == 404
        remaining = client.get("/conversations/2")
        assert remaining.status_code == 200
        assert remaining.json() == {"id": 2, "title": "保留"}
        listed = client.get("/conversations")
        assert listed.status_code == 200
        assert listed.json() == [{"id": 2, "title": "保留"}]

    conn = connect_database(database_path)
    try:
        assert list_messages(conn, 1) == []
        assert list_messages(conn, 2) == [(2, "user", "保留的消息")]
    finally:
        conn.close()


def test_delete_missing_conversation_returns_404(tmp_path):
    database_path = tmp_path / "test_chat.db"
    initialize_database(database_path)

    def open_test_database():
        return connect_database(database_path)

    with patch(
        "src.routers.conversations.connect_database",
        side_effect=open_test_database,
    ):
        response = client.delete("/conversations/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "会话不存在"}

def test_create_conversation_rejects_missing_title():
    with patch(
        "src.routers.conversations.connect_database",
    ) as mock_connect:
        response = client.post(
            "/conversations",
            json={},
        )

    assert response.status_code == 422
    mock_connect.assert_not_called()