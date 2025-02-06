from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema

SINGLE_SMS_REQUEST_SCHEMA = {
    "application/json": {
        "example": {
            "phone": "251912345678",
            "message": "Hello, this is a test message!",
        }
    }
}

SINGLE_SMS_RESPONSES = {
    200: OpenApiResponse(
        description="SMS sent successfully",
        examples=[
            OpenApiExample(
                "Success Response",
                value={
                    "status": "SMS sent successfully",
                    "data": {
                        "message_id": "12345",
                        "status": "queued",
                    },
                },
            ),
        ],
    ),
    400: OpenApiResponse(
        description="Bad Request",
        examples=[
            OpenApiExample(
                "Error Response",
                value={
                    "error": "Missing required fields (phone, message)",
                },
            ),
        ],
    ),
    429: OpenApiResponse(
        description="Too Many Requests",
        examples=[
            OpenApiExample(
                "Error Response",
                value={
                    "error": "Request was throttled. Expected available in 60 seconds.",
                },
            ),
        ],
    ),
    500: OpenApiResponse(
        description="Internal Server Error",
        examples=[
            OpenApiExample(
                "Error Response",
                value={
                    "error": "Failed to send SMS: 401 Unauthorized",
                },
            ),
        ],
    ),
}

BULK_SMS_REQUEST_SCHEMA = {
    "application/json": {
        "example": {
            "contacts": [
                {
                    "fname": "John",
                    "lname": "Doe",
                    "phone_number": "251912345678"
                },
                {
                    "fname": "Jane",
                    "lname": "Doe",
                    "phone_number": "251987654321"
                }
            ],
            "sender_id": "GeezSMS",
            "msg": "Hello [[fname]] [[lname]], this is a test message!",
            "notify_url": "https://your-notify-url.com"
        }
    }
}

BULK_SMS_RESPONSES = {
    200: OpenApiResponse(
        description="Bulk SMS sent successfully",
        examples=[
            OpenApiExample(
                "Success Response",
                value={
                    "status": "Bulk SMS sent successfully",
                    "data": {
                        "message_id": "12345",
                        "status": "queued",
                    },
                },
            ),
        ],
    ),
    400: OpenApiResponse(
        description="Bad Request",
        examples=[
            OpenApiExample(
                "Error Response",
                value={
                    "error": "Missing required fields (contacts, msg, notify_url)",
                },
            ),
        ],
    ),
    500: OpenApiResponse(
        description="Internal Server Error",
        examples=[
            OpenApiExample(
                "Error Response",
                value={
                    "error": "Failed to send bulk SMS: 401 Unauthorized",
                },
            ),
        ],
    ),
}

# Extend Schema Decorators
single_sms_schema = extend_schema(
    request=SINGLE_SMS_REQUEST_SCHEMA,
    responses=SINGLE_SMS_RESPONSES,
    description="Send a single SMS using the GeezSMS API.",
    summary="Send SMS",
    tags=["SMS"],
)

bulk_sms_schema = extend_schema(
    request=BULK_SMS_REQUEST_SCHEMA,
    responses=BULK_SMS_RESPONSES,
    description="Send bulk SMS.",
    summary="Send Bulk SMS",
    tags=["SMS"],
)
