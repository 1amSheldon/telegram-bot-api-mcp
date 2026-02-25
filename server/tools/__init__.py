from . import methods, search, types, other

def get_tools() -> list:
    return [
        methods.resolve_method,
        methods.list_methods,
        types.resolve_type,
        types.list_types,
        search.find,
        other.get_version,
        other.get_changelog_link,
    ]
