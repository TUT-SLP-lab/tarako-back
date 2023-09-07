import json

from responses import get_response


def lambda_handler(event, context):
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

    return get_response(200, json.dumps(example))
