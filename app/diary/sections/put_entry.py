import json
from datetime import datetime

from table_utils import (
    DynamoDBError,
    get_item,
    json_dumps,
    put_item,
    section_diary_table,
    section_table,
    user_table,
)


def lambda_handler(event, context):
    ppm = event.get("pathParameters", {})
    if ppm is None:
        return {"statusCode": 400, "body": "Bad Request: Invalid path parameters"}

    section_id = ppm.get("section_id")
    diary_id = ppm.get("diary_id")
    body = event.get("body", "{}")
    try:
        section_id = int(section_id)
    except ValueError:
        return {"statusCode": 400, "body": "Bad Request: section_id is not int"}

    if body is None:
        return {"statusCode": 400, "body": "Bad Request: Invalid body"}
    body = json.loads(body)

    details = body.get("details", None)
    serious = body.get("serious", None)
    user_ids = body.get("user_ids", None)

    # バリデーション
    error_messages = []
    if section_id is None or not isinstance(section_id, int):
        error_messages.append("Bad Request: Invalid section_id")
    if diary_id is None or not isinstance(diary_id, str):
        error_messages.append("Bad Request: Invalid diary_id")
    if details is None or not isinstance(details, str):
        error_messages.append("Bad Request: Invalid details")
    if serious is None or not isinstance(serious, int):
        error_messages.append("Bad Request: Invalid serious")
    if user_ids is None or not isinstance(user_ids, list):
        error_messages.append("Bad Request: Invalid user_ids")
    if len(error_messages) > 0:
        return {
            "statusCode": 400,
            "body": "\n".join(error_messages),
        }

    # ユーザーの存在確認
    try:
        for user_id in user_ids:
            get_item(user_table, "user_id", user_id)
        # sectionの取得
        section = get_item(section_table, "section_id", section_id)
        # get diary
        diary = get_item(section_diary_table, "diary_id", diary_id)

        # section validation
        if section["section_id"] != section_id:
            return {
                "statusCode": 400,
                "body": "Bad Request: Invalid section_id",
            }
        # update
        UpdateExpression = "set details=:d, serious=:s, user_ids=:u, updated_at=:upd"
        ExpressionAttributeValues = {
            ":d": details,
            ":s": serious,
            ":u": user_ids,
            ":upd": datetime.now().isoformat(),
        }
        diary = put_item(
            section_diary_table,
            "diary_id",
            diary_id,
            UpdateExpression,
            ExpressionAttributeValues,
        )
    except DynamoDBError as e:
        return {"statusCode": 500, "body": f"Failed: {e}"}
    except IndexError as e:
        return {"statusCode": 404, "body": f"Failed: {e}"}

    return {
        "statusCode": 200,
        "body": json_dumps(diary),
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "PUT",
            "Access-Control-Allow-Headers": "Content-Type,X-CSRF-TOKEN",
        },
    }
