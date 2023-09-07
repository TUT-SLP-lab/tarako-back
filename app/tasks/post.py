# import cgi
import json
import random
import uuid
from datetime import datetime

from data_formatter import task_to_front
from responses import post_response
from table_utils import add_chat_to_db, json_dumps, post_item, task_table
from validation import validate_file, validate_user_id_not_none

# from io import BytesIO


category_list = [
    "HR",
    "Accounting",
    "GeneralAffairs",
    "Diary",
    "Other",
]


def lambda_handler(event, context):
    # suggest_taskを使用する際にコメントアウトを外す
    # qsp = event.get("queryStringParameters")
    # if qsp:
    #     force_create = qsp.get("force_create", None)
    # else:
    #     force_create = None
    body = event.get("body")
    if body is None:
        return post_response(400, "Bad Request: Invalid body")
    body_json = json.loads(body)

    # BytesIOを使用してボディをファイルポインタとして扱う
    # body_file = BytesIO(body.encode("utf-8"))

    # FieldStorageを使うと、multipart/form-dataの場合に対応できる
    try:
        # form = cgi.FieldStorage(
        #     fp=body_file,
        #     environ={
        #         "REQUEST_METHOD": "POST",
        #         "CONTENT_TYPE": event.get("headers").get("Content-Type"),
        #     },
        # )
        # user_id = form.getfirst("user_id", None)
        # msg = form.getfirst("text", None)
        # reference_task_id = form.getfirst("reference_task_id", None)
        # if "file" in form:
        #     file_item = form["file"]
        #     # 現状では、ファイルは無視する
        #     # file_data = file_item.file.read()  # ファイルデータを読み込む
        # else:
        #     file_item = None
        #     # file_data = None

        user_id = body_json.get("user_id", None)
        msg = body_json.get("text", None)
        reference_task_id = body_json.get("reference_task_id", None)
        file_item = None
    except Exception as e:
        print(e)
        return post_response(400, "Bad Request: Invalid form-data")

    # バリデーションの続き
    error_msg = []
    is_valid, err_msg = validate_user_id_not_none(user_id)
    if not is_valid:
        error_msg.append(err_msg)

    if not (msg or file_item):
        error_msg.append("text or file is required")
    if msg and not isinstance(msg, str):
        error_msg.append("text must be string")
    # fileはバイナリデータ
    if file_item and validate_file(file_item):
        error_msg.append("file must be unique")
    # TODO: ファイルがアップロードされた際の処理を書く
    if not msg:
        error_msg.append("ファイルアップロードが未対応の間、textは必須です")
    if reference_task_id and not isinstance(reference_task_id, str):
        error_msg.append("reference_task_id must be string")

    if error_msg:
        return post_response(400, "\n".join(error_msg))

    # Chatデータベースにメッセージを追加する
    add_chat_to_db(user_id, msg, is_user_message=True)

    # TODO: reference_task_idが指定された場合、タスクの作成時に参照をする
    gpt_output = gen_dummy_data(msg)

    # TODO: 似たタスクがあるかどうかを確認する

    # NOTE: 本来はuser_idからsection_idを取得する
    # 現在は、userの直打ちから持ってきている
    section_id_dict = {
        "4f73ab32-21bf-47ef-a119-fa024bc2b9cc": 0,
        "595c060d-8417-4ac8-bcb5-c8e733dc64e0": 0,
        "e08bf311-b1bc-4a38-bac1-374c3ede7203": 1,
    }
    section_id = int(section_id_dict.get(user_id, 0))

    now = str(datetime.now().isoformat())
    task_id = str(uuid.uuid4())
    task = {
        "task_id": task_id,
        "assigned_to": user_id,
        "section_id": section_id,
        "title": gpt_output.get("title"),
        "category": gpt_output.get("category"),
        "tags": gpt_output.get("tags"),
        "progresses": [{"datetime": now, "percentage": gpt_output.get("progress")}],
        "started_at": now,
        "last_status_at": now,
        "completed": "True" if gpt_output.get("progress") == 100 else "False",
        "serious": gpt_output.get("serious"),
        "details": gpt_output.get("details"),
        "placeholder": 0,  # NOTE: 検索のためのダミーフィールド。dynamodbの弊害
        "created_at": now,
        "updated_at": now,
    }

    # task_tableに追加する
    task = task_to_front(post_item(task_table, task))
    # Chatデータベースにシステムからのメッセージを追加する
    add_chat_to_db(user_id, gpt_output.get("response_message"), is_user_message=False)

    response = {
        "message": gpt_output.get("response_message"),
        "task": task,
    }
    return post_response(201, json_dumps(response))


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
        "progress": random.randint(0, 100),
        "serious": random.randint(0, 5),
        "details": msg,
        "response_message": "タスクを作成しました",
    }
