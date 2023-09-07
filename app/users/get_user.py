from responses import get_response
from table_utils import get_item, json_dumps, user_table
from validation import validate_user_id_not_none


def lambda_handler(event, context):
    user_id = event.get("pathParameters", {}).get("user_id")

    # バリデーション
    is_valid, err_msg = validate_user_id_not_none(user_id)
    if not is_valid:
        return get_response(400, err_msg)

    try:
        response = get_item(user_table, "user_id", user_id)
    except IndexError as e:
        return get_response(404, json_dumps(e))
    except Exception as e:
        return get_response(500, json_dumps(e))

    return get_response(200, json_dumps(response))
