from table_utils import json_dumps, task_table


def lambda_handler(event, context):
    ppm = event.get("pathParameters")
    if ppm is None:
        return {"statusCode": 400, "body": "Bad Request: Missing pathParameters"}
    task_id = ppm.get("task_id")

    # バリデーション
    if not task_id and not isinstance(task_id, str):
        return {"statusCode": 400, "body": "Bad Request: Missing task_id"}

    option = {"Key": {"task_id": task_id}}
    response = task_table.get_item(**option)
    if response["ResponseMetadata"]["HTTPStatusCode"] != 200:
        return {"statusCode": 500, "body": "DynamoDB Error"}
    if "Item" not in response:
        return {"statusCode": 404, "body": f"task_id:{task_id} Not Found"}

    response = task_table.delete_item(**option)
    if response["ResponseMetadata"]["HTTPStatusCode"] != 200:
        return {
            "statusCode": 500,
            "body": f"Failed to delete task with ID: {task_id}",
        }

    return {
        "statusCode": 200,
        "body": json_dumps({"message": f"Deleted task with ID: {task_id}"}),
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "DELETE",
            "Access-Control-Allow-Headers": "Content-Type,X-CSRF-TOKEN",
        },
    }
