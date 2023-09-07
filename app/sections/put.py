import json

from responses import put_response


def lambda_handler(event, context):
    section_id = event.get("pathParameters", {}).get("section_id")

    if not section_id:
        return put_response(400, "Bad Request: Invalid path parameters")
    body = json.loads(event.get("body", "{}"))

    # バリデーション
    if section_id and not isinstance(section_id, int):
        return put_response(400, "Bad Request: Invalid section_id")
    if not body:
        return put_response(400, "Bad Request: Invalid body")

    # ここに処理を書く
    return put_response(405, "Method Not Allowed")
