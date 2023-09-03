import json
from decimal import Decimal
from os import getenv

import boto3

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
    response = table.scan(**option)
    if response["ResponseMetadata"]["HTTPStatusCode"] != 200:
        raise DynamoDBError()
    return response["Items"]


class DynamoDBError(Exception):
    pass
