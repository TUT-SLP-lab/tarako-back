import json
from datetime import datetime

from table_utils import json_dumps, user_diary_table


def lambda_handler(event, context):
    path_params = event.get("pathParameters", {})
    if path_params is None:
        return {"statusCode": 400, "body": "Bad Request: Missing path parameters"}
    user_id = path_params.get("user_id", None)
    diary_id = path_params.get("diary_id", None)

    body = event.get("body", "{}")
    if body is None:
        return {"statusCode": 400, "body": "Bad Request: Missing request body"}
    body = json.loads(body)
    detailes = body.get("details", None)
    serious = body.get("serious", None)
    task_ids = body.get("task_ids", None)

    # validation
    if user_id is None or not isinstance(user_id, str):
        return {"statusCode": 400, "body": "Bad Request: Invalid user_id"}
    if diary_id is None or not isinstance(diary_id, str):
        return {"statusCode": 400, "body": "Bad Request: Invalid diary_id"}
    if detailes is None or not isinstance(detailes, str):
        return {"statusCode": 400, "body": "Bad Request: Invalid detailes"}
    if serious is None or not isinstance(serious, int):
        return {"statusCode": 400, "body": "Bad Request: Invalid serious"}
    if task_ids is None or not isinstance(task_ids, list):
        return {"statusCode": 400, "body": "Bad Request: Invalid task_ids"}

    # TODO from user db
    user_list = [
        "4f73ab32-21bf-47ef-a119-fa024bc2b9cc",
        "595c060d-8417-4ac8-bcb5-c8e733dc64e0",
        "e08bf311-b1bc-4a38-bac1-374c3ede7203",
    ]
    if user_id not in user_list:
        return {"statusCode": 400, "body": "Bad Request: user_id not found"}

    # get diary
    option = {"Key": {"diary_id": diary_id}}
    response = user_diary_table.get_item(**option)

    # Validation
    if response["ResponseMetadata"]["HTTPStatusCode"] != 200:
        return {"statusCode": 500, "body": "Internal Server Error"}
    if "Item" not in response:
        return {"statusCode": 404, "body": "Not Found"}

    # user ID check
    if response["Item"]["user_id"] != user_id:
        return {"statusCode": 403, "body": "Forbidden"}

    item = response["Item"]
    item["details"] = detailes
    item["serious"] = serious
    item["task_ids"] = task_ids

    response = user_diary_table.update_item(
        Key={"diary_id": diary_id},
        UpdateExpression="set details=:d, serious=:s, task_ids=:t, updated_at=:u",
        ExpressionAttributeValues={
            ":d": detailes,
            ":s": serious,
            ":t": task_ids,
            ":u": datetime.now().isoformat(),
        },
        ReturnValues="UPDATED_NEW",
    )
    # get diary again
    option = {"Key": {"diary_id": diary_id}}
    response = user_diary_table.get_item(**option)
    return {
        "statusCode": 200,
        "body": json_dumps(response["Item"]),
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "PUT",
            "Access-Control-Allow-Headers": "Content-Type,X-CSRF-TOKEN",
        },
    }
