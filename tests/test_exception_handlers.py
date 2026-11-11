import os
import unittest
from unittest.mock import patch

import requests
from fastapi.testclient import TestClient

from src.errors import AppError

with patch.dict(os.environ, {"DEEPSEEK_API_KEY": "test-key"}):
    from src.main import app


class ExceptionHandlersTest(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app, raise_server_exceptions=False)

    def test_app_error_returns_400_in_standard_format(self) -> None:
        with patch(
            "src.routers.chat.service.reply",
            side_effect=AppError("请求内容不正确"),
        ):
            response = self.client.post(
                "/chat",
                headers={"X-Request-ID": "request-400"},
                json={"question": "hello"},
            )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json(),
            {
                "code": 400,
                "message": "请求内容不正确",
                "request_id": "request-400",
            },
        )
        self.assertEqual(response.headers["X-Request-ID"], "request-400")

    def test_timeout_returns_504_in_standard_format(self) -> None:
        with patch(
            "src.routers.chat.service.reply",
            side_effect=requests.Timeout("secret upstream detail"),
        ):
            response = self.client.post(
                "/chat",
                headers={"X-Request-ID": "request-504"},
                json={"question": "hello"},
            )

        self.assertEqual(response.status_code, 504)
        self.assertEqual(
            response.json(),
            {
                "code": 504,
                "message": "模型服务响应超时",
                "request_id": "request-504",
            },
        )
        self.assertNotIn("secret upstream detail", response.text)

    def test_unknown_error_returns_safe_500_response(self) -> None:
        with patch(
            "src.routers.chat.service.reply",
            side_effect=RuntimeError("database password leaked"),
        ):
            response = self.client.post(
                "/chat",
                headers={"X-Request-ID": "request-500"},
                json={"question": "hello"},
            )

        self.assertEqual(response.status_code, 500)
        self.assertEqual(
            response.json(),
            {
                "code": 500,
                "message": "服务器内部错误",
                "request_id": "request-500",
            },
        )
        self.assertNotIn("database password leaked", response.text)


if __name__ == "__main__":
    unittest.main()
