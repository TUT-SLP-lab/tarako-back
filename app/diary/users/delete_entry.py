from table_utils import (
    DynamoDBError,
    get_item,
    json_dumps,
    user_diary_table,
    validate_diary_id,
    validate_user_id,
)


def lambda_handler(event, context):
    user_id = event.get("pathParameters", {}).get("user_id")
    diary_id = event.get("pathParameters", {}).get("diary_id")

    # バリデーション
    is_valid, err_msg = validate_user_id(user_id)
    if not is_valid:
        return {"statusCode": 400, "body": f"Bad Request: {err_msg}"}
    is_valid, err_msg = validate_diary_id(diary_id)
    if not is_valid:
        return {"statusCode": 400, "body": f"Bad Request: {err_msg}"}

    # search user diary
    try:
        user_diary = get_item(user_diary_table, "diary_id", diary_id)
    except DynamoDBError as e:
        return {"statusCode": 500, "body": str(e)}
    except IndexError:
        return {"statusCode": 404, "body": f"Not Found: user_id={user_id}"}

    if user_diary["user_id"] != user_id:
        return {"statusCode": 403, "body": "Forbidden: Invalid user_id"}

    # delete user diary
    option = {"Key": {"diary_id": diary_id}}
    response = user_diary_table.delete_item(**option)

    if response["ResponseMetadata"]["HTTPStatusCode"] != 200:
        return {
            "statusCode": 500,
            "body": f"Failed to delete diary with ID: {diary_id} for section with ID: {user_id}",
        }
    return {
        "statusCode": 200,
        "body": json_dumps(
            {
                "message": f"Deleted diary with ID: {diary_id} for section with ID: {user_id}"
            }
        ),
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "DELETE",
            "Access-Control-Allow-Headers": "Content-Type,X-CSRF-TOKEN",
        },
    }
