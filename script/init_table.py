import decimal
import json
import random
import uuid
from datetime import datetime

import boto3

PR_NUM = "9"

dynamodb = boto3.client("dynamodb", region_name="ap-northeast-1")

user_list = [
    "4f73ab32-21bf-47ef-a119-fa024bc2b9cc",
    "595c060d-8417-4ac8-bcb5-c8e733dc64e0",
    "e08bf311-b1bc-4a38-bac1-374c3ede7203",
]

# Init task
task_ids = []
for idx in range(5):
    item = {
        "task_id": {"S": str(uuid.uuid4())},
        "assigned_by": {"S": random.choice(user_list)},
        "title": {"S": "単体テスト作成"},
        "category": {"S": "HR"},
        "tags": {"SS": ["人事", "休暇"]},
        "progresses": {
            "L": [
                {
                    "M": {
                        "datetime": {"S": "2020-01-01T00:00:00+09:00"},
                        "percentage": {"N": "0"},
                    }
                },
                {
                    "M": {
                        "datetime": {"S": "2020-01-01T00:00:00+09:00"},
                        "percentage": {"N": "50"},
                    }
                },
                {
                    "M": {
                        "datetime": {"S": "2020-01-01T00:00:00+09:00"},
                        "percentage": {"N": "100"},
                    }
                },
            ]
        },
        "completed": {"BOOL": True},
        "serious": {"N": "0"},
        "details": {"S": "hoge.fugaの単体テストを作成する"},
        "created_at": {"S": datetime.now().isoformat()},
        "updated_at": {"S": datetime.now().isoformat()},
    }
    option = {
        "TableName": f"TasksTable-{PR_NUM}",
        "Item": item,
    }
    dynamodb.put_item(**option)

    task_ids.append(item["task_id"]["S"])


# Init user daily
date_list = [
    "2023-09-02",
    "2023-09-01",
    "2023-08-31",
    datetime.now().strftime("%Y-%m-%d"),
    datetime.now().strftime("%Y-%m-%d"),
]
user_diary_template = []

for idx in range(5):
    item = {
        "diary_id": {"S": str(uuid.uuid4())},
        "date": {"S": random.choice(date_list)},
        "details": {"S": "hoge.fugaの単体テストを作成する"},
        "serious": {"N": random.choice(["0", "1", "2", "3", "4", "5"])},
        "created_at": {"S": datetime.now().isoformat()},
        "updated_at": {"S": datetime.now().isoformat()},
        "user_id": {"S": random.choice(user_list)},
        "task_ids": {"SS": random.sample(task_ids, 2)},
    }
    option = {
        "TableName": f"UserDiaryTable-{PR_NUM}",
        "Item": item,
    }
    dynamodb.put_item(**option)
