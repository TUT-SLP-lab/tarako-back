import json


def lambda_handler(event, context):
    user_id = event.get("pathParameters", {}).get("user_id")

    if not user_id:
        return {"statusCode": 400, "body": "Bad Request: Missing user_id"}
    body = json.loads(event.get("body", "{}"))

    # バリデーション
    if user_id and not isinstance(user_id, int):
        return {"statusCode": 400, "body": "Bad Request: Invalid user_id"}
    if not body:
        return {"statusCode": 400, "body": "Bad Request: Missing request body"}

    # ここに処理を書く

    return {
        "statusCode": 405,
        "body": "Method Not Allowed",
    }