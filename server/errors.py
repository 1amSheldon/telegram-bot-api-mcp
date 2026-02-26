class MethodNotFoundError(ValueError):
    """Raised when a Telegram Bot API method cannot be resolved."""

    def __init__(self, name: str, suggestions: list[str] | None = None):
        suggestion_text = ""
        if suggestions:
            suggestion_text = f" Did you mean: {', '.join(suggestions)}?"
        message = (
            f"Method '{name}' not found; try list_methods(filter='passport')."
            f"{suggestion_text}"
        )
        super().__init__(message)


class TypeNotFoundError(ValueError):
    """Raised when a Telegram Bot API type cannot be resolved."""

    def __init__(self, name: str):
        message = (
            f"Type '{name}' not found; try list_types() and then resolve_type() with an exact name."
        )
        super().__init__(message)
