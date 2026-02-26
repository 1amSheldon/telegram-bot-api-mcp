import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from server.errors import TypeNotFoundError
from server.telegram_data import TelegramData
from server.tools.types import list_types, resolve_type


class TypesToolsTest(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.telegram_data = TelegramData(api_url=None)
        self.telegram_data.api_data = {
            "methods": {},
            "types": {
                "ReplyKeyboardMarkup": {
                    "name": "ReplyKeyboardMarkup",
                    "href": "https://core.telegram.org/bots/api#replykeyboardmarkup",
                    "description": ["This object represents a custom keyboard."],
                    "fields": [
                        {
                            "name": "keyboard",
                            "types": ["Array of Array of KeyboardButton"],
                            "required": True,
                            "description": "Array of button rows.",
                        }
                    ],
                }
            },
        }
        self.telegram_data.current_version = "Bot API 9.4 (February 9, 2026)"
        self.telegram_data.normalized_type_names = {
            self.telegram_data.normalize_name(name): name
            for name in self.telegram_data.api_data["types"].keys()
        }
        self.ctx = SimpleNamespace(lifespan_context={"telegram_data": self.telegram_data})

    async def test_resolve_type_supports_underscore_insensitive_lookup(self) -> None:
        with patch("server.metrics.logger") as logger_mock:
            logger_mock.ainfo = AsyncMock(return_value=None)
            response = await resolve_type(name="reply_keyboard_markup", ctx=self.ctx)

        self.assertEqual(response.data.name, "ReplyKeyboardMarkup")
        self.assertEqual(
            response.metadata.documentation_url,
            "https://core.telegram.org/bots/api#replykeyboardmarkup",
        )

    async def test_resolve_type_raises_actionable_error(self) -> None:
        with patch("server.metrics.logger") as logger_mock:
            logger_mock.ainfo = AsyncMock(return_value=None)
            with self.assertRaises(TypeNotFoundError) as exc:
                await resolve_type(name="MissingType", ctx=self.ctx)

        self.assertIn("list_types()", str(exc.exception))

    async def test_list_types_returns_envelope(self) -> None:
        with patch("server.metrics.logger") as logger_mock:
            logger_mock.ainfo = AsyncMock(return_value=None)
            response = await list_types(ctx=self.ctx)

        self.assertEqual(response.data.total, 1)
        self.assertEqual(response.data.items, ["ReplyKeyboardMarkup"])


if __name__ == "__main__":
    unittest.main()
