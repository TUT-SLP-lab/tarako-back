import random
import uuid
from datetime import datetime

import boto3
from boto3.dynamodb.types import TypeSerializer

PR_NUM = "dev"

dynamodb = boto3.client("dynamodb", region_name="ap-northeast-1")

serializer = TypeSerializer()
user_list = [
    "4f73ab32-21bf-47ef-a119-fa024bc2b9cc",
    "595c060d-8417-4ac8-bcb5-c8e733dc64e0",
    "e08bf311-b1bc-4a38-bac1-374c3ede7203",
]

# Init task
task_ids = []
for idx in range(5):
    item = {
        "task_id": str(uuid.uuid4()),
        "assigned_by": random.choice(user_list),
        "section_id": 1,
        "title": "単体テスト作成",
        "category": "HR",
        "tags": ["人事", "休暇"],
        "progresses": [
            {"datetime": "2020-01-01T00:00:00+09:00", "percentage": 0},
            {"datetime": "2020-01-01T00:00:00+09:00", "percentage": 50},
            {
                "datetime": "2020-01-01T00:00:00+09:00",
                "percentage": 100,
            },
        ],
        "completed": "True",
        "serious": 0,
        "details": "hoge.fugaの単体テストを作成する",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }
    item_dynamodb_json = {k: serializer.serialize(v) for k, v in item.items()}
    option = {
        "TableName": f"TasksTable-{PR_NUM}",
        "Item": item_dynamodb_json,
    }
    dynamodb.put_item(**option)

    task_ids.append(item["task_id"])


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
        "diary_id": str(uuid.uuid4()),
        "section_id": 1,
        "date": random.choice(date_list),
        "details": "hoge.fugaの単体テストを作成する",
        "serious": random.choice([0, 1, 2, 3, 4, 5]),
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "user_id": random.choice(user_list),
        "task_ids": random.sample(task_ids, 2),
    }
    item_dynamodb_json = {k: serializer.serialize(v) for k, v in item.items()}
    option = {
        "TableName": f"UserDiaryTable-{PR_NUM}",
        "Item": item_dynamodb_json,
    }
    dynamodb.put_item(**option)
