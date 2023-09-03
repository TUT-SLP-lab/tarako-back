import json
import uuid
from datetime import datetime

from table_utils import json_dumps, task_table

category_list = [
    "HR",
    "Accounting",
    "GeneralAffairs",
    "Diary",
    "Other",
]


def lambda_handler(event, context):
    ppm = event.get("pathParameters")
    if ppm:
        user_id = ppm.get("user_id")
    qsp = event.get("queryStringParameters")
    if qsp:
        force_create = qsp.get("force_create", None)
    else:
        force_create = None
    body = json.loads(event.get("body", None))

    if user_id is None or not isinstance(user_id, str):
        return {"statusCode": 400, "body": "Bad Request: Invalid user_id"}
    # TODO: bodyの中身のバリデーションも書く
    if not body:
        return {"statusCode": 400, "body": "Bad Request: Empty request body"}

    task_id = str(uuid.uuid4())
    msg = body.get("message")
    # TODO: ファイルがアップロードされた際の処理も書く

    gpt_output = gen_dummy_data()

    # TODO: 似たタスクがあるかどうかを確認する

    now = datetime.now().isoformat()
    task = {
        "task_id": task_id,
        "assigned_by": user_id,
        "title": msg,
        "category": gpt_output.get("category"),
        "tags": gpt_output.get("tags"),
        "progresses": [
            {
                "datetime": now,
                "percentage": gpt_output.get("progress"),
            }
        ],
        "completed": gpt_output.get("progress") == 100,
        "serious": gpt_output.get("serious"),
        "details": msg,
        "created_at": now,
        "updated_at": now,
    }

    # task_tableに追加する
    task_table.put_item(Item=task)
    # task_tableから再取得する
    task = task_table.get_item(Key={"task_id": task_id}).get("Item")

    return {
        "statusCode": 200,
        "body": json_dumps(task),
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST",
            "Access-Control-Allow-Headers": "Content-Type,X-CSRF-TOKEN",
        },
    }


def check_suggest_task():
    """タスクの提案を行うかどうかを判定する"""
    pass


# HACK: ここから下は、ダミーデータを生成するための諸々
# 本番までに取り除きたい

dummy_tags = [
    "人事",
    "休暇",
    "経理",
    "総務",
    "日報",
    "その他",
]


def gen_dummy_data():
    """ChatGPTから返ってくるであろう出力を生成する"""
    return {
        "category": random.choice(category_list),
        "tags": random.sample(dummy_tags, random.randint(1, len(dummy_tags))),
        "progress": random.int(0, 100),
        "serious": random.randint(0, 5),
    }
