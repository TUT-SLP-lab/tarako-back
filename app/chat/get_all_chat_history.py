from boto3.dynamodb.conditions import Key
from table_utils import chat_history_table, get_items, json_dumps


def lambda_handler(event, context):
    qsp = event.get("queryStringParameters")
    if qsp:
        from_date = event.get("from_date", None)
        to_date = event.get("to_date", None)
    else:
        from_date = None
        to_date = None
    if from_date is not None and not isinstance(from_date, str):
        return {"statusCode": 400, "body": "Bad Request: Invalid from_date"}
    if to_date is not None and not isinstance(to_date, str):
        return {"statusCode": 400, "body": "Bad Request: Invalid to_date"}

    try:
        if from_date is None and to_date is None:
            # scanを利用して、全件取得する
            chat_history = chat_history_table.scan()
        else:
            if from_date is not None and to_date is not None:
                datetime_range = Key("date").between(from_date, to_date)
            elif from_date is not None:
                datetime_range = Key("date").gte(from_date)
            elif to_date is not None:
                datetime_range = Key("date").lte(to_date)
            index_name = "UserDateIndex"
            # TODO: user_listをDBから取得する
            user_list = [
                "4f73ab32-21bf-47ef-a119-fa024bc2b9cc",
                "595c060d-8417-4ac8-bcb5-c8e733dc64e0",
                "e08bf311-b1bc-4a38-bac1-374c3ede7203",
            ]
            chat_history = []
            for user in user_list:
                expr = Key("user_id").eq(user) & datetime_range
                tmp_chat = get_items(chat_history_table, index_name, expr)
                chat_history.extend(tmp_chat)
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
