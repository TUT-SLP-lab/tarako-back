import json


def lambda_handler(event, context):
    body = json.loads(event.get("body", "{}"))

    # バリデーション
    if not body:
        return {"statusCode": 400, "body": "Bad Request: Missing request body"}

    # ここに処理を書く

    return {
        "statusCode": 405,
        "body": "Method Not Allowed",
    }
