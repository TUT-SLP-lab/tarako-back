import json
import uuid
from datetime import datetime

from boto3.dynamodb.conditions import Key
from table_utils import (DynamoDBError, get_item, get_items, json_dumps,
                         post_item, section_diary_table, section_table,
                         user_table)


def lambda_handler(event, context):
    ppm = event.get("pathParameters", {})

    # validation
    if ppm is None:
        return {"statusCode": 400, "body": "Bad Request: Invalid path parameters"}
    section_id = ppm.get("section_id")
    try:
        section_id = int(section_id)
    except ValueError:
        return {"statusCode": 400, "body": "Bad Request: section_id is not int"}

    # body balidation
    body = event.get("body", "{}")
    if body is None:
        return {"statusCode": 400, "body": "Bad Request: Invalid body"}

    body = json.loads(body)
    date = body.get("date", None)
    message = body.get("message", None)

    # バリデーション
    if section_id is None or not isinstance(section_id, int):
        return {"statusCode": 400, "body": "Bad Request: Invalid section_id"}
    if date is None or not isinstance(date, str):
        return {"statusCode": 400, "body": "Bad Request: Invalid date"}
    if message is None or not isinstance(message, str):
        return {"statusCode": 400, "body": "Bad Request: Invalid message"}
    try:
        datetime.fromisoformat(date)
    except ValueError:
        return {"statusCode": 400, "body": "Bad Request: Invalid date format"}

    print(date, message)

    try:
        user_list = get_items(
            user_table, "SectionIndex", Key("section_id").eq(section_id)
        )
        user_ids = [item["user_id"] for item in user_list]

        # TODO Chat GPTに聞く

        diary_id = str(uuid.uuid4())
        # Update 処理
        item = {
            "diary_id": diary_id,
            "date": date,
            "details": "hoge.fugaの単体テストを作成する",
            "serious": 0,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "section_id": section_id,
            "user_ids": user_ids,
        }

        item = post_item(section_diary_table, item)

    except DynamoDBError as e:
        return {"statusCode": 500, "body": f"Failed: {e}"}
    except IndexError as e:
        return {"statusCode": 404, "body": f"Failed: {e}"}
    return {
        "statusCode": 200,
        "body": json_dumps(item),
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST",
            "Access-Control-Allow-Headers": "Content-Type,X-CSRF-TOKEN",
        },
    }
