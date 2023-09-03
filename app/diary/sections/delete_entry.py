import json

from layer.table_utils import section_diary_table


def lambda_handler(event, context):
    ppm = event.get("pathParameters", {})
    if ppm is None:
        return {"statusCode": 400, "body": "Bad Request: Invalid path parameters"}
    sections_id = ppm.get("sections_id", None)
    diary_id = ppm.get("diary_id")

    try:
        section_id = int(sections_id)
    except ValueError:
        return {"statusCode": 400, "body": "Bad Request: Invalid section_id"}

    # バリデーション
    if section_id is None or not isinstance(section_id, int):
        return {"statusCode": 400, "body": "Bad Request: Invalid section_id"}
    if diary_id is None or not isinstance(diary_id, str):
        return {"statusCode": 400, "body": "Bad Request: Invalid diary_id"}

    option = {"Key": {"section_id": section_id}}
    response = section_diary_table.get_item(**option)
    if response["ResponseMetadata"]["HTTPStatusCode"] != 200:
        return {
            "statusCode": 500,
            "body": f"Failed to find diary with section id: {section_id}",
        }
    if "Item" not in response:
        return {
            "statusCode": 404,
            "body": f"Item is not found with {section_id}",
        }
    if response["Item"]["diary_id"] != diary_id:
        return {"statsCode": 404, "body": f"Failed to fild diary_id: {diary_id}"}

    option = {"Key": {"diary_id": diary_id}}
    response = section_diary_table.delete_item(**option)

    if response["ResponseMetadata"]["HTTPStatusCode"] != 200:
        return {
            "statusCode": 500,
            "body": f"Failed to delete diary with ID: {diary_id} for section with ID: {section_id}",
        }

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
