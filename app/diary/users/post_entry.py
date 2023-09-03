import json
import uuid
from datetime import datetime

from table_utils import json_dumps, user_diary_table


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

    # TODO from user db
    user_list = [
        "4f73ab32-21bf-47ef-a119-fa024bc2b9cc",
        "595c060d-8417-4ac8-bcb5-c8e733dc64e0",
        "e08bf311-b1bc-4a38-bac1-374c3ede7203",
    ]
    if user_id not in user_list:
        return {"statusCode": 400, "body": "Bad Request: user_id not found"}

    # get from task
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
    response = user_diary_table.put_item(Item=item)
    if response["ResponseMetadata"]["HTTPStatusCode"] != 200:
        return {"statusCode": 500, "body": "Internal Server Error"}
    response = user_diary_table.get_item(Key={"diary_id": diary_id})
    return {
        "statusCode": 200,
        "body": json_dumps(response["Item"]),
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST",
            "Access-Control-Allow-Headers": "Content-Type,X-CSRF-TOKEN",
        },
    }
