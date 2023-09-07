import json
from datetime import datetime

from responses import put_response
from table_utils import DynamoDBError, get_item, json_dumps, put_item, user_diary_table
from validation import (
    validate_details_not_none,
    validate_diary_id_not_none,
    validate_serious_not_none,
    validate_user_id_not_none,
)


def lambda_handler(event, context):
    path_params = event.get("pathParameters", {})
    if path_params is None:
        return put_response(400, "Bad Request: Invalid path parameters")
    user_id = path_params.get("user_id", None)
    diary_id = path_params.get("diary_id", None)

    body = event.get("body", "{}")
    if body is None:
        return put_response(400, "Bad Request: Invalid body")
    body = json.loads(body)
    detailes = body.get("details", None)
    serious = body.get("serious", None)
    task_ids = body.get("task_ids", None)

    # validation
    is_valid, err_msg = validate_user_id_not_none(user_id)
    if not is_valid:
        return put_response(400, f"Bad Request: {err_msg}")
    is_valid, err_msg = validate_diary_id_not_none(diary_id)
    if not is_valid:
        return put_response(400, f"Bad Request: {err_msg}")
    is_valid, err_msg = validate_details_not_none(detailes)
    if not is_valid:
        return put_response(400, f"Bad Request: {err_msg}")
    is_valid, err_msg = validate_serious_not_none(serious)
    if not is_valid:
        return put_response(400, f"Bad Request: {err_msg}")

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
        return put_response(500, f"Internal Server Error: DynamoDB Error: {e}")
    except IndexError as e:
        return put_response(404, f"Not Found: {e}")

    return put_response(200, json_dumps(user_diary))
