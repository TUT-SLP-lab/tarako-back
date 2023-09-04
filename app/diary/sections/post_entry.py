import json
import uuid
from datetime import datetime

from boto3.dynamodb.conditions import Key
from table_utils import (json_dumps, section_diary_table, section_table,
                         user_table)


def lambda_handler(event, context):
    ppm = event.get("pathParameters", {})

    if ppm is None:
        return {"statusCode": 400, "body": "Bad Request: Invalid path parameters"}
    section_id = ppm.get("section_id")
    try:
        section_id = int(section_id)
    except ValueError:
        return {"statusCode": 400, "body": "Bad Request: Invalid section_id"}

    body = event.get("body", "{}")
    if body is None:
        return {"statusCode": 400, "body": "Bad Request: Invalid body"}

    body = json.loads(body)
    date = body.get("date", None)
    message = body.get("message", None)

    print(date, message)

    # バリデーション
    if section_id is None or not isinstance(section_id, int):
        return {"statusCode": 400, "body": "Bad Request: Invalid section_id"}

    param = {
        "IndexName": "SectionIndex",
        "KeyConditionExpression": Key("section_id").eq(section_id),
    }
    user_resp = user_table.query(**param)
    if user_resp["ResponseMetadata"]["HTTPStatusCode"] != 200:
        return {
            "statusCode": 500,
            "body": f"Failed to find diary with section id: {section_id}",
        }
    if "Items" not in user_resp:
        return {
            "statusCode": 404,
            "body": f"Item is not found with {section_id}",
        }
    print(user_resp)
    user_ids = [item["user_id"] for item in user_resp["Items"]]

    # TODO Chat GPTに聞く

    # section 情報の取得
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

    diary_id = str(uuid.uuid4())
    # Update 処理
    item = {
        "diary_id": diary_id,
        "date": date,
        "details": "hoge.fugaの単体テストを作成する",
        "serious": 0,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "section_id": section_id,
        "section": section,
        "user_ids": user_ids,
    }
    put_resp = section_diary_table.put_item(Item=item)
    if put_resp["ResponseMetadata"]["HTTPStatusCode"] != 200:
        return {
            "statusCode": 500,
            "body": f"Failed to put diary with section id: {section_id}",
        }

    return {
        "statusCode": 200,
        "body": json_dumps(item),
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST",
            "Access-Control-Allow-Headers": "Content-Type,X-CSRF-TOKEN",
        },
    }
