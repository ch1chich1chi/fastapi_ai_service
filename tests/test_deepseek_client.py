import unittest
from unittest.mock import Mock, patch

from src.clients.deepseek import DeepSeekClient


class DeepSeekClientTest(unittest.TestCase):
    def test_requires_api_key(self) -> None:
        with patch.dict("os.environ", {}, clear=True):
            with self.assertRaisesRegex(ValueError, "DEEPSEEK_API_KEY"):
                DeepSeekClient()

    @patch("src.clients.deepseek.requests.post")
    def test_generate_returns_assistant_content(self, mock_post: Mock) -> None:
        response = Mock()
        response.json.return_value = {
            "choices": [{"message": {"content": "FastAPI 是 Web 框架。"}}]
        }
        mock_post.return_value = response

        client = DeepSeekClient(api_key="test-key")
        answer = client.generate("什么是 FastAPI？")

        self.assertEqual(answer, "FastAPI 是 Web 框架。")
        response.raise_for_status.assert_called_once_with()
        mock_post.assert_called_once_with(
            "https://api.deepseek.com/chat/completions",
            headers={
                "Authorization": "Bearer test-key",
                "Content-Type": "application/json",
            },
            json={
                "model": "deepseek-flash",
                "messages": [
                    {"role": "user", "content": "什么是 FastAPI？"}
                ],
                "thinking": {"type": "disabled"},
            },
            timeout=30,
        )


if __name__ == "__main__":
    unittest.main()
