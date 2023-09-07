import json

from responses import put_response


def lambda_handler(event, context):
    user_id = event.get("pathParameters", {}).get("user_id")

    if not user_id:
        return put_response(400, "Bad Request: Invalid path parameters")
    body = json.loads(event.get("body", "{}"))

    # バリデーション
    if user_id and not isinstance(user_id, int):
        return put_response(400, "Bad Request: Invalid user_id")
    if not body:
        return put_response(400, "Bad Request: Invalid body")

    # ここに処理を書く

    return put_response(405, "Method Not Allowed")
