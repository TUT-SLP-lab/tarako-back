from responses import get_response
from table_utils import DynamoDBError, get_item, json_dumps, user_table


def lambda_handler(event, context):
    user_id = event.get("pathParameters", {}).get("user_id")

    # バリデーション
    if not user_id:
        return get_response(400, "Bad Request: Invalid path parameters")

    # ここに処理を書く
    try:
        response = get_item(user_table, "user_id", user_id)
    except DynamoDBError as e:
        return get_response(500, e)
    except IndexError as e:
        return get_response(404, e)

    return get_response(200, json_dumps(response))
