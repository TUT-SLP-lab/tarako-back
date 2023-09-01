import json


def lambda_handler(event, context):
    # ここに処理を書く
    example = [
        {
            "section_id": 0,
            "name": "営業課",
            "created_at": "2020-01-01T00:00:00+09:00",
            "updated_at": "2020-01-01T00:00:00+09:00",
        },
        {
            "section_id": 0,
            "name": "管理課",
            "created_at": "2020-01-01T00:00:00+09:00",
            "updated_at": "2020-01-01T00:00:00+09:00",
        },
    ]

    return {"statusCode": 200, "body": json.dumps(example),"headers": {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Credentials": True,
      "Access-Control-Allow-Methods": "POST",
      "Access-Control-Allow-Headers": "Content-Type,X-CSRF-TOKEN",
    }}
