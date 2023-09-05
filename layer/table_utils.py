import json
from decimal import Decimal
from os import getenv

import boto3
from boto3.dynamodb.conditions import Key

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
    response = table.put_item(Item=item, ReturnValues="ALL_NEW")
    if response["ResponseMetadata"]["HTTPStatusCode"] != 200:
        raise DynamoDBError(f"Failed to find {table.name} with {item}")
    if "Attributes" not in response:
        raise IndexError(f"Attributes of {table.name} is not found with {item}")
    return response["Attributes"]


class DynamoDBError(Exception):
    pass
