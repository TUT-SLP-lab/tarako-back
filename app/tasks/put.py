import json
from datetime import datetime

from table_utils import json_dumps, task_table


def lambda_handler(event, context):
    ppm = event.get("pathParameters")
    if ppm is None:
        return {"statusCode": 400, "body": "Bad Request: Missing pathParameters"}
    task_id = ppm.get("task_id")
    body = event.get("body", None)

    # バリデーション
    erro_msg = []
    option = {"Key": {"task_id": task_id}}
    if not task_id:
        return {"statusCode": 400, "body": "Bad Request: Missing task_id"}
    elif not isinstance(task_id, str):
        erro_msg.append("task_id must be string")
    else:
        response = task_table.get_item(**option)
        if "Item" not in response:
            return {"statusCode": 404, "body": "Not Found: Diary not found"}

    if body is None:
        return {"statusCode": 400, "body": "Bad Request: Missing body"}
    else:
        json_body = json.loads(body)
    if not isinstance(body, dict):
        return {"statusCode": 400, "body": "Bad Request: body must be dict"}

    # bodyのバリデーション
    is_valid, erro_msg = validate_body(json_body)
    if not is_valid:
        return {"statusCode": 400, "body": f"Bad Request: {', '.join(erro_msg)}"}
    last_progress = json_body.get("progresses")[-1]

    expr = ", ".join(
        [
            "SET completed=:completed",
            "last_status_at=:last_status_at",
            "updated_at=:updated_at",
            "assigned_to=:assigned_to",
            "section_id=:section_id",
            "title=:title",
            "category=:category",
            "tags=:tags",
            "progresses=:progresses",
            "serious=:serious",
            "details=:details",
        ]
    )

    update_object = {
        ":completed": "True" if last_progress["percentage"] == 100 else "False",
        ":last_status_at": last_progress["datetime"],
        ":updated_at": datetime.now().isoformat(),
        ":assigned_to": json_body.get("assigned_to"),
        ":section_id": json_body.get("section_id"),
        ":title": json_body.get("title"),
        ":category": json_body.get("category"),
        ":tags": json_body.get("tags"),
        ":progresses": json_body.get("progresses"),
        ":serious": json_body.get("serious"),
        ":details": json_body.get("details"),
    }

    response = task_table.update_item(
        Key=option["Key"],
        UpdateExpression=expr,
        ExpressionAttributeValues=update_object,
        ReturnValues="ALL_NEW",
    )

    return {
        "statusCode": 200,
        "body": json_dumps(response["Attributes"]),
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET",
            "Access-Control-Allow-Headers": "Content-Type,X-CSRF-TOKEN",
        },
    }


def check_in_body_and_type(body, key, type) -> tuple[bool, str]:
    if key not in body:
        return False, f"{key} is required"
    if not isinstance(body[key], type):
        return False, f"{key} must be {type}"
    return True, ""


def validate_body(body: dict) -> tuple[bool, list[str]]:
    error_msg = []
    key_type = {
        "assigned_to": str,
        "title": str,
        "category": str,
        "tags": list,
        "progresses": list,
        "serious": int,
        "details": str,
        "section_id": int,
    }
    for key, type in key_type.items():
        is_valid, msg = check_in_body_and_type(body, key, type)
        if not is_valid:
            error_msg.append(msg)
        if key == "tags":
            if not all(isinstance(tag, str) for tag in body["tags"]):
                error_msg.append("all tags must be string")
        if key == "serious":
            if not (0 <= body["serious"] <= 5):
                error_msg.append("serious must be 0 <= serious <= 5")
        if key == "progresses":
            if not all(
                isinstance(progress, dict)
                and "datetime" in progress
                and "percentage" in progress
                for progress in body["progresses"]
            ):
                error_msg.append(
                    "all progresses must be dict and have datetime and percentage"
                )
            if not all(
                isinstance(progress["datetime"], str)
                and isinstance(progress["percentage"], int)
                for progress in body["progresses"]
            ):
                error_msg.append("all progresses must be datetime and percentage")
    return len(error_msg) == 0, error_msg
