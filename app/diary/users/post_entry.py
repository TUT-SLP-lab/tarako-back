import json
import uuid
from datetime import datetime

from table_utils import (
    DynamoDBError,
    get_item,
    json_dumps,
    post_item,
    user_diary_table,
    user_table,
)


def lambda_handler(event, context):
    path_params = event.get("pathParameters", {})
    if path_params is None:
        return {"statusCode": 400, "body": "Bad Request: Missing path parameters"}
    user_id = path_params.get("user_id", None)

    body = event.get("body", {})
    if body is None:
        return {"statusCode": 400, "body": "Bad Request: Missing request body"}
    body = json.loads(body)
    date = body.get("date", None)
    message = body.get("message", None)

    # バリデーション
    if user_id is None or not isinstance(user_id, str):
        return {"statusCode": 400, "body": "Bad Request: Invalid user_id"}
    if date is None or not isinstance(date, str):
        return {"statusCode": 400, "body": "Bad Request: Invalid date"}
    if message is None or not isinstance(message, str):
        return {"statusCode": 400, "body": "Bad Request: Invalid message"}
    try:
        datetime.fromisoformat(date)
    except ValueError:
        return {"statusCode": 400, "body": "Bad Request: Invalid date format"}

    # user 存在確認
    try:
        get_item(user_table, "user_id", user_id)
        # TODO get from task

        # TODO send message to ChatGPT
        diary_id = str(uuid.uuid4())
        item = {
            "diary_id": diary_id,
            "section_id": 1,
            "date": date,
            "details": "hogehoge",
            "serious": 0,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "user_id": user_id,
            "task_ids": ["aaaa", "aaa"],
        }
        user_diary = post_item(user_diary_table, item)

    except DynamoDBError as e:
        return {"statusCode": 500, "body": f"Internal Server Error: {e}"}
    except IndexError as e:
        return {"statusCode": 404, "body": f"Not Found: {e}"}

    return {
        "statusCode": 200,
        "body": json_dumps(user_diary),
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST",
            "Access-Control-Allow-Headers": "Content-Type,X-CSRF-TOKEN",
        },
    }
