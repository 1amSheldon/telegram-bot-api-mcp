from typing import TypeVar

from server.schemas import ApiMetadata, MethodDetail, Parameter, Response, TypeDetail


TData = TypeVar("TData")


def build_metadata(
    *,
    version: str,
    documentation_url: str | None = None,
) -> ApiMetadata:
    return ApiMetadata(
        api_version=version,
        documentation_url=documentation_url,
    )


def build_response(data: TData, metadata: ApiMetadata) -> Response[TData]:
    return Response[TData](
        data=data,
        metadata=metadata,
    )


def format_method(method: dict) -> MethodDetail:
    return MethodDetail(
        name=method["name"],
        description=method.get("description", []),
        returns=method.get("returns", []),
        parameters=[
            Parameter(
                name=field["name"],
                types=field["types"],
                required=field["required"],
                description=field["description"],
            )
            for field in method.get("fields", [])
        ],
    )


def format_type(type_data: dict) -> TypeDetail:
    return TypeDetail(
        name=type_data["name"],
        description=type_data.get("description", []),
        fields=[
            Parameter(
                name=field["name"],
                types=field["types"],
                required=field["required"],
                description=field["description"],
            )
            for field in type_data.get("fields", [])
        ],
    )
