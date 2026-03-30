import json
import re
import time
from asyncio import Lock
from html import unescape
from pathlib import Path
from typing import Any

import httpx
import structlog
from structlog.typing import FilteringBoundLogger

logger: FilteringBoundLogger = structlog.get_logger()

CHANGELOG_PAGE_URL = "https://core.telegram.org/bots/api-changelog"
MAX_RECENT_CHANGELOG_UPDATES = 3

class TelegramData:
    def __init__(
            self,
            api_url: str | None = None,
            refresh_ttl_seconds: int = 900,
    ):
        self.api_url = api_url
        self.refresh_ttl_seconds = max(refresh_ttl_seconds, 0)
        self.api_data: dict[str, Any] = {}
        self.normalized_method_names: dict[str, str] = {}
        self.normalized_type_names: dict[str, str] = {}
        self.method_search_text: dict[str, str] = {}
        self.search_index: dict[str, list[dict[str, str]]] = {}
        self.fallback_path = Path(__file__).resolve().parent.parent.joinpath("data", "botapi.json")
        self.current_version = ""
        self.recent_changelog: list[dict[str, Any]] = []
        self._loaded_monotonic: float = 0.0
        self._refresh_lock = Lock()

    @staticmethod
    def normalize_name(name: str) -> str:
        return name.lower().replace("_", "")

    def resolve_method_name(self, name: str) -> str | None:
        return self.normalized_method_names.get(self.normalize_name(name))

    def resolve_type_name(self, name: str) -> str | None:
        return self.normalized_type_names.get(self.normalize_name(name))

    def list_method_names(self, filter_keyword: str | None = None) -> list[str]:
        methods = list(self.api_data.get("methods", {}).keys())
        if not filter_keyword:
            return methods

        keyword = filter_keyword.lower().strip()
        if not keyword:
            return methods

        return [
            name
            for name in methods
            if keyword in self.method_search_text.get(name, "")
        ]
    
    async def load_api_data(self) -> None:
        try:
            if not self.api_url:
                raise ValueError("API URL is not specified")

            await logger.ainfo(f"Fetching API data from {self.api_url}")
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(self.api_url)
                
                if response.status_code == 200:
                    self.api_data = response.json()
                    await logger.ainfo("Successfully fetched API data from remote source")
                else:
                    raise httpx.HTTPStatusError(
                        f"HTTP {response.status_code}",
                        request=response.request,
                        response=response,
                    )
        except Exception as ex:
            await logger.aexception(
                f"Failed to fetch remote API data: {ex.__class__.__name__}: {ex}"
            )
            await logger.ainfo(f"Loading fallback API data from {self.fallback_path}")
            
            with open(self.fallback_path, "rt", encoding="utf-8") as file:
                self.api_data = json.load(file)
            
            await logger.ainfo("Successfully loaded fallback API data")
        
        self.normalized_method_names = {
            self.normalize_name(name): name
            for name in self.api_data.get("methods", {}).keys()
        }
        self.normalized_type_names = {
            self.normalize_name(name): name
            for name in self.api_data.get("types", {}).keys()
        }
        self.method_search_text = {
            method_name: " ".join(
                [method_name.lower()] + method_data.get("description", [])
            ).lower()
            for method_name, method_data in self.api_data.get("methods", {}).items()
        }
        self.search_index = self.__build_search_index()

        version_text = f"{self.api_data['version']} ({self.api_data['release_date']})"
        self.current_version = version_text
        self._loaded_monotonic = time.monotonic()

        await self.__load_recent_changelog()

    async def ensure_fresh(self) -> None:
        if not self.api_data:
            await self.load_api_data()
            return

        if self.refresh_ttl_seconds <= 0:
            return

        now = time.monotonic()
        if now - self._loaded_monotonic < self.refresh_ttl_seconds:
            return

        async with self._refresh_lock:
            now = time.monotonic()
            if self.api_data and now - self._loaded_monotonic < self.refresh_ttl_seconds:
                return

            await logger.ainfo(
                "Refreshing Telegram Bot API data because refresh TTL expired",
                refresh_ttl_seconds=self.refresh_ttl_seconds,
            )
            await self.load_api_data()

    async def __load_recent_changelog(self) -> None:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(CHANGELOG_PAGE_URL)
                response.raise_for_status()
                self.recent_changelog = self.__parse_recent_changelog(response.text)
        except Exception as ex:
            await logger.aexception(
                f"Failed to fetch/parse changelog page: {ex.__class__.__name__}: {ex}"
            )
            self.recent_changelog = []

    @staticmethod
    def __plain_text(value: str) -> str:
        without_tags = re.sub(r"<[^>]+>", "", value)
        return " ".join(unescape(without_tags).split())

    def __parse_recent_changelog(self, html: str) -> list[dict[str, Any]]:
        updates: list[dict[str, Any]] = []
        release_pattern = re.compile(
            r"<h4[^>]*>.*?</a>(?P<date>[^<]+)</h4>(?P<body>.*?)(?=<h4[^>]*>|\Z)",
            re.IGNORECASE | re.DOTALL,
        )

        for match in release_pattern.finditer(html):
            date = self.__plain_text(match.group("date"))
            body = match.group("body")

            version_match = re.search(
                r"<p>\s*<strong>\s*(Bot API\s+[^<]+?)\s*</strong>\s*</p>",
                body,
                re.IGNORECASE | re.DOTALL,
            )
            if not version_match:
                continue

            version = self.__plain_text(version_match.group(1))
            changes = [
                self.__plain_text(item)
                for item in re.findall(r"<li>(.*?)</li>", body, re.IGNORECASE | re.DOTALL)
            ]

            if not changes:
                continue

            updates.append(
                {
                    "date": date,
                    "version": version,
                    "changes": changes,
                }
            )
            if len(updates) >= MAX_RECENT_CHANGELOG_UPDATES:
                break

        return updates
    
    def __build_search_index(self) -> dict[str, list[dict[str, str]]]:
        search_index = dict()
        
        for method_name, method_data in self.api_data.get("methods", {}).items():
            name_lower = method_name.lower()
            desc_text = " ".join(method_data.get("description", [])).lower()
            
            words = set(name_lower.split("_"))
            for word in desc_text.split():
                if len(word) > 2:
                    words.add(word.lower())
            
            for word in words:
                if word not in search_index:
                    search_index[word] = []
                search_index[word].append({"type": "method", "name": method_name})
        
        for type_name, type_data in self.api_data.get("types", {}).items():
            name_lower = type_name.lower()
            desc_text = " ".join(type_data.get("description", [])).lower()
            
            words = {name_lower}
            for word in desc_text.split():
                if len(word) > 2:
                    words.add(word.lower())
            
            for word in words:
                if word not in search_index:
                    search_index[word] = []
                search_index[word].append({"type": "type", "name": type_name})

        return search_index
