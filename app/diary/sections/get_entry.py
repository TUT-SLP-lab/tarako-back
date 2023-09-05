from table_utils import (
    DynamoDBError,
    get_item,
    json_dumps,
    section_diary_table,
    validate_diary_id,
    validate_section_id,
)


def lambda_handler(event, context):
    path_params = event.get("pathParameters", {})
    if path_params is None:
        return {"statusCode": 400, "body": "Bad Request: Invalid path parameters"}
    section_id = path_params.get("section_id", None)
    diary_id = path_params.get("diary_id", None)

    # バリデーション
    is_valid, err_msg = validate_section_id(section_id)
    if not is_valid:
        return {"statusCode": 400, "body": f"Bad Request: {err_msg}"}
    is_valid, err_msg = validate_diary_id(diary_id)
    if not is_valid:
        return {"statusCode": 400, "body": f"Bad Request: {err_msg}"}

    try:
        # diary_idの確認
        diary = get_item(section_diary_table, "diary_id", diary_id)
    except DynamoDBError as e:
        return {"statusCode": 500, "body": f"Internal Server Error: {e}"}
    except IndexError as e:
        return {"statusCode": 404, "body": f"Not Found: {e}"}

    return {
        "statusCode": 200,
        "body": json_dumps(diary),
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET",
            "Access-Control-Allow-Headers": "Content-Type,X-CSRF-TOKEN",
        },
    }
