# Telegram Bot API MCP Server

An MCP (Model Context Protocol) server that provides access to Telegram Bot API documentation and methods. 
This server enables AI assistants to interact with Telegram Bot API documentation programmatically.

**Bot API Data Source**: This project uses Telegram Bot API specifications from [telegram-bot-api-spec](https://github.com/PaulSonOfLars/telegram-bot-api-spec)

## Requirements

- **Python**: >=3.13
- **Stack**: FastMCP

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd telegram-bot-api-mcp

# Install dependencies
uv sync
```

## Configuration

Copy `settings.example.toml` to `settings.toml` and configure as needed.

## Available Tools

### Methods Tools
- **`resolve_method`** - Return canonical details for a Bot API method by name (parameters, return type, and semantics)
- **`list_methods`** - List all Bot API method names for discovery; use before `resolve_method` when the exact method is unknown

### Types Tools  
- **`resolve_type`** - Return canonical details for a Bot API type by name (fields, field types, and constraints)
- **`list_types`** - List all Bot API type names for discovery; use before `resolve_type` when the exact type is unknown

### Search Tools
- **`find`** - Search methods and types by natural-language query (e.g., "edit message"); then resolve returned names with `resolve_method`/`resolve_type`

### Other Tools
- **`get_version`** - Return the current Telegram Bot API version for version-sensitive guidance
- **`get_changelog_link`** - Return the URL of the latest Bot API changelog for recent changes and migration context

## Usage

Start the MCP server:

```bash
python -m server
```

The server will load the latest Telegram Bot API documentation and provide tools for accessing methods, types, and searching through the API reference.

## Development

This project uses:
- **Python 3.13**
- **FastMCP** for MCP server implementation
- **structlog** for structured logging
- **httpx** for HTTP requests
- **uvicorn** for ASGI server

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.