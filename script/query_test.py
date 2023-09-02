import random
from datetime import datetime

import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource("dynamodb", region_name="ap-northeast-1")

table = dynamodb.Table("UserDiaryTable-9")

# option = {
#     "KeyConditionExpression": Key("diary_id").eq(
#         "3fa85f64-5717-4562-b3fc-2c963f66afa6"
#     ),
# }

option = {
    "KeyConditionExpression": Key("user_id").eq(
        "3fa85f64-5717-4562-b3fc-2c963f66afa6"
    ),
}

resp = table.query(**option)
print(resp)


# def get_timestamp():
#     rand_minute = int(random.uniform(0, 59))
#     rand_second = int(random.uniform(0, 59))
#     return datetime(2020, 9, 10, 13, rand_minute, rand_second)
#
#
# def get_yesterday_timestamp():
#     rand_minute = int(random.uniform(0, 59))
#     rand_second = int(random.uniform(0, 59))
#     return datetime(2020, 9, 10, 13, rand_minute, rand_second)
#
#
# print(get_yesterday_timestamp().isoformat())
#
# option = {
#     "KeyConditionExpression": "#date between :start_date and :end_date",
#     "ExpressionAttributeNames": {"#date": "created_at"},
#     "ExpressionAttributeValues": {
#         ":start_date": {"S": get_timestamp().isoformat()},
#         ":end_date": {"S": get_yesterday_timestamp().isoformat()},
#     },
# }
#
# resp = table.query(**option)
#
# print(resp)
