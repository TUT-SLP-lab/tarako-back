import json


def lambda_handler(event, context):
    task_id = event.get("pathParameters", {}).get("task_id")

    if task_id is None or not isinstance(task_id, str):
        return {"statusCode": 400, "body": "Bad Request: Invalid task_id"}

    response = {
        "statusCode": 200,
        "body": json.dumps({"message": f"Deleted task with ID: {task_id}"}),
    }

    return response
