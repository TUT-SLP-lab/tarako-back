import json

from boto3.dynamodb.conditions import Key
from table_utils import json_dumps, user_diary_table


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

    return {
        "statusCode": 200,
        "body": json_dumps(response["Item"]),
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET",
            "Access-Control-Allow-Headers": "Content-Type,X-CSRF-TOKEN",
        },
    }
