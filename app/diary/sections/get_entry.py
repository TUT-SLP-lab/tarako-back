from table_utils import (
    DynamoDBError,
    get_item,
    json_dumps,
    section_diary_table,
    section_table,
)


def lambda_handler(event, context):
    path_params = event.get("pathParameters", {})
    if path_params is None:
        return {"statusCode": 400, "body": "Bad Request: Invalid path parameters"}
    section_id = path_params.get("section_id", None)
    diary_id = path_params.get("diary_id", None)

    # バリデーション
    if section_id is None or not isinstance(section_id, str):
        return {"statusCode": 400, "body": "Bad Request: Invalid section_id"}
    if diary_id is None or not isinstance(diary_id, str):
        return {"statusCode": 400, "body": "Bad Request: Invalid diary_id"}
    try:
        section_id = int(section_id)
    except ValueError:
        return {"statusCode": 400, "body": "Bad Request: Invalid section_id"}

    try:
        # diary_idの確認
        diary = get_item(section_diary_table, "diary_id", diary_id)
        if diary["section_id"] != section_id:
            return {"statusCode": 404, "body": "Not Found: Diary not found"}

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
