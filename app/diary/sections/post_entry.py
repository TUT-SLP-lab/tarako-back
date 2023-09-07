import json
import uuid
from datetime import datetime

from boto3.dynamodb.conditions import Key
from responses import post_response
from table_utils import (
    DynamoDBError,
    get_items,
    json_dumps,
    post_item,
    section_diary_table,
    user_table,
)
from validation import (
    validate_date_not_none,
    validate_message_not_none,
    validate_section_id_not_none,
)


def lambda_handler(event, context):
    ppm = event.get("pathParameters", {})

    # validation
    if ppm is None:
        return post_response(400, "Bad Request: Invalid path parameters")
    section_id = ppm.get("section_id")

    # body balidation
    body = event.get("body", "{}")
    if body is None:
        return post_response(400, "Bad Request: Invalid body")

    body = json.loads(body)
    date = body.get("date", None)
    message = body.get("message", None)

    # バリデーション
    is_valid, err_msg = validate_section_id_not_none(section_id)
    if not is_valid:
        return post_response(400, f"Bad Request: {err_msg}")
    is_valid, err_msg = validate_date_not_none(date)
    if not is_valid:
        return post_response(400, f"Bad Request: {err_msg}")
    is_valid, err_msg = validate_message_not_none(message)
    if not is_valid:
        return post_response(400, f"Bad Request: {err_msg}")

    section_id = int(section_id)
    print(date, message)

    try:
        user_list = get_items(user_table, "SectionIndex", Key("section_id").eq(section_id))
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
        return post_response(500, f"Internal Server Error: DynamoDB Error: {e}")
    except IndexError as e:
        return post_response(404, f"Not Found: {e}")
    return post_response(200, json_dumps(item))
