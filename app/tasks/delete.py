from responses import delete_response
from table_utils import DynamoDBError, delete_item, json_dumps, task_table
from validation import validate_task_id_not_none


def lambda_handler(event, context):
    ppm = event.get("pathParameters")
    if ppm is None:
        return delete_response(400, "Bad Request: Invalid path parameters")
    task_id = ppm.get("task_id")

    # バリデーション
    is_valid, err_msg = validate_task_id_not_none(task_id)
    if not is_valid:
        return delete_response(400, f"Bad Request: {err_msg}")

    try:
        delete_item(task_table, "task_id", task_id)
    except DynamoDBError as e:
        return delete_response(500, f"Internal Server Error: DynamoDB Error: {e}")

    return delete_response(200, json_dumps({"message": f"Deleted task with ID: {task_id}"}))
