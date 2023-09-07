from responses import delete_response
from table_utils import (
    DynamoDBError,
    delete_item,
    get_item,
    json_dumps,
    user_diary_table,
)
from validation import validate_diary_id_not_none, validate_user_id_not_none


def lambda_handler(event, context):
    user_id = event.get("pathParameters", {}).get("user_id")
    diary_id = event.get("pathParameters", {}).get("diary_id")

    # バリデーション
    is_valid, err_msg = validate_user_id_not_none(user_id)
    if not is_valid:
        return delete_response(400, f"Bad Request: {err_msg}")
    is_valid, err_msg = validate_diary_id_not_none(diary_id)
    if not is_valid:
        return delete_response(400, f"Bad Request: {err_msg}")

    # search user diary
    try:
        user_diary = get_item(user_diary_table, "diary_id", diary_id)
    except DynamoDBError as e:
        return delete_response(500, f"Internal Server Error: DynamoDB Error: {e}")
    except IndexError:
        return delete_response(404, f"Failed to find diary_id: {diary_id}")

    if user_diary["user_id"] != user_id:
        return delete_response(403, "Forbidden: Invalid user_id")

    # delete user diary
    try:
        delete_item(user_diary_table, "diary_id", diary_id)
    except DynamoDBError as e:
        return delete_response(500, f"Internal Server Error: DynamoDB Error: {e}")

    return delete_response(
        200, json_dumps({"message": f"Deleted diary with ID: {diary_id} for user with ID: {user_id}"})
    )
