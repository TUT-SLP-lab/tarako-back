import json


def lambda_handler(event, context):
    user_id = event.get("pathParameters", {}).get("user_id")
    diary_id = event.get("pathParameters", {}).get("diary_id")

    # バリデーション
    if user_id is None or not isinstance(user_id, int):
        return {"statusCode": 400, "body": "Bad Request: Invalid user_id"}
    if diary_id is None or not isinstance(diary_id, str):
        return {"statusCode": 400, "body": "Bad Request: Invalid diary_id"}

    # ここに処理を書く

    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "message": f"Deleted diary with ID: {diary_id} for section with ID: {user_id}"
            }
        ),
    }
