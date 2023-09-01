import json


def lambda_handler(event, context):
    task_id = event.get("pathParameters", {}).get("task_id")

    if task_id is None or not isinstance(task_id, str):
        return {"statusCode": 400, "body": "Bad Request: Invalid task_id"}

    response = {
        "statusCode": 200,
        "body": json.dumps({"message": f"Deleted task with ID: {task_id}"}),
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": True,
            "Access-Control-Allow-Methods": "POST",
            "Access-Control-Allow-Headers": "Content-Type,X-CSRF-TOKEN",
        }
    }

    return response
