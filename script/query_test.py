import random
from datetime import datetime

import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource("dynamodb", region_name="ap-northeast-1")

table = dynamodb.Table("UserDiaryTable-9")

option = {
    "KeyConditionExpression": Key("diary_id").eq(
        "3fa85f64-5717-4562-b3fc-2c963f66afa6"
    ),
}

option = {
    "IndexName": "UserSeriousIndex",
    "KeyConditionExpression": Key("user_id").eq(
        "4f73ab32-21bf-47ef-a119-fa024bc2b9cc"
    ) & Key("serious").eq(0),
}

resp = table.query(**option)
print(resp["Items"])


def get_timestamp():
    rand_minute = int(random.uniform(0, 59))
    rand_second = int(random.uniform(0, 59))
    return datetime(2023, 9, 1, 13, rand_minute, rand_second)


def get_yesterday_timestamp():
    rand_minute = int(random.uniform(0, 59))
    rand_second = int(random.uniform(0, 59))
    return datetime(2019, 9, 1, 13, rand_minute, rand_second)


userid_key = Key("user_id").eq("4f73ab32-21bf-47ef-a119-fa024bc2b9cc")
datetime_between = Key("created_at").between(
    get_yesterday_timestamp().isoformat(), get_timestamp().isoformat()
)

print(get_yesterday_timestamp().isoformat())
print(get_timestamp().isoformat())

option = {
    "IndexName": "UserDateIndex",
    "KeyConditionExpression": userid_key & datetime_between,
}

resp = table.query(**option)

print(resp)
