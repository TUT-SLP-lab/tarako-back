import json


def lambda_handler(event, context):
    section_id = event.get("pathParameters", {}).get("section_id")
    body = json.loads(event.get("body", "{}"))

    # バリデーション
    if section_id is None or not isinstance(section_id, int):
        return {"statusCode": 400, "body": "Bad Request: Invalid section_id"}
    if not body:
        return {"statusCode": 400, "body": "Bad Request: Missing request body"}

    # ここに処理を書く
    example = {
        "diary_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "date": "2023-08-31",
        "details": "hoge.fugaの単体テストを作成する",
        "serious": 0,
        "created_at": "2020-01-01T00:00:00+09:00",
        "updated_at": "2020-01-01T00:00:00+09:00",
        "section": {
            "section_id": 0,
            "name": "営業課",
            "created_at": "2020-01-01T00:00:00+09:00",
            "updated_at": "2020-01-01T00:00:00+09:00"
        },
        "user_ids": [
            "4f73ab32-21bf-47ef-a119-fa024bc2b9cc"
        ]
    }

    return {"statusCode": 200, "body": json.dumps(example),"headers": {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Credentials": True,
      "Access-Control-Allow-Methods": "POST",
      "Access-Control-Allow-Headers": "Content-Type,X-CSRF-TOKEN",
    }}
