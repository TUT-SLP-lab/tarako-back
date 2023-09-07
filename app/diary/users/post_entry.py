import datetime
import json
import traceback
import uuid

from boto3.dynamodb.conditions import Key
from chat_util import gen_user_diary_data
from responses import post_response
from table_utils import (
    DynamoDBError,
    get_item,
    get_items,
    json_dumps,
    post_item,
    task_table,
    user_diary_table,
    user_table,
)
from validation import (
    validate_date,
    validate_message_not_none,
    validate_user_id_not_none,
)


def lambda_handler(event, context):
    path_params = event.get("pathParameters", {})
    if path_params is None:
        return post_response(400, "Bad Request: Invalid path parameters")
    user_id = path_params.get("user_id", None)

    body = event.get("body", {})
    if body is None:
        return post_response(400, "Bad Request: Invalid body")
    body = json.loads(body)
    date = body.get("date", None)
    message = body.get("message", None)

    # バリデーション
    is_valid, err_msg = validate_user_id_not_none(user_id)
    if not is_valid:
        return post_response(400, f"Bad Request: {err_msg}")
    is_valid, err_msg = validate_date(date)
    if not is_valid:
        return post_response(400, f"Bad Request: {err_msg}")
    is_valid, err_msg = validate_message_not_none(message)
    if not is_valid:
        return post_response(400, f"Bad Request: {err_msg}")

    try:
        user = get_item(user_table, "user_id", user_id)

        # date(YYYY-MM-DD)をdatetimeに変換
        dt = datetime.datetime.strptime(date, "%Y-%m-%d")
        # dtが日本時間での0時を取得しているので、9時間引く
        dt = dt - datetime.timedelta(hours=9)
        dt = str(dt.isoformat())
        expr = Key("assigned_to").eq(user_id) & Key("last_status_at").gte(dt)
        task_list = get_items(task_table, "UserLastStatusAtIndex", expr)
        task_ids = [task["task_id"] for task in task_list]
        serious = sum([int(task["serious"]) for task in task_list])

        gpt_diary = gen_user_diary_data(message, task_list)
        # TODO send message to ChatGPT
        diary_id = str(uuid.uuid4())
        now = datetime.datetime.now().isoformat()
        item = {
            "diary_id": diary_id,
            "section_id": user["section_id"],
            "date": date,
            "details": gpt_diary["details"],
            "ai_analysis": gpt_diary["ai_analysis"],
            # "serious": int(gpt_diary["serious"]),
            "serious": serious,
            "created_at": now,
            "updated_at": now,
            "user_id": user_id,
            "task_ids": task_ids,
        }
        user_diary = post_item(user_diary_table, item)

    except DynamoDBError as e:
        return post_response(500, f"Internal Server Error: DynamoDB Error: {e}")
    except IndexError as e:
        return post_response(404, f"Not Found: {e}")
    except Exception as e:
        print(traceback.format_exc())
        return post_response(500, f"Internal Server Error: {e}")

    return post_response(200, json_dumps(user_diary))
