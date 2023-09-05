import json
import uuid
from datetime import datetime
from decimal import Decimal
from os import getenv

import boto3
from boto3.dynamodb.conditions import Key

# from docx import Document
# from openpyxl import load_workbook

# PR番号
PR_NUM = getenv("PR_NUM", "dev")

# テーブル名
USER_TABLE_NAME = f"UserTable-{PR_NUM}"
SECTION_TABLE_NAME = f"SectionTable-{PR_NUM}"
TASK_TABLE_NAME = f"TasksTable-{PR_NUM}"
USER_DIARY_TABLE_NAME = f"UserDiaryTable-{PR_NUM}"
SECTION_DIARY_TABLE_NAME = f"SectionDiaryTable-{PR_NUM}"
CHAT_HISTORY_TABLE_NAME = f"ChatHistoryTable-{PR_NUM}"

# テーブルの定義
dynamodb = boto3.resource("dynamodb")
user_table = dynamodb.Table(USER_TABLE_NAME)
section_table = dynamodb.Table(SECTION_TABLE_NAME)
task_table = dynamodb.Table(TASK_TABLE_NAME)
user_diary_table = dynamodb.Table(USER_DIARY_TABLE_NAME)
section_diary_table = dynamodb.Table(SECTION_DIARY_TABLE_NAME)
chat_history_table = dynamodb.Table(CHAT_HISTORY_TABLE_NAME)


def translate_object(obj):
    if isinstance(obj, Decimal):
        return int(obj)
    if isinstance(obj, set):
        return list(obj)
    return obj


def json_dumps(obj):
    return json.dumps(obj, default=translate_object, ensure_ascii=False)


def get_all_items(table) -> list:
    """
    テーブルから全てのアイテムを取得する
    Args:
        table (boto3.resource.Table): テーブル
    Returns:
        list: アイテムのリスト
    Raises:
        DynamoDBError: DynamoDBのエラー
    """
    response = table.scan()
    if response["ResponseMetadata"]["HTTPStatusCode"] != 200:
        raise DynamoDBError(f"Failed to find {table.name}")
    if "Items" not in response:
        raise IndexError(f"Items of {table.name} are not found")
    return response["Items"]


def get_items(table, index_name: str, expr: Key) -> list:
    """テーブルからアイテムを取得する

    Args:
        table (boto3.resource.Table): テーブル
        index_name str: インデックス名
        expr: キー条件式

    Returns:
        list: アイテムのリスト

    Raises:
        DynamoDBError: DynamoDBのエラー
    """
    option = {"IndexName": index_name, "KeyConditionExpression": expr}
    response = table.query(**option)
    if response["ResponseMetadata"]["HTTPStatusCode"] != 200:
        raise DynamoDBError(f"Failed to find {table.name} with {expr.get_expression()}")
    if "Items" not in response:
        raise IndexError(
            f"Items of {table.name} are not found with {expr.get_expression()}"
        )
    return response["Items"]


def get_item(table, key: str, value: str) -> dict:
    """テーブルからアイテムを取得する
    Args:
        table (boto3.resource.Table): テーブル
        key (str): キー
        value (str): 値
    Returns:
        dict: アイテム
    Raises:
        DynamoDBError: DynamoDBのエラー
    """
    response = table.get_item(Key={key: value})
    if response["ResponseMetadata"]["HTTPStatusCode"] != 200:
        raise DynamoDBError(f"Failed to find {table.name} with {key}: {value}")
    if "Item" not in response:
        raise IndexError(f"Item of {table.name} is not found with {value}")
    return response["Item"]


def put_item(table, key: str, value: str, UpdExp: str, ExpAtt: dict) -> dict:
    """テーブルにアイテムを追加する
    Args:
        table (boto3.resource.Table): テーブル
        key (str): キー
        value (str): 値
        UpdExp (str): UpdateExpression
        ExpAtt (dict): ExpressionAttributeValues
    Returns:
        dict: アイテム
    Raises:
        DynamoDBError: DynamoDBのエラー
    """
    response = table.update_item(
        Key={key: value},
        UpdateExpression=UpdExp,
        ExpressionAttributeValues=ExpAtt,
        ReturnValues="ALL_NEW",
    )
    if response["ResponseMetadata"]["HTTPStatusCode"] != 200:
        raise DynamoDBError(f"Failed to find {table.name} with {key}: {value}")
    if "Attributes" not in response:
        raise IndexError(f"Attributes of {table.name} is not found with {value}")
    return response["Attributes"]


def post_item(table, item: dict) -> dict:
    """テーブルにアイテムを追加する
    Args:
        table (boto3.resource.Table): テーブル
        item (dict): アイテム
    Returns:
        dict: アイテム
    Raises:
        DynamoDBError: DynamoDBのエラー
    """
    response = table.put_item(Item=item, ReturnValues="NONE")
    if response["ResponseMetadata"]["HTTPStatusCode"] != 200:
        raise DynamoDBError(f"Failed to find {table.name}")
    return item


class DynamoDBError(Exception):
    pass


def validate_file(file_item):
    # ファイル形式の検証
    allowed_extensions = [".docx", ".xlsx"]
    filename = file_item.filename.lower()
    if not any(filename.endswith(ext) for ext in allowed_extensions):
        return False
    # ファイルサイズの検証 (例: 5MB以下)
    max_file_size = 5 * 1024 * 1024  # 5MB
    if len(file_item.value) > max_file_size:
        return False
    return True


def validate_uuid(uuid: str) -> bool:
    """UUIDの妥当性を検証する

    Args:
        uuid (str): UUID

    Returns:
        bool: 妥当性
    """
    if uuid is None:
        return False
    try:
        uuid.UUID(uuid)
    except ValueError:
        return False
    return True


def validate_datetime(from_date: str, to_date: str) -> tuple[bool, str]:
    """日付の妥当性を検証する

    Args:
        date (str): 日付

    Returns:
        bool: 妥当性
    """

    class FromToError:
        pass

    try:
        if from_date:
            if not isinstance(from_date, str):
                raise ValueError
            from_date_datetime = datetime.date.fromisoformat(from_date)
        if to_date:
            if not isinstance(to_date, str):
                raise ValueError
            to_date_datetime = datetime.date.fromisoformat(to_date)
        if from_date and to_date and from_date_datetime >= to_date_datetime:
            raise FromToError
        datetime.date.fromisoformat(datetime)
    except ValueError:
        return False, "Invalid format"
    except FromToError:
        return False, "From date is requierd to be earlier than To date"
    return True, None


def validate_user_ids_not_none(user_ids: list) -> tuple[bool, str]:
    """ユーザIDの妥当性を検証する

    Args:
        user_ids (list): ユーザID

    Returns:
        bool: 妥当性
    """
    if user_ids is None:
        return False, "user_id is required"
    return validate_user_ids(user_ids)


def validate_user_ids(user_ids: list) -> tuple[bool, str]:
    """ユーザIDの妥当性を検証する

    Args:
        user_ids (list): ユーザID

    Returns:
        bool: 妥当性
    """
    if user_ids:
        if not isinstance(user_ids, list):
            return False, "user_ids is required to be list"
        for user_id in user_ids:
            is_valid, err_msg = validate_user_id(user_id)
            if not is_valid:
                return False, err_msg
    return True, None


def validate_user_id(user_id: str) -> tuple[bool, str]:
    """ユーザIDの妥当性を検証する

    Args:
        user_id (str): ユーザID

    Returns:
        bool: 妥当性
    """
    if user_id is None:
        return False, "user_id is required"
    if not validate_uuid(user_id):
        return False, "user_id is required to be uuid"
    try:
        get_item(user_table, "user_id", user_id)
    except DynamoDBError as e:
        return False, str(e)
    except IndexError:
        return False, f"user_id is required to exist: {user_id}"
    return True, None


def validate_section_id(section_id: str) -> tuple[bool, str]:
    """セクションIDの妥当性を検証する

    Args:
        section_id (str): セクションID

    Returns:
        bool: 妥当性
    """
    if section_id is None:
        return False, "section_id is required"
    try:
        int(section_id)
    except ValueError:
        return False, "section_id is required to be int"
    # TODO: section_idの存在確認
    return True, None


def validate_task_id(task_id: str) -> tuple[bool, str]:
    """タスクIDの妥当性を検証する

    Args:
        task_id (str): タスクID

    Returns:
        bool: 妥当性
    """
    if task_id is None:
        return False, "task_id is required"
    if not validate_uuid(task_id):
        return False, "task_id is required to be uuid"
    try:
        get_item(task_table, "task_id", task_id)
    except DynamoDBError as e:
        return False, str(e)
    except IndexError:
        return False, f"task_id is required to exist: {task_id}"
    return True, None


def validate_diary_id(diary_id: str) -> tuple[bool, str]:
    """日報IDの妥当性を検証する

    Args:
        diary_id (str): 日報ID

    Returns:
        bool: 妥当性
    """
    if diary_id is None:
        return False, "diary_id is required"
    if not validate_uuid(diary_id):
        return False, "diary_id is required to be uuid"
    return True, None


def validate_date_not_none(date: str) -> tuple[bool, str]:
    """日付の妥当性を検証する

    Args:
        date (str): 日付

    Returns:
        bool: 妥当性
    """
    if date is None:
        return False, "date is required"
    return validate_date(date)


def validate_date(date: str) -> tuple[bool, str]:
    """日付の妥当性を検証する

    Args:
        date (str): 日付

    Returns:
        bool: 妥当性
    """
    try:
        # dateはYYYY-MM-DDの形式
        datetime.date.fromisoformat(date)
    except ValueError:
        return False, "Invalid format"
    return True, None


def validate_details_not_none(details: str) -> tuple[bool, str]:
    """詳細の妥当性を検証する

    Args:
        details (str): 詳細

    Returns:
        bool: 妥当性
    """
    if details is None:
        return False, "details is required"
    return validate_details(details)


def validate_details(details: str) -> tuple[bool, str]:
    """詳細の妥当性を検証する

    Args:
        details (str): 詳細

    Returns:
        bool: 妥当性
    """
    if details is not None and not isinstance(details, str):
        return False, "details is required to be str"
    return True, None


def validate_message_not_none(message: str) -> tuple[bool, str]:
    """メッセージの妥当性を検証する

    Args:
        message (str): メッセージ

    Returns:
        bool: 妥当性
    """
    if message is None:
        return False, "message is required"
    return validate_message(message)


def validate_message(message: str) -> tuple[bool, str]:
    """メッセージの妥当性を検証する

    Args:
        message (str): メッセージ

    Returns:
        bool: 妥当性
    """
    if message is not None and not isinstance(message, str):
        return False, "message is required to be str"
    return True, None


def validate_serious(serious: str) -> tuple[bool, str]:
    """重要度の妥当性を検証する

    Args:
        serious (str): 重要度

    Returns:
        bool: 妥当性
    """
    if serious is None:
        return False, "serious is required"
    try:
        int(serious)
    except ValueError:
        return False, "serious is required to be int"
    return True, None


def validate_status(status: str) -> tuple[bool, str]:
    """ステータスの妥当性を検証する

    Args:
        status (str): ステータス

    Returns:
        bool: 妥当性
    """
    if status and status not in ["completed", "incomplete"]:
        return False, "status is required to be completed or incomplete"
    return True, None


def add_chat_to_db(user_id: str, message: str, is_user_message: bool) -> None:
    """チャット履歴をDBに追加する

    Args:
        user_id (str): ユーザID
        text (str): テキスト
        is_user_message (bool): ユーザメッセージかどうか
    """
    dt = datetime.now().isoformat()
    response = chat_history_table.put_item(
        Item={
            "chat_id": str(uuid.uuid4()),
            "user_id": user_id,
            "timestamp": dt,
            "message": message,
            "is_user_message": is_user_message,
            "created_at": dt,
            "updated_at": dt,
        }
    )
    if response["ResponseMetadata"]["HTTPStatusCode"] != 200:
        raise DynamoDBError("add to chat is failed")


# def extract_text_from_docx(docx_file):
#     doc = Document(docx_file)
#     text = []
#     for paragraph in doc.paragraphs:
#         text.append(paragraph.text)
#     return "\n".join(text)
#
#     # # NOTE: .docx ファイルを解析する場合には、以下のようにする
#     # if 'file' in form:
#     #     file_item = form['file']
#     #     validate_file(file_item)
#     #     docx_text = extract_text_from_docx(file_item.file)
#     #     # docx_text を ChatGPT に渡して処理する
#
#
# def extract_text_from_xlsx(xlsx_file):
#     wb = load_workbook(filename=xlsx_file)
#     text = []
#     for sheet in wb.worksheets:
#         for row in sheet.iter_rows(values_only=True):
#             text.extend(row)
#     return " ".join(map(str, text))
#
#     # # NOTE: .xlsx ファイルを解析する場合には、以下のようにする
#     # if "file" in form:
#     #     file_item = form["file"]
#     #     validate_file(file_item)
#     #     xlsx_text = extract_text_from_xlsx(file_item.file)
#     #     # xlsx_text を ChatGPT に渡して処理する
#
#
# def get_file_extension(filename):
#     # ファイル名から拡張子を取得
#     return filename.split('.')[-1].lower()
#
#     # # NOTE: match構文を使うと、以下のように書ける
#     # match get_file_extension(filename):
#     #     case "docx":
#     #         docx_text = extract_text_from_docx(file_item.file)
#     #         # docx_text を ChatGPT に渡して処理する
#     #     case "xlsx":
#     #         xlsx_text = extract_text_from_xlsx(file_item.file)
#     #         # xlsx_text を ChatGPT に渡して処理する
#     #     case _:
#     #         # 未対応のファイル形式
#     #         return {
#     #             "statusCode": 400,
#     #             "body": json_dumps({"error": "Unsupported file format"}),
#     #         }
