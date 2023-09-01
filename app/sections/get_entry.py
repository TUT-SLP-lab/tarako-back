import json


def lambda_handler(event, context):
    section_id = event.get("pathParameters", {}).get("section_id")
    print(f"************* {section_id} *************")

    if not section_id:
        return {"statusCode": 400, "body": "Bad Request: Missing section_id"}

    # ここに処理を書く
    example = [
        {
            "section_id": 0,
            "name": "営業課",
            "created_at": "2020-01-01T00:00:00+09:00",
            "updated_at": "2020-01-01T00:00:00+09:00",
        },
        {
            "section_id": 1,
            "name": "管理課",
            "created_at": "2020-01-01T00:00:00+09:00",
            "updated_at": "2020-01-01T00:00:00+09:00",
        },
    ]
    # exampleからsection_idと一致するsectionを取り出す。見つからなければ404を返す
    for section in example:
        if section["section_id"] == int(section_id):
            return {"statusCode": 200, "body": json.dumps(section),"headers": {
                        "Access-Control-Allow-Origin": "*",
                        "Access-Control-Allow-Credentials": True,
                        "Access-Control-Allow-Methods": "POST",
                        "Access-Control-Allow-Headers": "Content-Type,X-CSRF-TOKEN",
                    }}
    return {"statusCode": 404, "body": "Section Not Found","headers": {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Credentials": True,
      "Access-Control-Allow-Methods": "POST",
      "Access-Control-Allow-Headers": "Content-Type,X-CSRF-TOKEN",
    }}
