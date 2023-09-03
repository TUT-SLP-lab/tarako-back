from boto3.dynamodb.conditions import Key
from table_utils import json_dumps, user_diary_table


def lambda_handler(event, context):
    qsp = event.get("queryStringParameters")
    if qsp:
        from_date = qsp.get("from_date")
        to_date = qsp.get("to_date")
    else:
        from_date = None
        to_date = None
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
    if from_date is None and to_date is None:
        option = {"IndexName": "UserIndex"}
        datetime_range = None
    else:
        if from_date is not None and to_date is not None:
            datetime_range = Key("date").between(from_date, to_date)
        elif from_date is not None:
            datetime_range = Key("date").gte(from_date)
        elif to_date is not None:
            datetime_range = Key("date").lte(to_date)
        option = {"IndexName": "UserDateIndex"}

    user_daily_list = []
    for user in user_list:
        user_id_key = Key("user_id").eq(user)
        if datetime_range is not None:
            expr = user_id_key & datetime_range
        else:
            expr = user_id_key
        option["KeyConditionExpression"] = expr

        response = user_diary_table.query(**option)
        if response["ResponseMetadata"]["HTTPStatusCode"] != 200:
            return {"statusCode": 500, "body": "DynamoDB Error"}
        user_daily_list += response["Items"]

    return {
        "statusCode": 200,
        "body": json_dumps(user_daily_list),
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET",
            "Access-Control-Allow-Headers": "Content-Type,X-CSRF-TOKEN",
        },
    }
