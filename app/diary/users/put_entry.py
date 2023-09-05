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
    validate_diary_id,
    validate_details_not_none,
    validate_serious,
    validate_task_ids,
    validate_user_id,
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
    is_valid, err_msg = validate_user_id(user_id)
    if not is_valid:
        return {"statusCode": 400, "body": f"Bad Request: {err_msg}"}
    is_valid, err_msg = validate_diary_id(diary_id)
    if not is_valid:
        return {"statusCode": 400, "body": f"Bad Request: {err_msg}"}
    is_valid, err_msg = validate_details_not_none(detailes)
    if not is_valid:
        return {"statusCode": 400, "body": f"Bad Request: {err_msg}"}
    is_valid, err_msg = validate_serious(serious)
    if not is_valid:
        return {"statusCode": 400, "body": f"Bad Request: {err_msg}"}

    try:
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
