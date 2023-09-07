from responses import get_response
from table_utils import DynamoDBError, get_item, json_dumps, section_diary_table
from validation import validate_diary_id_not_none, validate_section_id_not_none


def lambda_handler(event, context):
    path_params = event.get("pathParameters", {})
    if path_params is None:
        return get_response(400, "Bad Request: Invalid path parameters")
    section_id = path_params.get("section_id", None)
    diary_id = path_params.get("diary_id", None)

    # バリデーション
    is_valid, err_msg = validate_section_id_not_none(section_id)
    if not is_valid:
        return get_response(400, f"Bad Request: {err_msg}")
    is_valid, err_msg = validate_diary_id_not_none(diary_id)
    if not is_valid:
        return get_response(400, f"Bad Request: {err_msg}")

    try:
        # diary_idの確認
        diary = get_item(section_diary_table, "diary_id", diary_id)
    except DynamoDBError as e:
        return get_response(500, f"Internal Server Error: DynamoDB Error: {e}")
    except IndexError as e:
        return get_response(404, f"Not Found: {e}")

    return get_response(200, json_dumps(diary))
