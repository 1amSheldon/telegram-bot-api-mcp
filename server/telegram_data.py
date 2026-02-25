import json
from pathlib import Path
from typing import Any

import httpx
import structlog
from structlog.typing import FilteringBoundLogger

logger: FilteringBoundLogger = structlog.get_logger()

class TelegramData:
    def __init__(
            self,
            api_url: str | None = None,
    ):
        self.api_url = api_url
        self.api_data: dict[str, Any] = {}
        self.bot_api_methods: dict[str, str] = {}
        self.bot_api_types: dict[str, str] = {}
        self.search_index: dict[str, list[dict[str, str]]] = {}
        self.fallback_path = Path(__file__).resolve().parent.parent.joinpath("data", "botapi.json")
        self.version = ""
        self.changelog_link = ""
    
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
        
        self.bot_api_methods = {
            name.lower(): name for name in self.api_data.get("methods", {}).keys()
        }
        self.bot_api_types = {
            name.lower(): name for name in self.api_data.get("types", {}).keys()
        }
        self.search_index = self.build_search_index()

        version_text = f"{self.api_data['version']} ({self.api_data['release_date']})"
        self.version = version_text

        self.changelog_link = self.api_data["changelog"]
    
    def build_search_index(self) -> dict[str, list[dict[str, str]]]:
        search_index = {}
        
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
