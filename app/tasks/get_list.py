import json


def lambda_handler(event, context):
    qsp = event.get("queryStringParameters")
    if qsp:
        user_id = event.get("queryStringParameters", {}).get("user_id")
        from_datetime = event.get("queryStringParameters", {}).get("from")
        to_datetime = event.get("queryStringParameters", {}).get("to")
        status = event.get("queryStringParameters", {}).get("status")
    else:
        user_id = None
        from_datetime = None
        to_datetime = None
        status = None

    # バリデーション
    if user_id and not isinstance(user_id, str):
        return {"statusCode": 400, "body": "Bad Request: Invalid user_id"}
    if from_datetime and not isinstance(from_datetime, str):
        return {"statusCode": 400, "body": "Bad Request: Invalid from_datetime"}
    if to_datetime and not isinstance(to_datetime, str):
        return {"statusCode": 400, "body": "Bad Request: Invalid to_datetime"}

    # ここに処理を書く
    example = [
        {
            "task_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            "assigned_by": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            "title": "単体テスト作成",
            "category": "HR",
            "tags": ["人事", "休暇"],
            "progresses": [
                {"datetime": "2020-01-01T00:00:00+09:00", "percentage": 0},
                {"datetime": "2020-01-02T00:00:00+09:00", "percentage": 50},
                {"datetime": "2020-01-03T00:00:00+09:00", "percentage": 100},
            ],
            "completed": True,
            "serious": 0,
            "details": "hoge.fugaの単体テストを作成する",
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
