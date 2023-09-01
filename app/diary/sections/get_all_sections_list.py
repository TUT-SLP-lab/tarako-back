import json


def lambda_handler(event, context):
    qsp = event.get("queryStringParameters")
    if qsp:
        from_date = event.get("queryStringParameters", {}).get("from_date")
        to_date = event.get("queryStringParameters", {}).get("to_date")
    else:
        from_date = None
        to_date = None

    if from_date is not None and not isinstance(from_date, str):
        return {"statusCode": 400, "body": "Bad Request: Invalid from_date"}
    if to_date is not None and not isinstance(to_date, str):
        return {"statusCode": 400, "body": "Bad Request: Invalid to_date"}

    # ここに処理を書く
    example = [
        {
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
    ]

    return {"statusCode": 200, "body": json.dumps(example),"headers": {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Credentials": True,
      "Access-Control-Allow-Methods": "POST",
      "Access-Control-Allow-Headers": "Content-Type,X-CSRF-TOKEN",
    }}
