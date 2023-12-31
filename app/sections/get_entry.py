import json

from responses import get_response


def lambda_handler(event, context):
    section_id = event.get("pathParameters", {}).get("section_id")

    if not section_id:
        return get_response(400, "Bad Request: Invalid path parameters")

    # ここに処理を書く
    example = [
        {
            "section_id": 0,
            "name": "営業課",
            "icon": "section_0",
            "created_at": "2020-01-01T00:00:00+09:00",
            "updated_at": "2020-01-01T00:00:00+09:00",
        },
        {
            "section_id": 1,
            "name": "管理課",
            "icon": "section_1",
            "created_at": "2020-01-01T00:00:00+09:00",
            "updated_at": "2020-01-01T00:00:00+09:00",
        },
        {
            "section_id": 2,
            "name": "開発課",
            "icon": "section_2",
            "created_at": "2020-01-01T00:00:00+09:00",
            "updated_at": "2020-01-01T00:00:00+09:00",
        },
        {
            "section_id": 3,
            "name": "人事課",
            "icon": "section_3",
            "created_at": "2020-01-01T00:00:00+09:00",
            "updated_at": "2020-01-01T00:00:00+09:00",
        },
        {
            "section_id": 4,
            "name": "企画課",
            "icon": "section_4",
            "created_at": "2020-01-01T00:00:00+09:00",
            "updated_at": "2020-01-01T00:00:00+09:00",
        },
        {
            "section_id": 5,
            "name": "広報課",
            "icon": "section_5",
            "created_at": "2020-01-01T00:00:00+09:00",
            "updated_at": "2020-01-01T00:00:00+09:00",
        },
    ]
    # exampleからsection_idと一致するsectionを取り出す。見つからなければ404を返す
    for section in example:
        if section["section_id"] == int(section_id):
            return get_response(200, json.dumps(section))
    return get_response(404, "Not Found: Section Not Found")
