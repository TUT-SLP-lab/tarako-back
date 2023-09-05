import json
import os

import openai

openai.apikey = os.environ["OPENAI_API_KEY"]
CHATGPT_MODEL = "gpt-3.5-turbo"


def gen_create_task_prompt(msg):
    return f"""
次の内容のタスクを作成してください。
もし、似た内容のタスクがあった場合、それも教えてください。
```
{msg}
```
"""


def create_task_function(category_list):
    return {
        "name": "create_task",
        "description": "タスクオブジェクトを作成する",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "タスク名"},
                "category": {
                    "type": "string",
                    "description": "タスク名のカテゴリ",
                    "enum": category_list,
                },
                "tags": {
                    "type": "array",
                    "description": "タスクのタグ(複数可)",
                    "items": {"type": "string"},
                },
                "progress": {
                    "type": "integer",
                    "description": "タスクの進捗(0~100)",
                    "minimum": 0,
                    "maximum": 100,
                },
                "serious": {
                    "type": "integer",
                    "description": "タスクの深刻度(0~5)",
                    "minimum": 0,
                    "maximum": 5,
                },
                "details": {
                    "type": "string",
                    "description": "タスクの詳細。タイトルでは表現できない内容を記述する",
                },
                "response_message": {
                    "type": "string",
                    "description": "タスクを作成したことをユーザに伝えるメッセージ",
                },
                "required": [
                    "title",
                    "category",
                    "tags",
                    "progress",
                    "serious",
                    "details",
                    "response_message",
                ],
            },
        },
    }


def suggest_similer_task_function(task_title_dict: dict[str, str]):
    return {
        "name": "suggest_similer_task",
        "description": "似たようなタスクがあった場合、タスクタイトルとIDのペアを返す",
        "parameters": {
            "type": "object",
            "properties": {
                "task": {
                    "type": "object",
                    "description": "タスクオブジェクト",
                    "properties": {
                        "title": {"type": "string", "description": "タスク名"},
                        "task_id": {"type": "string", "description": "タスクID"},
                    },
                    "enum": task_title_dict,
                },
                "required": ["title", "task_id"],
            },
        },
    }


def gen_task_data(
    msg: str, category_list: list[str], task_title_dict: dict[str, str] = {}
):
    response = openai.ChatCompletion.create(
        model=CHATGPT_MODEL,
        messages=[
            {"role": "user", "content": gen_create_task_prompt(msg)},
        ],
        functions=[
            create_task_function(category_list),
            suggest_similer_task_function(task_title_dict),
        ],
    )
    if "function_call" not in response["choices"][0]["message"]:
        raise FunctionCallingError("function_callがありません")
    task = None
    suggest_task = None
    if response["choices"][0]["message"]["function_call"]["name"] == "create_task":
        task_str = response["choices"][0]["message"]["function_call"]["arguments"]
        task = json.loads(task_str)
    elif (
        response["choices"][0]["message"]["function_call"]["name"]
        == "suggest_similer_task"
    ):
        suggest_task_str = response["choices"][0]["message"]["function_call"][
            "arguments"
        ]
        suggest_task = json.loads(suggest_task_str)
    return task, suggest_task


def gen_create_user_diary_prompt(msg, task_dict: dict[str, str]):
    return f"""
次の内容は事務員の今日タスクです。これらの内容から日報を作成してください。
```
{json.dumps(task_dict)}

最後に従業員の一言です．{msg}
```
"""


def create_user_diary_function():
    return {
        "name": "create_diary",
        "description": "複数タスクの情報から日報を作成する",
        "parameters": {
            "type": "object",
            "properties": {
                "details": {
                    "type": "string",
                    "description": "日報の詳細。タスクの情報をできるだけ網羅できていて，"
                    + "分かりやすい内容でMarkdown形式で記述する．",
                },
                "ai_analysis": {
                    "type": "string",
                    "description": "メッセージやタスクからAIが自動で分析した内容を記述する．"
                    + "思いやりがあって，従業員がやる気になるような内容を記述する．",
                },
                "serious": {
                    "type": "integer",
                    "description": "日報の深刻度(0~5)",
                },
                "required": [
                    "title",
                    "details",
                    "serious",
                ],
            },
        },
    }


def gen_user_diary_data(msg: str, task_dict: dict[str, str] = {}):
    response = openai.ChatCompletion.create(
        model=CHATGPT_MODEL,
        messages=[
            {"role": "user", "content": gen_create_user_diary_prompt(task_dict, msg)},
        ],
        functions=[
            create_user_diary_function(),
        ],
    )
    if "function_call" not in response["choices"][0]["message"]:
        raise FunctionCallingError("function_callがありません")
    diary = None
    if response["choices"][0]["message"]["function_call"]["name"] == "create_diary":
        diary_str = response["choices"][0]["message"]["function_call"]["arguments"]
        diary = json.loads(diary_str)
    return diary


class FunctionCallingError(Exception):
    pass
