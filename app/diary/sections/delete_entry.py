import json

from table_utils import DynamoDBError, delete_item, get_item, section_diary_table
from validation import validate_diary_id_not_none, validate_section_id_not_none


def lambda_handler(event, context):
    ppm = event.get("pathParameters", {})
    if ppm is None:
        return {"statusCode": 400, "body": "Bad Request: Invalid path parameters"}
    sections_id = ppm.get("section_id", None)
    diary_id = ppm.get("diary_id")

    try:
        section_id = int(sections_id)
    except ValueError:
        return {"statusCode": 400, "body": "Bad Request: Invalid section_id"}

    # バリデーション
    is_valid, err_msg = validate_section_id_not_none(section_id)
    if not is_valid:
        return {"statusCode": 400, "body": f"Bad Request: {err_msg}"}
    is_valid, err_msg = validate_diary_id_not_none(diary_id)
    if not is_valid:
        return {"statusCode": 400, "body": f"Bad Request: {err_msg}"}

    # sectionの確認
    try:
        print(section_diary_table.name, diary_id)
        diary = get_item(section_diary_table, "diary_id", diary_id)
    except DynamoDBError as e:
        return {"statusCode": 500, "body": f"Failed: {e}"}
    except IndexError as e:
        return {"statusCode": 404, "body": f"Failed: {e}"}
    if diary["section_id"] != section_id:
        return {"statsCode": 404, "body": f"Failed to fild section_id: {section_id}"}

    # 削除処理
    try:
        delete_item(section_diary_table, "diary_id", diary_id)
    except DynamoDBError as e:
        return {"statusCode": 500, "body": str(e)}

    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "message": f"Deleted diary with ID: {diary_id} for section with ID: {section_id}"
            }
        ),
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "DELETE",
            "Access-Control-Allow-Headers": "Content-Type,X-CSRF-TOKEN",
        },
    }
