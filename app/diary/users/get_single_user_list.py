from boto3.dynamodb.conditions import Key
from table_utils import json_dumps, user_diary_table


def lambda_handler(event, context):
    path_params = event.get("pathParameters", {})
    if path_params is None:
        return {"statusCode": 400, "body": "Bad Request: Invalid path parameters"}
    user_id = path_params.get("user_id", None)
    qsp = event.get("queryStringParameters")
    if qsp:
        from_date = event.get("from_date", None)
        to_date = event.get("to_date", None)
    else:
        from_date = None
        to_date = None

    # Validation
    if user_id is None or not isinstance(user_id, str):
        return {"statusCode": 400, "body": "Bad Request: Invalid user_id"}
    if from_date is not None and not isinstance(from_date, str):
        return {"statusCode": 400, "body": "Bad Request: Invalid from_date"}
    if to_date is not None and not isinstance(to_date, str):
        return {"statusCode": 400, "body": "Bad Request: Invalid to_date"}

    # Get user diary list
    user_id_key = Key("user_id").eq(user_id)
    if from_date is None and to_date is None:
        option = {"IndexName": "UserIndex"}
        expr = user_id_key
    else:
        if from_date is not None and to_date is not None:
            datetime_range = Key("date").between(from_date, to_date)
        elif from_date is not None:
            datetime_range = Key("date").gte(from_date)
        elif to_date is not None:
            datetime_range = Key("date").lte(to_date)
        option = {"IndexName": "UserDateIndex"}
        expr = user_id_key & datetime_range

    option["KeyConditionExpression"] = expr
    response = user_diary_table.query(**option)

    # Validation
    if response["ResponseMetadata"]["HTTPStatusCode"] != 200:
        return {"statusCode": 500, "body": "DynamoDB Error"}

    return {
        "statusCode": 200,
        "body": json_dumps(response["Items"]),
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET",
            "Access-Control-Allow-Headers": "Content-Type,X-CSRF-TOKEN",
        },
    }
