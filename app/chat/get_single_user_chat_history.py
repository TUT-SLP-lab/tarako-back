from boto3.dynamodb.conditions import Key
from table_utils import (DynamoDBError, chat_history_table, get_items,
                         json_dumps)
from validation import validate_datetime, validate_user_id_not_none


def lambda_handler(event, context):
    ppm = event.get("pathParameters", {})
    if ppm is None:
        return {"statusCode": 400, "body": "Bad Request: Invalid path parameters"}
    user_id = ppm.get("user_id", None)
    qsp = event.get("queryStringParameters")
    if qsp:
        from_date = event.get("from_date", None)
        to_date = event.get("to_date", None)
    else:
        from_date = None
        to_date = None

    # Validation
    is_valid, err_msg = validate_user_id_not_none(user_id)
    if not is_valid:
        return {"statusCode": 400, "body": f"Bad Request: {err_msg}"}
    is_valid, err_msg = validate_datetime(from_date, to_date)
    if not is_valid:
        return {"statusCode": 400, "body": f"Bad Request: {err_msg}"}

    try:
        user_id_key = Key("user_id").eq(user_id)
        if from_date is None and to_date is None:
            index_name = "UserIndex"
            expr = user_id_key
        else:
            if from_date is not None and to_date is not None:
                datetime_range = Key("date").between(from_date, to_date)
            elif from_date is not None:
                datetime_range = Key("date").gte(from_date)
            elif to_date is not None:
                datetime_range = Key("date").lte(to_date)
            index_name = "UserDateIndex"
            expr = user_id_key & datetime_range

        chat_history = get_items(chat_history_table, index_name, expr)
    except DynamoDBError as e:
        print(e)
        return {"statusCode": 500, "body": "Internal Server Error: DynamoDB Error"}
    except Exception as e:
        print(e)
        return {"statusCode": 500, "body": "Internal Server Error: Unknown Error"}

    return {
        "statusCode": 200,
        "body": json_dumps(chat_history),
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET",
            "Access-Control-Allow-Headers": "Content-Type,X-CSRF-TOKEN",
        },
    }
