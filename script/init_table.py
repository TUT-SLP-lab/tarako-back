import decimal
import json

import boto3

PR_NUM = "dev"

dynamodb = boto3.client("dynamodb", region_name="ap-northeast-1")

UserDiaryTable = f"UserDiaryTable-{PR_NUM}"


with open("init_items/user_diary_table.json") as json_file:
    items = json.load(json_file, parse_float=decimal.Decimal)
    for item in items:
        option = {
            "TableName": UserDiaryTable,
            "Item": item,
        }
        print(option)
        dynamodb.put_item(**option)
