import json


def lambda_handler(event, context):
    qsp = event.get("queryStringParameters")
    print(qsp)
    # ここに処理を書く
    example = [
        {
            "chat_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            "user_id": "4f73ab32-21bf-47ef-a119-fa024bc2b9cc",
            "timestamp": "2020-01-01T00:00:00+09:00",
            "message": "こんにちは",
            "is_user_message": False,
            "created_at": "2020-01-01T00:00:00+09:00",
            "updated_at": "2020-01-01T00:00:00+09:00",
        }
    ]

    return {
        "statusCode": 200,
        "body": json.dumps(example),
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET",
            "Access-Control-Allow-Headers": "Content-Type,X-CSRF-TOKEN",
        },
    }
