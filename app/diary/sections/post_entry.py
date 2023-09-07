import json
import uuid
from datetime import datetime

from boto3.dynamodb.conditions import Key
from chat_util import gen_section_diary_data
from responses import post_response
from table_utils import (
    DynamoDBError,
    get_items,
    json_dumps,
    post_item,
    section_diary_table,
    user_diary_table,
    user_table,
)
from validation import validate_date_not_none, validate_section_id_not_none


def lambda_handler(event, context):
    ppm = event.get("pathParameters", {})

    # validation
    if ppm is None:
        return post_response(400, "Bad Request: Invalid path parameters")
    section_id = ppm.get("section_id", None)

    # body balidation
    body = event.get("body", "{}")
    if body is None:
        return post_response(400, "Bad Request: Invalid body")

    body = json.loads(body)
    date = body.get("date", None)

    # バリデーション
    is_valid, err_msg = validate_section_id_not_none(section_id)
    if not is_valid:
        return post_response(400, f"Bad Request: {err_msg}")
    is_valid, err_msg = validate_date_not_none(date)
    if not is_valid:
        return post_response(400, f"Bad Request: {err_msg}")

    section_id = int(section_id)

    # SectionのUser 日報を取得

    try:
        # get section user
        expr = Key("section_id").eq(section_id)
        user_list = get_items(user_table, "SectionIndex", expr)
        user_ids = [user["user_id"] for user in user_list]

        # get user diaries
        user_diary_list = []
        for user_id in user_ids:
            expr = Key("user_id").eq(user_id) & Key("date").eq(date)
            user_diaries = get_items(user_diary_table, "UserDateIndex", expr)
            user_diary_list += user_diaries

        if len(user_diary_list) == 0:
            return post_response(404, "The specified resource was not found.")

        # calc serious
        section_serious = sum([int(user_diary["serious"]) for user_diary in user_diary_list])

        gpt_section_diary = gen_section_diary_data(user_diary_list)

        diary_id = str(uuid.uuid4())
        # Update 処理
        item = {
            "diary_id": diary_id,
            "date": date,
            "details": gpt_section_diary.get("details", ""),
            "ai_analysis": gpt_section_diary.get("ai_analysis", ""),
            "serious": section_serious,
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
