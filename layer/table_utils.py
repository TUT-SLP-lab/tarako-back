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


def put_item(table, key: str, value: str, UpdExp: str, ExpAtt: dict, ExpAttName: dict = None) -> dict:
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
    if ExpAttName is None:
        response = table.update_item(
            Key={key: value},
            UpdateExpression=UpdExp,
            ExpressionAttributeValues=ExpAtt,
            ReturnValues="ALL_NEW",
        )
    else:
        response = table.update_item(
            Key={key: value},
            UpdateExpression=UpdExp,
            ExpressionAttributeValues=ExpAtt,
            ExpressionAttributeNames=ExpAttName,
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


def delete_item(table, key: str, value: str) -> dict:
    """テーブルからアイテムを削除する
    Args:
        table (boto3.resource.Table): テーブル
        key (str): キー
        value (str): 値
    Returns:
        dict: アイテム
    Raises:
        DynamoDBError: DynamoDBのエラー
    """
    response = table.delete_item(Key={key: value}, ReturnValues="NONE")
    if response["ResponseMetadata"]["HTTPStatusCode"] != 200:
        raise DynamoDBError(f"Failed to find {table.name} with {key}: {value}")


class DynamoDBError(Exception):
    pass


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
