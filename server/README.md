# Telegram Bot API MCP Server

An MCP (Model Context Protocol) server that provides access to Telegram Bot API documentation.

## Features

- **resolve_method(name)**: Get detailed information about a Bot API method
- **list_methods()**: List all available Bot API methods
- **resolve_type(name)**: Get detailed information about a Bot API type
- **list_types()**: List all available Bot API types
- **find(query)**: Search for methods and types by query string

## Configuration

Copy `settings.example.toml` to `settings.toml` and adjust values as needed.

## Run

From the repository root:

```bash
uv run python -m server
```

## Data Source

The server fetches the latest Bot API specification from `app.api_url`. If the request fails, it loads the
fallback data from `data/botapi.json` (relative to the repository root).

## Method Name Formats

Method names are case-insensitive and accept multiple formats:

- `getUpdates` (camelCase)
- `getupdates` (lowercase)
- `get_updates` (snake_case)

## Examples

### Resolve a method

```python
await resolve_method("getUpdates")
await resolve_method("getupdates")
await resolve_method("get_updates")
```

### Search for methods and types

```python
await find("message")
await find("inline keyboard")
```

### Get type information

```python
await resolve_type("InlineKeyboardButton")
await resolve_type("inlinekeyboardbutton")
```

