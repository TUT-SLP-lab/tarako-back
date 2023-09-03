import json
from decimal import Decimal
from os import getenv

import boto3
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

# テーブルの定義
dynamodb = boto3.resource("dynamodb")
user_table = dynamodb.Table(USER_TABLE_NAME)
section_table = dynamodb.Table(SECTION_TABLE_NAME)
task_table = dynamodb.Table(TASK_TABLE_NAME)
user_diary_table = dynamodb.Table(USER_DIARY_TABLE_NAME)
section_diary_table = dynamodb.Table(SECTION_DIARY_TABLE_NAME)


def translate_object(obj):
    if isinstance(obj, Decimal):
        return int(obj)
    if isinstance(obj, set):
        return list(obj)
    return obj


def json_dumps(obj):
    return json.dumps(obj, default=translate_object)


def get_items(table, index_name, expr) -> list:
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
        raise DynamoDBError()
    return response["Items"]


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
