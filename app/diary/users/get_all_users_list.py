import json
import os
from decimal import Decimal

import boto3
from boto3.dynamodb.conditions import Key

TABLE_NAME = "UserDiaryTable"
PR_NUM = os.getenv("PR_NUM")
print(f"{TABLE_NAME}-{PR_NUM}")
dynamodb = boto3.resource("dynamodb", region_name="ap-northeast-1")
user_diary_table = dynamodb.Table(f"{TABLE_NAME}-{PR_NUM}")


def decimal_to_int(obj):
    if isinstance(obj, Decimal):
        return int(obj)
    if isinstance(obj, set):
        return list(obj)


def lambda_handler(event, context):
    body = event.get("body", "{}")
    body = "{}" if body is None else body
    try:
        body = json.loads(body)
    except json.JSONDecodeError:
        return {"statusCode": 400, "body": "Bad Request: Invalid JSON"}
    from_date = body.get("from", None)
    to_date = body.get("to", None)

    # バリデーション
    if from_date is not None and not isinstance(from_date, str):
        return {"statusCode": 400, "body": "Bad Request: Invalid from_date"}
    if to_date is not None and not isinstance(to_date, str):
        return {"statusCode": 400, "body": "Bad Request: Invalid to_date"}

    # TODO from user DB
    user_list = [
        "4f73ab32-21bf-47ef-a119-fa024bc2b9cc",
        "595c060d-8417-4ac8-bcb5-c8e733dc64e0",
        "e08bf311-b1bc-4a38-bac1-374c3ede7203",
    ]

    # get user diary list between from_date and to_date
    user_daily_list = []
    for user in user_list:
        if from_date is None and to_date is None:
            user_id_key = Key("user_id").eq(user)
            option = {
                "IndexName": "UserIndex",
                "KeyConditionExpression": user_id_key,
            }
        else:
            if from_date is not None and to_date is not None:
                datetime_range = Key("date").between(from_date, to_date)
            elif from_date is not None:
                datetime_range = Key("date").gte(from_date)
            elif to_date is not None:
                datetime_range = Key("date").lte(to_date)

            user_id_key = Key("user_id").eq(user)
            option = {
                "IndexName": "UserDateIndex",
                "KeyConditionExpression": user_id_key & datetime_range,
            }

        response = user_diary_table.query(
            **option,
        )
        if response["ResponseMetadata"]["HTTPStatusCode"] != 200:
            return {"statusCode": 500, "body": "DynamoDB Error"}
        user_daily_list += response["Items"]

    return {
        "statusCode": 200,
        "body": json.dumps(user_daily_list, default=decimal_to_int),
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET",
            "Access-Control-Allow-Headers": "Content-Type,X-CSRF-TOKEN",
        },
    }
