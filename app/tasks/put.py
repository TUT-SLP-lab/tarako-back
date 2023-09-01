import json


def lambda_handler(event, context):
    task_id = event.get("pathParameters", {}).get("task_id")
    body = json.loads(event.get("body", "{}"))

    if task_id is None or not isinstance(task_id, str):
        return {"statusCode": 400, "body": "Bad Request: Invalid task_id"}
    if not body:
        return {"statusCode": 400, "body": "Bad Request: Empty request body"}

    # ここに処理を書く
    example = {
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

    return {"statusCode": 200, "body": json.dumps(example),"headers": {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Credentials": True,
      "Access-Control-Allow-Methods": "POST",
      "Access-Control-Allow-Headers": "Content-Type,X-CSRF-TOKEN",
    }}
