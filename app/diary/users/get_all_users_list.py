from boto3.dynamodb.conditions import Key
from table_utils import (
    DynamoDBError,
    get_all_items,
    get_items,
    json_dumps,
    user_diary_table,
    user_table,
    validate_datetime,
)


def lambda_handler(event, context):
    qsp = event.get("queryStringParameters")
    if qsp:
        from_date = qsp.get("from_date")
        to_date = qsp.get("to_date")
    else:
        from_date = None
        to_date = None

    # バリデーション
    is_valid, err_msg = validate_datetime(from_date, to_date)
    if not is_valid:
        return {"statusCode": 400, "body": f"Bad Request: {err_msg}"}

    try:
        users = get_all_items(user_table)
        user_ids = [user["user_id"] for user in users]

        # get user diary list between from_date and to_date
        if from_date is None and to_date is None:
            index_name = "UserIndex"
            datetime_range = None
        else:
            if from_date is not None and to_date is not None:
                datetime_range = Key("date").between(from_date, to_date)
            elif from_date is not None:
                datetime_range = Key("date").gte(from_date)
            elif to_date is not None:
                datetime_range = Key("date").lte(to_date)
            index_name = "UserDateIndex"

        user_daily_list = []
        for user_id in user_ids:
            user_id_key = Key("user_id").eq(user_id)
            if datetime_range is not None:
                expr = user_id_key & datetime_range
            else:
                expr = user_id_key

            user_diary = get_items(user_diary_table, index_name, expr)
            user_daily_list += user_diary
    except DynamoDBError as e:
        return {"statusCode": 500, "body": f"Internal Server Error: {e}"}
    except IndexError as e:
        return {"statusCode": 404, "body": f"Not Found: {e}"}

    return {
        "statusCode": 200,
        "body": json_dumps(user_daily_list),
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET",
            "Access-Control-Allow-Headers": "Content-Type,X-CSRF-TOKEN",
        },
    }
