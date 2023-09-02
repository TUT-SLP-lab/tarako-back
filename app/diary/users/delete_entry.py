import json
from decimal import Decimal

import boto3
import os
# from boto3.dynamodb.conditions import Key


dynamodb = boto3.resource("dynamodb", region_name="ap-northeast-1")
user_diary_table = dynamodb.Table(f"UserDiaryTable-{PR_NUM}")


def decimal_to_int(obj):
    if isinstance(obj, Decimal):
        return int(obj)
    if isinstance(obj, set):
        return list(obj)


def lambda_handler(event, context):
    user_id = event.get("pathParameters", {}).get("user_id")
    diary_id = event.get("pathParameters", {}).get("diary_id")

    # バリデーション
    if user_id is None or not isinstance(user_id, str):
        return {"statusCode": 400, "body": "Bad Request: Invalid user_id"}
    if diary_id is None or not isinstance(diary_id, str):
        return {"statusCode": 400, "body": "Bad Request: Invalid diary_id"}

    # search user diary
    option = {"Key": {"diary_id": diary_id}}
    response = user_diary_table.get_item(**option)
    if response["ResponseMetadata"]["HTTPStatusCode"] != 200:
        return {"statusCode": 500, "body": "DynamoDB Error"}
    if "Item" not in response:
        return {"statusCode": 404, "body": "TaskID is not found"}

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
        "body": json.dumps(
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
