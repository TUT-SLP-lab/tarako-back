import json


def lambda_handler(event, context):
    user_id = event.get("pathParameters", {}).get("user_id")
    body = json.loads(event.get("body", "{}"))

    if user_id is None or not isinstance(user_id, str):
        return {"statusCode": 400, "body": "Bad Request: Invalid user_id"}
    if not body:
        return {"statusCode": 400, "body": "Bad Request: Empty request body"}

    # ここに処理を書く
    example = {
        "diary_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "date": "2023-08-31",
        "details": "hoge.fugaの単体テストを作成する",
        "serious": 0,
        "task_ids": ["3fa85f64-5717-4562-b3fc-2c963f66afa6"],
        "created_at": "2020-01-01T00:00:00+09:00",
        "updated_at": "2020-01-01T00:00:00+09:00",
        "user_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    }

    return {"statusCode": 200, "body": json.dumps(example)}
