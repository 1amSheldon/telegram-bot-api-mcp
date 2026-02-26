import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from server.errors import MethodNotFoundError
from server.telegram_data import TelegramData
from server.tools.methods import list_methods, resolve_method


class MethodsToolsTest(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.telegram_data = TelegramData(api_url=None)
        self.telegram_data.api_data = {
            "methods": {
                "sendMessage": {
                    "name": "sendMessage",
                    "href": "https://core.telegram.org/bots/api#sendmessage",
                    "description": ["Use this method to send text messages."],
                    "returns": ["Message"],
                    "fields": [
                        {
                            "name": "chat_id",
                            "types": ["Integer", "String"],
                            "required": True,
                            "description": "Unique identifier for the target chat.",
                        }
                    ],
                },
                "sendPhoto": {
                    "name": "sendPhoto",
                    "href": "https://core.telegram.org/bots/api#sendphoto",
                    "description": ["Use this method to send photos."],
                    "returns": ["Message"],
                    "fields": [],
                },
            },
            "types": {},
        }
        self.telegram_data.current_version = "Bot API 9.4 (February 9, 2026)"
        self.telegram_data.normalized_method_names = {
            self.telegram_data.normalize_name(name): name
            for name in self.telegram_data.api_data["methods"].keys()
        }
        self.telegram_data.method_search_text = {
            method_name: " ".join(
                [method_name.lower()] + method_data.get("description", [])
            ).lower()
            for method_name, method_data in self.telegram_data.api_data["methods"].items()
        }
        self.ctx = SimpleNamespace(lifespan_context={"telegram_data": self.telegram_data})

    async def test_resolve_method_supports_normalized_lookup(self) -> None:
        with patch("server.metrics.logger") as logger_mock:
            logger_mock.ainfo = AsyncMock(return_value=None)
            response = await resolve_method(name="send_message", ctx=self.ctx)

        self.assertEqual(response.data.name, "sendMessage")
        self.assertEqual(response.metadata.api_version, self.telegram_data.current_version)
        self.assertEqual(
            response.metadata.documentation_url,
            "https://core.telegram.org/bots/api#sendmessage",
        )

    async def test_resolve_method_returns_actionable_suggestions(self) -> None:
        with patch("server.metrics.logger") as logger_mock:
            logger_mock.ainfo = AsyncMock(return_value=None)
            with self.assertRaises(MethodNotFoundError) as exc:
                await resolve_method(name="sendMesage", ctx=self.ctx)

        self.assertIn("Did you mean", str(exc.exception))
        self.assertIn("list_methods(filter='passport')", str(exc.exception))

    async def test_list_methods_applies_filter_and_pagination(self) -> None:
        with patch("server.metrics.logger") as logger_mock:
            logger_mock.ainfo = AsyncMock(return_value=None)
            response = await list_methods(
                ctx=self.ctx,
                filter="photos",
                limit=1,
                offset=0,
            )

        self.assertEqual(response.data.total, 1)
        self.assertEqual(response.data.items, ["sendPhoto"])
        self.assertEqual(response.data.limit, 1)
        self.assertEqual(response.data.offset, 0)


if __name__ == "__main__":
    unittest.main()
