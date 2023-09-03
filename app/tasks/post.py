import cgi
import random
import uuid
from datetime import datetime
from io import BytesIO

from table_utils import json_dumps, task_table, validate_file

category_list = [
    "HR",
    "Accounting",
    "GeneralAffairs",
    "Diary",
    "Other",
]


def lambda_handler(event, context):
    qsp = event.get("queryStringParameters")
    if qsp:
        force_create = qsp.get("force_create", None)
    else:
        force_create = None  # suggest_taskを使用する際に必要
    body = event.get("body")
    if body is None:
        return {
            "statusCode": 400,
            "body": json_dumps({"error": "Missing request body"}),
        }

    # BytesIOを使用してボディをファイルポインタとして扱う
    body_file = BytesIO(body.encode("utf-8"))

    # FieldStorageを使うと、multipart/form-dataの場合に対応できる
    try:
        form = cgi.FieldStorage(
            fp=body_file,
            environ={"REQUEST_METHOD": "POST"},
            headers={"Content-Type": "multipart/form-data"},
        )
        user_id = form.getfirst("user_id", None)
        msg = form.getfirst("text", None)
        if "file" in form:
            file_item = form["file"]
            file_data = file_item.file.read()  # ファイルデータを読み込む
    except Exception as e:
        print(e)
        return {
            "statusCode": 500,
            "body": json_dumps({"error": "Failed to parse form-data"}),
        }

    # バリデーションの続き
    error_strings = []
    # TODO: user_idが存在するかどうかを確認する
    if not user_id:
        error_strings.append("user_id is required")
    elif not isinstance(user_id, str):
        error_strings.append("user_id must be string")
    if not (msg or file):
        error_strings.append("text or file is required")
    if msg and not isinstance(msg, str):
        error_strings.append("text must be string")
    # fileはバイナリデータ
    if file_item and validate_file(file_item):
        error_strings.append("file must be unique")
    elif len(file) == 1:
        file = file[0]
        if isinstance(file, str):
            error_strings.append("file must be string")

    # TODO: ファイルがアップロードされた際の処理を書く
    if not msg:
        error_strings.append("ファイルアップロードが未対応の間、textは必須です")

    gpt_output = gen_dummy_data(msg)

    # TODO: 似たタスクがあるかどうかを確認する

    now = datetime.now().isoformat()
    task_id = str(uuid.uuid4())
    task = {
        "task_id": task_id,
        "assigned_to": user_id,
        "title": gpt_output.get("title"),
        "category": gpt_output.get("category"),
        "tags": gpt_output.get("tags"),
        "progresses": [{"datetime": now, "percentage": gpt_output.get("progress")}],
        "started_at": now,
        "last_status_at": now,
        "completed": gpt_output.get("progress") == 100,
        "serious": gpt_output.get("serious"),
        "details": gpt_output.get("details"),
        "placeholder": "",  # NOTE: 検索のためのダミーフィールド。dynamodbの弊害
        "created_at": now,
        "updated_at": now,
    }

    # task_tableに追加する
    task_table.put_item(Item=task)
    return {"statusCode": 200, "body": json_dumps(task)}


def check_suggest_task():
    """
    タスクの提案を行うかどうかを判定する

    備考: ChatGPTと合体するまで保留
    """
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


def gen_dummy_data(msg):
    """ChatGPTから返ってくるであろう出力を生成する"""
    return {
        "title": msg,
        "category": random.choice(category_list),
        "tags": random.sample(dummy_tags, random.randint(1, len(dummy_tags))),
        "progress": random.int(0, 100),
        "serious": random.randint(0, 5),
        "details": msg,
    }
