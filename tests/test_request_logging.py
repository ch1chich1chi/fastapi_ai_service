import os
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

with patch.dict(os.environ, {"DEEPSEEK_API_KEY": "test-key"}):
    from src.main import app


class RequestLoggingTest(unittest.TestCase):
    def test_successful_request_logs_request_id_status_and_elapsed_time(self) -> None:
        client = TestClient(app)

        with self.assertLogs("src.main", level="INFO") as captured:
            response = client.get(
                "/health",
                headers={"X-Request-ID": "request-123"},
            )

        logs = "\n".join(captured.output)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["X-Request-ID"], "request-123")
        self.assertIn("request_started", logs)
        self.assertIn("request_finished", logs)
        self.assertIn("request_id=request-123", logs)
        self.assertIn("method=GET", logs)
        self.assertIn("path=/health", logs)
        self.assertIn("status=200", logs)
        self.assertIn("elapsed_ms=", logs)

    def test_failed_request_logs_request_id_and_error_status(self) -> None:
        client = TestClient(app, raise_server_exceptions=False)

        with patch(
            "src.routers.chat.service.reply",
            side_effect=RuntimeError("upstream failed"),
        ):
            with self.assertLogs("src.main", level="ERROR") as captured:
                response = client.post(
                    "/chat",
                    headers={"X-Request-ID": "request-500"},
                    json={"question": "hello"},
                )

        logs = "\n".join(captured.output)
        self.assertEqual(response.status_code, 500)
        self.assertIn("request_failed", logs)
        self.assertIn("request_id=request-500", logs)
        self.assertIn("status=500", logs)
        self.assertIn("elapsed_ms=", logs)


if __name__ == "__main__":
    unittest.main()
