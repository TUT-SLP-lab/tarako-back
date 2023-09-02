from decimal import Decimal
import json
from os import getenv

import boto3

# PR番号
PR_NUMBER = getenv('PR_NUMBER', 'dev')

# テーブル名
USER_TABLE_NAME=f"UserDiaryTable-{PR_NUMBER}"
SECTION_TABLE_NAME=f"SectionTable-{PR_NUMBER}"
TASK_TABLE_NAME=f"TaskTable-{PR_NUMBER}"
USER_DIARY_TABLE_NAME=f"UserDiaryTable-{PR_NUMBER}"
SECTION_DIARY_TABLE_NAME=f"SectionDiaryTable-{PR_NUMBER}"

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