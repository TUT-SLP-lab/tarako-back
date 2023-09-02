import json


def lambda_handler(event, context):
    section_id = event.get("pathParameters", {}).get("section_id")

    if not section_id:
        return {"statusCode": 400, "body": "Bad Request: Missing section_id"}
    body = json.loads(event.get("body", "{}"))

    # バリデーション
    if section_id and not isinstance(section_id, int):
        return {"statusCode": 400, "body": "Bad Request: Invalid section_id"}
    if not body:
        return {"statusCode": 400, "body": "Bad Request: Missing request body"}

    # ここに処理を書く

    return {
        "statusCode": 405,
        "body": "Method Not Allowed",
    }