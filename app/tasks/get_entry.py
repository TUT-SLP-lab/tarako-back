from data_formatter import task_to_front
from responses import get_response
from table_utils import DynamoDBError, get_item, json_dumps, task_table
from validation import validate_task_id_not_none


def lambda_handler(event, context):
    ppm = event.get("pathParameters")
    if ppm is None:
        return get_response(400, "Bad Request: Invalid path parameters")
    task_id = ppm.get("task_id")

    # バリデーション
    is_valid, err_msg = validate_task_id_not_none(task_id)
    if not is_valid:
        return get_response(400, f"Bad Request: {err_msg}")

    try:
        response = task_to_front(get_item(task_table, "task_id", task_id))
    except DynamoDBError as e:
        return get_response(500, f"Internal Server Error: DynamoDB Error: {e}")
    except IndexError as e:
        return get_response(404, f"Not Found: {e}")
    return get_response(200, json_dumps(response))
