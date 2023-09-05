from table_utils import DynamoDBError, delete_item, json_dumps, task_table
from validation import validate_task_id_not_none


def lambda_handler(event, context):
    ppm = event.get("pathParameters")
    if ppm is None:
        return {"statusCode": 400, "body": "Bad Request: Missing pathParameters"}
    task_id = ppm.get("task_id")

    # バリデーション
    is_valid, err_msg = validate_task_id_not_none(task_id)
    if not is_valid:
        return {"statusCode": 400, "body": f"Bad Request: {err_msg}"}

    try:
        delete_item(task_table, "task_id", task_id)
    except DynamoDBError as e:
        return {"statusCode": 500, "body": str(e)}

    return {
        "statusCode": 200,
        "body": json_dumps({"message": f"Deleted task with ID: {task_id}"}),
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "DELETE",
            "Access-Control-Allow-Headers": "Content-Type,X-CSRF-TOKEN",
        },
    }
