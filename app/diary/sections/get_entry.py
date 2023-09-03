from table_utils import json_dumps, section_diary_table, section_table


def lambda_handler(event, context):
    path_params = event.get("pathParameters", {})
    if path_params is None:
        return {"statusCode": 400, "body": "Bad Request: Invalid path parameters"}
    section_id = path_params.get("section_id", None)
    diary_id = path_params.get("diary_id", None)

    # バリデーション
    if section_id is None or not isinstance(section_id, str):
        return {"statusCode": 400, "body": "Bad Request: Invalid section_id"}
    if diary_id is None or not isinstance(diary_id, str):
        return {"statusCode": 400, "body": "Bad Request: Invalid diary_id"}
    try:
        section_id = int(section_id)
    except ValueError:
        return {"statusCode": 400, "body": "Bad Request: Invalid section_id"}

    # diary_idの確認
    diary_resp = section_diary_table.get_item(Key={"diary_id": diary_id})
    if diary_resp["ResponseMetadata"]["HTTPStatusCode"] != 200:
        return {"statusCode": 500, "body": "Internal Server Error: Section get failed"}
    if "Item" not in diary_resp:
        return {"statusCode": 404, "body": "Not Found: Diary not found"}
    if diary_resp["Item"]["section_id"] != section_id:
        return {"statusCode": 404, "body": "Not Found: Diary not found"}

    # get section info
    section_resp = section_table.get_item(Key={"section_id": section_id})
    if section_resp["ResponseMetadata"]["HTTPStatusCode"] != 200:
        return {"statusCode": 500, "body": "Internal Server Error: Section get failed"}
    if "Item" not in section_resp:
        return {"statusCode": 404, "body": "Not Found: Section not found"}

    # section情報の追加
    diary_resp["Item"]["section"] = section_resp["Item"]

    return {
        "statusCode": 200,
        "body": json_dumps(diary_resp["Item"]),
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET",
            "Access-Control-Allow-Headers": "Content-Type,X-CSRF-TOKEN",
        },
    }
