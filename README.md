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
- **`resolve_method`** - Resolve a Telegram Bot API method by name and get detailed information including parameters, return types, and descriptions
- **`list_methods`** - List all available Telegram Bot API methods

### Types Tools  
- **`resolve_type`** - Resolve a Telegram Bot API type by name and get detailed information including fields and their types
- **`list_types`** - List all available Telegram Bot API types

### Search Tools
- **`find`** - Search for methods and types by query string with fuzzy matching

### Other Tools
- **`get_version`** - Get current Telegram Bot API version
- **`get_changelog_link`** - Get link to the most recent changelog

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