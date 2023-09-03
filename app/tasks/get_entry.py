from table_utils import json_dumps, task_table


def lambda_handler(event, context):
    ppm = event.get("pathParameters")
    if ppm is None:
        return {"statusCode": 400, "body": "Bad Request: Missing pathParameters"}
    task_id = ppm.get("task_id")

    # バリデーション
    if not task_id:
        return {"statusCode": 400, "body": "Bad Request: Missing task_id"}

    response = task_table.get_item(Key={"task_id": task_id})
    if "Item" not in response:
        return {"statusCode": 404, "body": "Not Found"}

    return {
        "statusCode": 200,
        "body": json_dumps(response["Item"]),
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET",
            "Access-Control-Allow-Headers": "Content-Type,X-CSRF-TOKEN",
        },
    }
