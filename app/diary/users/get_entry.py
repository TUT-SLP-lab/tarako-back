from table_utils import DynamoDBError, get_item, json_dumps, user_diary_table
from validation import validate_diary_id, validate_user_id


def lambda_handler(event, context):
    path_params = event.get("pathParameters", {})

    if path_params is None:
        return {"statusCode": 400, "body": "Bad Request: Invalid path parameters"}
    else:
        user_id = path_params.get("user_id", None)
        diary_id = path_params.get("diary_id", None)

    # Validation
    is_valid, err_msg = validate_user_id(user_id)
    if not is_valid:
        return {"statusCode": 400, "body": f"Bad Request: {err_msg}"}
    is_valid, err_msg = validate_diary_id(diary_id)
    if not is_valid:
        return {"statusCode": 400, "body": f"Bad Request: {err_msg}"}

    try:
        user_diary = get_item(user_diary_table, "diary_id", diary_id)
    except DynamoDBError as e:
        return {"statusCode": 500, "body": f"Internal Server Error: {e}"}
    except IndexError as e:
        return {"statusCode": 404, "body": f"Not Found: {e}"}
    # user ID check
    if user_diary["user_id"] != user_id:
        return {"statusCode": 403, "body": "Forbidden"}

    return {
        "statusCode": 200,
        "body": json_dumps(user_diary),
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET",
            "Access-Control-Allow-Headers": "Content-Type,X-CSRF-TOKEN",
        },
    }
