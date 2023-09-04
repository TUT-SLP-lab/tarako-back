from table_utils import DynamoDBError, get_item, json_dumps, user_diary_table


def lambda_handler(event, context):
    path_params = event.get("pathParameters", {})

    if path_params is None:
        return {"statusCode": 400, "body": "Bad Request: Invalid path parameters"}
    else:
        user_id = path_params.get("user_id", None)
        diary_id = path_params.get("diary_id", None)

    # Validation
    if user_id is None or not isinstance(user_id, str):
        return {"statusCode": 400, "body": "Bad Request: Invalid user_id"}
    if diary_id is None or not isinstance(diary_id, str):
        return {"statusCode": 400, "body": "Bad Request: Invalid diary_id"}

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
