import json
from datetime import datetime

from table_utils import (
    DynamoDBError,
    get_item,
    get_items,
    json_dumps,
    put_item,
    user_diary_table,
    user_table,
)


def lambda_handler(event, context):
    path_params = event.get("pathParameters", {})
    if path_params is None:
        return {"statusCode": 400, "body": "Bad Request: Missing path parameters"}
    user_id = path_params.get("user_id", None)
    diary_id = path_params.get("diary_id", None)

    body = event.get("body", "{}")
    if body is None:
        return {"statusCode": 400, "body": "Bad Request: Missing request body"}
    body = json.loads(body)
    detailes = body.get("details", None)
    serious = body.get("serious", None)
    task_ids = body.get("task_ids", None)

    # validation
    if user_id is None or not isinstance(user_id, str):
        return {"statusCode": 400, "body": "Bad Request: Invalid user_id"}
    if diary_id is None or not isinstance(diary_id, str):
        return {"statusCode": 400, "body": "Bad Request: Invalid diary_id"}
    if detailes is None or not isinstance(detailes, str):
        return {"statusCode": 400, "body": "Bad Request: Invalid detailes"}
    if serious is None or not isinstance(serious, int):
        return {"statusCode": 400, "body": "Bad Request: Invalid serious"}
    if task_ids is None or not isinstance(task_ids, list):
        return {"statusCode": 400, "body": "Bad Request: Invalid task_ids"}

    try:
        user_list = get_items(user_table, "user_id", user_id)
        user_ids = [user["user_id"] for user in user_list]
        if user_id not in user_ids:
            return {"statusCode": 400, "body": "Bad Request: user_id not found"}

        user_diary = get_item(user_diary_table, "diary_id", diary_id)
        # user ID check
        if user_diary["user_id"] != user_id:
            return {"statusCode": 403, "body": "Forbidden"}

        UpdateExpression = "set details=:d, serious=:s, task_ids=:t, updated_at=:u"
        ExpressionAttributeValues = {
            ":d": detailes,
            ":s": serious,
            ":t": task_ids,
            ":u": datetime.now().isoformat(),
        }
        user_diary = put_item(
            user_diary_table,
            "diary_id",
            diary_id,
            UpdateExpression,
            ExpressionAttributeValues,
        )

    except DynamoDBError as e:
        return {"statusCode": 500, "body": f"Internal Server Error: {e}"}
    except IndexError as e:
        return {"statusCode": 404, "body": f"Not Found: {e}"}

    # get diary again
    return {
        "statusCode": 200,
        "body": json_dumps(user_diary),
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "PUT",
            "Access-Control-Allow-Headers": "Content-Type,X-CSRF-TOKEN",
        },
    }
