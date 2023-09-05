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

# Init section
section_list = []
random_name = ["営業課", "人事課", "総務課", "経理課", "開発課"]
for idx in range(5):
    section_list.append(idx)
    item = [
        {
            "section_id": idx,
            "name": random_name[idx],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
        },
    ]
    dynamodb.put_item(
        TableName=f"SectionTable-{PR_NUM}",
        Item={k: serializer.serialize(v) for k, v in item[0].items()},
    )

# Init User
items = [
    {
        "user_id": "4f73ab32-21bf-47ef-a119-fa024bc2b9cc",
        "name": "田中夏子",
        "description": "田中夏子です。よろしくお願いします。趣味は読書です。",
        "section_id": random.choice(section_list),
        "email": "tanaka.natsuko@tarako",
        "icon": "/user_1.png",
    },
    {
        "user_id": "595c060d-8417-4ac8-bcb5-c8e733dc64e0",
        "name": "山田太郎",
        "description": "山田太郎です。よろしくお願いします。趣味は野球です。",
        "section_id": random.choice(section_list),
        "email": "yamada.taro@tarako",
        "icon": "/user_2.png",
    },
    {
        "user_id": "e08bf311-b1bc-4a38-bac1-374c3ede7203",
        "name": "管理五郎",
        "description": "管理者五郎です。よろしくお願いします。人と関わる仕事が好きです。",
        "section": random.choice(section_list),
        "email": "admin.goro@tarako",
        "icon": "/admin.png",
    },
]
dynamodb.put_item(
    TableName=f"UserTable-{PR_NUM}",
    Item={k: serializer.serialize(v) for k, v in items[0].items()},
)

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
        "assigned_to": random.choice(user_list),
        "section_id": 1,
        "title": "単体テスト作成",
        "category": "HR",
        "tags": ["人事", "休暇"],
        "progresses": [
            {"datetime": "2020-01-01T00:00:00+09:00", "percentage": 0},
            {"datetime": "2020-01-02T00:00:00+09:00", "percentage": 50},
            {
                "datetime": "2020-01-03T00:00:00+09:00",
                "percentage": 100,
            },
        ],
        "started_at": "2020-01-01T00:00:00+09:00",
        "last_status_at": "2020-01-03T00:00:00+09:00",
        "placeholder": 0,
        "completed": "True",
        "serious": 0,
        "details": "hoge.fugaの単体テストを作成する",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
    }
    dynamodb.put_item(
        TableName=f"TasksTable-{PR_NUM}",
        Item={k: serializer.serialize(v) for k, v in item.items()},
    )
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
    dynamodb.put_item(
        TableName=f"UserDiaryTable-{PR_NUM}",
        Item={k: serializer.serialize(v) for k, v in item.items()},
    )

# Init section dialy
for idx in range(5):
    item = {
        "diary_id": str(uuid.uuid4()),
        "section_id": random.choice(section_list),
        "date": random.choice(date_list),
        "details": "hoge.fugaの単体テストを作成する",
        "serious": random.choice([0, 1, 2, 3, 4, 5]),
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "user_ids": [random.sample(user_list, 2)],
    }
    dynamodb.put_item(
        TableName=f"SectionDiaryTable-{PR_NUM}",
        Item={k: serializer.serialize(v) for k, v in item.items()},
    )
