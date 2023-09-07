from responses import get_response
from table_utils import DynamoDBError, get_item, json_dumps, user_diary_table
from validation import validate_diary_id_not_none, validate_user_id_not_none


def lambda_handler(event, context):
    path_params = event.get("pathParameters", {})

    if path_params is None:
        return get_response(400, "Bad Request: Invalid path parameters")
    else:
        user_id = path_params.get("user_id", None)
        diary_id = path_params.get("diary_id", None)

    # Validation
    is_valid, err_msg = validate_user_id_not_none(user_id)
    if not is_valid:
        return get_response(400, f"Bad Request: {err_msg}")
    is_valid, err_msg = validate_diary_id_not_none(diary_id)
    if not is_valid:
        return get_response(400, f"Bad Request: {err_msg}")

    try:
        user_diary = get_item(user_diary_table, "diary_id", diary_id)
    except DynamoDBError as e:
        return get_response(500, f"Internal Server Error: DynamoDB Error: {e}")
    except IndexError as e:
        return get_response(404, f"Not Found: {e}")
    # user ID check
    if user_diary["user_id"] != user_id:
        return get_response(403, "Forbidden: Invalid user_id")

    return get_response(200, json_dumps(user_diary))
