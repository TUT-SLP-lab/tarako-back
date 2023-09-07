import json

from responses import post_response


def lambda_handler(event, context):
    body = json.loads(event.get("body", "{}"))

    # バリデーション
    if not body:
        return post_response(400, "Bad Request: Invalid body")

    # ここに処理を書く

    return post_response(405, "Method Not Allowed")
