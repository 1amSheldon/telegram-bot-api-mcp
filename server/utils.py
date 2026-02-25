def format_method(method: dict) -> dict:
    return {
        "name": method["name"],
        "description": method.get("description", []),
        "returns": method.get("returns"),
        "parameters": [
            {
                "name": f["name"],
                "types": f["types"],
                "required": f["required"],
                "description": f["description"]
            }
            for f in method.get("fields", [])
        ]
    }


def format_type(type_data: dict) -> dict:
    return {
        "name": type_data["name"],
        "description": type_data.get("description", []),
        "fields": [
            {
                "name": f["name"],
                "types": f["types"],
                "required": f["required"],
                "description": f["description"]
            }
            for f in type_data.get("fields", [])
        ]
    }
