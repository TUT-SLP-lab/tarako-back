import datetime
import json

from table_utils import (json_dumps, section_diary_table, section_table,
                         user_table)


def lambda_handler(event, context):
    ppm = event.get("pathParameters", {})
    if ppm is None:
        return {"statusCode": 400, "body": "Bad Request: Invalid path parameters"}

    section_id = ppm.get("section_id")
    diary_id = ppm.get("diary_id")
    body = event.get("body", "{}")
    if body is None:
        return {"statusCode": 400, "body": "Bad Request: Invalid body"}
    body = json.loads(body)

    details = body.get("details", None)
    serious = body.get("serious", None)
    user_ids = body.get("user_ids", None)

    # バリデーション
    if section_id is None or not isinstance(section_id, int):
        return {"statusCode": 400, "body": "Bad Request: Invalid section_id"}
    if diary_id is None or not isinstance(diary_id, str):
        return {"statusCode": 400, "body": "Bad Request: Invalid diary_id"}
    if details is None or not isinstance(details, str):
        return {"statusCode": 400, "body": "Bad Request: Invalid details"}
    if serious is None or not isinstance(serious, int):
        return {"statusCode": 400, "body": "Bad Request: Invalid serious"}
    if user_ids is None or not isinstance(user_ids, list):
        return {"statusCode": 400, "body": "Bad Request: Invalid user_ids"}

    for user_id in user_ids:
        user_table_resp = user_table.get_item(Key={"user_id": user_id})
        if user_table_resp["ResponseMetadata"]["HTTPStatusCode"] != 200:
            return {
                "statusCode": 500,
                "body": f"Failed to find user with user id: {user_id}",
            }
        if "Item" not in user_table_resp:
            return {"statusCode": 404, "body": f"User {user_id} is not found"}

    diary_resp = section_diary_table.get_item(Key={"diary_id": diary_id})
    if diary_resp["ResponseMetadata"]["HTTPStatusCode"] != 200:
        return {
            "statusCode": 500,
            "body": f"Failed to find diary with diary id: {diary_id}",
        }
    if "Item" not in diary_resp:
        return {
            "statusCode": 404,
            "body": f"Item is not found with {diary_id}",
        }

    section_resp = section_table.get_item(Key={"section_id": section_id})
    if section_resp["ResponseMetadata"]["HTTPStatusCode"] != 200:
        return {
            "statusCode": 500,
            "body": f"Failed to find section with section id: {section_id}",
        }
    if "Item" not in section_resp:
        return {
            "statusCode": 404,
            "body": f"Item is not found with {section_id}",
        }
    section = section_resp["Item"]

    if diary_resp["Item"]["section_id"] != section_id:
        return {
            "statusCode": 400,
            "body": "Bad Request: Invalid section_id",
        }

    update_resp = section_diary_table.update_item(
        Key={"diary_id": diary_id},
        UpdateExpression="set details=:d, serious=:s, user_ids=:u, updated_at=:upd",
        ExpressionAttributeValues={
            ":d": details,
            ":s": serious,
            ":u": user_ids,
            ":upd": datetime.now().isoformat(),
        },
        ReturnValues="UPDATED_NEW",
    )
    if update_resp["ResponseMetadata"]["HTTPStatusCode"] != 200:
        return {
            "statusCode": 500,
            "body": f"Failed to update diary with diary id: {diary_id}",
        }

    diary = diary_resp["Item"]
    diary["details"] = details
    diary["serious"] = serious
    diary["user_ids"] = user_ids
    diary["updated_at"] = datetime.now().isoformat()
    diary["section"] = section

    return {
        "statusCode": 200,
        "body": json_dumps(diary),
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "PUT",
            "Access-Control-Allow-Headers": "Content-Type,X-CSRF-TOKEN",
        },
    }
