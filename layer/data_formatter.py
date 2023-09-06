def task_to_front(item: dict) -> dict:
    """タスク情報をフロント用に変換する

    Args:
        item (dict): タスク情報

    Returns:
        dict: フロント用タスク情報
    """
    return {
        "task_id": item["task_id"],
        "assigned_to": item["assigned_to"],
        "section_id": item["section_id"],
        "title": item["title"],
        "category": item["category"],
        "tags": item["tags"],
        "progresses": item["progresses"],
        "completed": True if item["completed"] == "True" else False,
        "serious": item["serious"],
        "details": item["details"],
        "created_at": item["created_at"],
        "updated_at": item["updated_at"],
    }
