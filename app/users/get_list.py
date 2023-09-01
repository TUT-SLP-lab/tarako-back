import json


def lambda_handler(event, context):
    qsp = event.get("queryStringParameters")
    if qsp:
        section = qsp.get("section")

        # バリデーション
        if section and not isinstance(section, str):
            return {"statusCode": 400, "body": "Bad Request: Invalid section"}

    # ここに処理を書く
    example = [
        {
            "user_id": "4f73ab32-21bf-47ef-a119-fa024bc2b9cc",
            "name": "田中夏子",
            "description": "田中夏子です。よろしくお願いします。趣味は読書です。",
            "section": {
                "section_id": 0,
                "name": "営業課",
                "created_at": "2020-01-01T00:00:00+09:00",
                "updated_at": "2020-01-01T00:00:00+09:00",
            },
            "email": "tanaka.natsuko@tarako",
            "icon": "/user_1.png",
        },
        {
            "user_id": "595c060d-8417-4ac8-bcb5-c8e733dc64e0",
            "name": "山田太郎",
            "description": "山田太郎です。よろしくお願いします。趣味は野球です。",
            "section": {
                "section_id": 0,
                "name": "営業課",
                "created_at": "2020-01-01T00:00:00+09:00",
                "updated_at": "2020-01-01T00:00:00+09:00",
            },
            "email": "yamada.taro@tarako",
            "icon": "/user_2.png",
        },
        {
            "user_id": "e08bf311-b1bc-4a38-bac1-374c3ede7203",
            "name": "管理五郎",
            "description": "管理者五郎です。よろしくお願いします。人と関わる仕事が好きです。",
            "section": {
                "section_id": 0,
                "name": "管理課",
                "created_at": "2020-01-01T00:00:00+09:00",
                "updated_at": "2020-01-01T00:00:00+09:00",
            },
            "email": "admin.goro@tarako",
            "icon": "/admin.png",
        },
    ]

    return {
        "statusCode": 200,
        "body": json.dumps(example),
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET",
            "Access-Control-Allow-Headers": "Content-Type,X-CSRF-TOKEN",
        },
    }
