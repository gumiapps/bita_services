
from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema

metrics_monitor_schema = extend_schema(
    summary="Get Monitoring Metrics",
    description="Returns metrics including total requests, success/failure rates, request counts by endpoint, and client.",
    responses={
        200: OpenApiResponse(
            response={
                "type": "object",
                "properties": {
                    "total_requests": {"type": "integer", "example": 250},
                    "success_count": {"type": "integer", "example": 200},
                    "success_rate": {"type": "number", "example": 0.8},
                    "failure_count": {"type": "integer", "example": 50},
                    "failure_rate": {"type": "number", "example": 0.2},
                    "request_count_by_endpoint": {
                        "type": "object",
                        "properties": {
                            "email": {"type": "integer", "example": 120},
                            "sms": {"type": "integer", "example": 80},
                            "in-app": {"type": "integer", "example": 50},
                        },
                    },
                    "request_count_by_client": {
                        "type": "object",
                        "additionalProperties": {"type": "integer", "example": 150},
                    },
                },
            }
        ),
        500: OpenApiResponse(description="Internal server error."),
    },
)


api_key_list_schema = extend_schema(
    summary="List API Keys",
    description="Fetches info on API keys.",
    responses={
        200: OpenApiResponse(
            response={
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {
                            "type": "string",
                            "example": "uPtZ5RaD.sha512$$....."
                        },
                        "name": {
                            "type": "string",
                            "example": "auth-dev"
                        },
                        "prefix": {
                            "type": "string",
                            "example": "uPtZ5RaD"
                        },
                        "created": {
                            "type": "string",
                            "format": "date-time",
                            "example": "2025-01-15T13:39:28.489015Z"
                        },
                        "revoked": {
                            "type": "boolean",
                            "example": "false"
                        }
                    },                },
            }
        ),
        403: OpenApiResponse(description="Permission denied."),
    },
)

