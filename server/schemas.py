from typing import Generic, TypeVar

from pydantic import BaseModel, Field


class ApiMetadata(BaseModel):
    """Metadata describing the source of returned Telegram Bot API data."""

    api_version: str = Field(description="Telegram Bot API version string with release date.")
    documentation_url: str | None = Field(
        default=None,
        description="Optional canonical documentation URL for the current entity.",
    )


TData = TypeVar("TData")


class Response(BaseModel, Generic[TData]):
    """Canonical envelope that separates payload data from metadata."""

    data: TData = Field(description="Main payload returned by the tool.")
    metadata: ApiMetadata = Field(description="Metadata about payload origin and docs.")


class Parameter(BaseModel):
    """Method or type field descriptor from Telegram Bot API specs."""

    name: str = Field(description="Parameter or field name.")
    types: list[str] = Field(description="Accepted Telegram Bot API types for this parameter.")
    required: bool = Field(description="Whether this parameter is required.")
    description: str = Field(description="Human-readable semantic description.")


class MethodDetail(BaseModel):
    """Canonical details for a single Telegram Bot API method."""

    name: str = Field(description="Official Telegram Bot API method name.")
    description: list[str] = Field(description="Method description paragraphs from the Bot API spec.")
    returns: list[str] = Field(description="Declared return type(s) from the Bot API spec.")
    parameters: list[Parameter] = Field(description="Method parameters accepted by this API method.")


class TypeDetail(BaseModel):
    """Canonical details for a single Telegram Bot API type."""

    name: str = Field(description="Official Telegram Bot API type name.")
    description: list[str] = Field(description="Type description paragraphs from the Bot API spec.")
    fields: list[Parameter] = Field(description="Fields declared on this Telegram Bot API type.")


class MethodList(BaseModel):
    """Paginated list of method names for discovery."""

    items: list[str] = Field(description="Method names in the requested page window.")
    total: int = Field(description="Total number of matching methods before pagination.")
    limit: int = Field(description="Maximum number of items requested in this page.")
    offset: int = Field(description="Zero-based offset used to build this page.")
    filter: str | None = Field(
        default=None,
        description="Optional keyword filter used to narrow methods.",
    )


class TypeList(BaseModel):
    """List of Telegram Bot API type names for discovery."""

    items: list[str] = Field(description="All available Telegram Bot API type names.")
    total: int = Field(description="Total number of available types.")


class FindResult(BaseModel):
    """Result of natural-language search over Telegram Bot API entities."""

    methods: list[str] = Field(description="Method names relevant to the query.")
    types: list[str] = Field(description="Type names relevant to the query.")


class VersionInfo(BaseModel):
    """Version payload for the Bot API."""

    version: str = Field(description="Current Telegram Bot API version string.")


class ChangelogUpdate(BaseModel):
    """Single parsed update item from Telegram Bot API changelog."""

    date: str = Field(description="Release date label from the changelog heading.")
    version: str = Field(description="Bot API version label, for example 'Bot API 9.1'.")
    changes: list[str] = Field(description="Plain-text list items describing all changes in this release block.")


class ChangelogResult(BaseModel):
    """Recent parsed changelog updates loaded during startup."""

    updates: list[ChangelogUpdate] = Field(description="Latest changelog updates, newest first.")
