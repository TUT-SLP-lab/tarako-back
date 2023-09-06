import datetime
import uuid
from typing import Optional

from table_utils import DynamoDBError, get_item, task_table, user_table


def validate_file(file_item):
    # ファイル形式の検証
    allowed_extensions = [".docx", ".xlsx"]
    filename = file_item.filename.lower()
    if not any(filename.endswith(ext) for ext in allowed_extensions):
        return False
    # ファイルサイズの検証 (例: 5MB以下)
    max_file_size = 5 * 1024 * 1024  # 5MB
    if len(file_item.value) > max_file_size:
        return False
    return True


def validate_uuid_not_none(uuid_str: str) -> bool:
    """UUIDの妥当性を検証する

    Args:
        uuid (str): UUID

    Returns:
        bool: 妥当性
    """
    if uuid_str is None:
        return False
    try:
        uuid.UUID(uuid_str)
    except ValueError:
        return False
    return True


def validate_datetime(from_date: str, to_date: str) -> tuple[bool, str]:
    """日付の妥当性を検証する

    Args:
        date (str): 日付

    Returns:
        bool: 妥当性
    """

    class FromToError(Exception):
        pass

    try:
        if from_date:
            if not isinstance(from_date, str):
                raise ValueError
            from_date_datetime = datetime.date.fromisoformat(from_date)
        if to_date:
            if not isinstance(to_date, str):
                raise ValueError
            to_date_datetime = datetime.date.fromisoformat(to_date)
        if from_date and to_date:
            if from_date_datetime >= to_date_datetime:
                raise FromToError
    except ValueError:
        return False, "Invalid format"
    except FromToError:
        return False, "From date is requierd to be earlier than To date"
    return True, None


def validate_user_ids_not_none(user_ids: list) -> tuple[bool, Optional[str]]:
    """ユーザIDの妥当性を検証する

    Args:
        user_ids (list): ユーザID

    Returns:
        bool: 妥当性
    """
    if user_ids is None:
        return False, "user_id is required"
    return validate_user_ids(user_ids)


def validate_user_ids(user_ids: list) -> tuple[bool, Optional[str]]:
    """ユーザIDの妥当性を検証する

    Args:
        user_ids (list): ユーザID

    Returns:
        bool: 妥当性
    """
    if user_ids:
        if not isinstance(user_ids, list):
            return False, "user_ids is required to be list"
        for user_id in user_ids:
            is_valid, err_msg = validate_user_id_not_none(user_id)
            if not is_valid:
                return False, err_msg
    return True, None


def validate_user_id_not_none(user_id: str) -> tuple[bool, Optional[str]]:
    """ユーザIDの妥当性を検証する

    Args:
        user_id (str): ユーザID

    Returns:
        bool: 妥当性
    """
    if user_id is None:
        return False, "user_id is required"
    if not validate_uuid_not_none(user_id):
        return False, "user_id is required to be uuid"
    try:
        get_item(user_table, "user_id", user_id)
    except DynamoDBError as e:
        return False, str(e)
    except IndexError:
        return False, f"user_id is required to exist: {user_id}"
    return True, None


def validate_section_id_not_none(section_id: str) -> tuple[bool, Optional[str]]:
    """セクションIDの妥当性を検証する

    Args:
        section_id (str): セクションID

    Returns:
        bool: 妥当性
    """
    if section_id is None:
        return False, "section_id is required"
    try:
        int(section_id)
    except ValueError:
        return False, "section_id is required to be int"
    # TODO: section_idの存在確認
    return True, None


def validate_task_id_not_none(task_id: str) -> tuple[bool, Optional[str]]:
    """タスクIDの妥当性を検証する

    Args:
        task_id (str): タスクID

    Returns:
        bool: 妥当性
    """
    if task_id is None:
        return False, "task_id is required"
    if not validate_uuid_not_none(task_id):
        return False, "task_id is required to be uuid"
    try:
        get_item(task_table, "task_id", task_id)
    except DynamoDBError as e:
        return False, str(e)
    except IndexError:
        return False, f"task_id is required to exist: {task_id}"
    return True, None


def validate_diary_id_not_none(diary_id: str) -> tuple[bool, Optional[str]]:
    """日報IDの妥当性を検証する

    Args:
        diary_id (str): 日報ID

    Returns:
        bool: 妥当性
    """
    if diary_id is None:
        return False, "diary_id is required"
    if not validate_uuid_not_none(diary_id):
        return False, "diary_id is required to be uuid"
    return True, None


def validate_date_not_none(date: str) -> tuple[bool, Optional[str]]:
    """日付の妥当性を検証する

    Args:
        date (str): 日付

    Returns:
        bool: 妥当性
    """
    if date is None:
        return False, "date is required"
    return validate_date(date)


def validate_date(date: str) -> tuple[bool, Optional[str]]:
    """日付の妥当性を検証する

    Args:
        date (str): 日付

    Returns:
        bool: 妥当性
    """
    if date:
        try:
            # dateはYYYY-MM-DDの形式
            datetime.date.fromisoformat(date)
        except ValueError:
            return False, "Invalid format"
    return True, None


def validate_details_not_none(details: str) -> tuple[bool, Optional[str]]:
    """詳細の妥当性を検証する

    Args:
        details (str): 詳細

    Returns:
        bool: 妥当性
    """
    if details is None:
        return False, "details is required"
    return validate_details(details)


def validate_details(details: str) -> tuple[bool, Optional[str]]:
    """詳細の妥当性を検証する

    Args:
        details (str): 詳細

    Returns:
        bool: 妥当性
    """
    if details:
        if not isinstance(details, str):
            return False, "details is required to be str"
    return True, None


def validate_message_not_none(message: str) -> tuple[bool, Optional[str]]:
    """メッセージの妥当性を検証する

    Args:
        message (str): メッセージ

    Returns:
        bool: 妥当性
    """
    if message is None:
        return False, "message is required"
    return validate_message(message)


def validate_message(message: str) -> tuple[bool, Optional[str]]:
    """メッセージの妥当性を検証する

    Args:
        message (str): メッセージ

    Returns:
        bool: 妥当性
    """
    if message:
        if not isinstance(message, str):
            return False, "message is required to be str"
    return True, None


def validate_serious_not_none(serious: str) -> tuple[bool, Optional[str]]:
    """重要度の妥当性を検証する

    Args:
        serious (str): 重要度

    Returns:
        bool: 妥当性
    """
    if serious is None:
        return False, "serious is required"
    try:
        int(serious)
    except ValueError:
        return False, "serious is required to be int"
    return True, None


def validate_status(status: str) -> tuple[bool, Optional[str]]:
    """ステータスの妥当性を検証する

    Args:
        status (str): ステータス

    Returns:
        bool: 妥当性
    """
    if status:
        if status not in ["completed", "incomplete"]:
            return False, "status is required to be completed or incomplete"
    return True, None
