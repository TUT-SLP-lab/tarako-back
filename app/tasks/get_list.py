from boto3.dynamodb.conditions import Key
from data_formatter import task_to_front
from responses import get_response
from table_utils import DynamoDBError, get_all_items, get_items, json_dumps, task_table
from validation import validate_datetime, validate_status, validate_user_ids


def lambda_handler(event, context):
    qsp = event.get("queryStringParameters")
    if qsp:
        not_assigned = qsp.get("not_assigned", None)
        status = qsp.get("status", None)

        # start_datetimeとlast_status_datetimeは同時に指定できない
        from_datetime = qsp.get("from_start_datetime", None)
        to_datetime = qsp.get("to_start_datetime", None)
        is_start_datetime = True
        datetime_key_name = "started_at"

        if not (from_datetime or to_datetime):
            from_datetime = qsp.get("from_last_status", None)
            to_datetime = qsp.get("to_last_status", None)
            is_start_datetime = False
            datetime_key_name = "last_status_at"
    else:
        not_assigned = None
        from_datetime = None
        to_datetime = None
        is_start_datetime = None
        status = None
    mqsp = event.get("multiValueQueryStringParameters")
    if mqsp:
        user_ids = mqsp.get("user_id", None)
    else:
        user_ids = None

    # バリデーション
    # NOTE: not_assigned は、指定されていれば値はなんでも良いので、バリデーションしない
    error_strings = []
    is_valid, err_msg = validate_datetime(from_datetime, to_datetime)
    if not is_valid:
        error_strings.append(err_msg)
    is_valid, err_msg = validate_status(status)
    if not is_valid:
        error_strings.append(err_msg)
    if not_assigned is None:
        is_valid, err_msg = validate_user_ids(user_ids)
        if not is_valid:
            error_strings.append(err_msg)

    if len(error_strings) > 0:
        return get_response(400, "\n".join(error_strings))

    # Make query
    if not_assigned:
        # NOTE: not_assignedがTrueの場合は、assigned_toが存在しないアイテムを取得する
        user_ids = [""]
        has_user_query = True
    else:
        has_user_query = user_ids is not None
    completed_query = None if status is None else Key("completed").eq(get_status_string(status))
    datetime_range = (
        None
        if not (from_datetime or to_datetime)
        else get_datetime_range(datetime_key_name, from_datetime, to_datetime)
    )

    try:
        result = get_result(
            has_user_query,
            datetime_range,
            completed_query,
            is_start_datetime,
            user_ids,
            status,
        )
    except DynamoDBError as e:
        return get_response(500, f"Internal Server Error: DynamoDB Error: {e}")
    except IndexError as e:
        return get_response(404, json_dumps({"errors": str(e)}))
    except Exception as e:
        return get_response(500, json_dumps({"errors": str(e)}))
    return get_response(200, json_dumps(result))


def get_status_string(status):
    return "True" if status == "completed" else "False"


def get_datetime_range(key_name, from_datetime, to_datetime):
    if from_datetime and to_datetime:
        return Key("started_at").between(from_datetime, to_datetime)
    elif from_datetime:
        return Key("started_at").gte(from_datetime)
    else:
        return Key("started_at").lte(to_datetime)


def user_ids_get_item(user_ids, index_name, append_expr=None):
    result = []
    for user_id_ in user_ids:
        if append_expr:
            expr = Key("assigned_to").eq(user_id_) & append_expr
        else:
            expr = Key("assigned_to").eq(user_id_)
        result.extend(get_items(task_table, index_name, expr))
    return result


def get_result(has_user_query, datetime_range, completed_query, is_start_datetime, user_ids, status):
    result = None
    index_name = ""
    if has_user_query and datetime_range:
        index_name = "UserStartedAtIndex" if is_start_datetime else "UserLastStatusAtIndex"
        result = user_ids_get_item(user_ids, index_name, datetime_range)
        # 3つのクエリがある場合は、更に絞り込みが必要
        # NOTE: あらかじめ大量に絞り込めるものを優先して絞った
        if completed_query:
            tmp = get_status_string(status)
            result = [item for item in result if item["completed"] == tmp]
    elif has_user_query and completed_query:
        index_name = "UserStatusIndex"
        result = []
        for user_id_ in user_ids:
            expr = Key("assigned_to").eq(user_id_) & completed_query
            result.extend(get_items(task_table, index_name, expr))
    elif completed_query and datetime_range:
        index_name = "CompletedStartedAtIndex" if is_start_datetime else "CompletedLastStatusAtIndex"
        expr = completed_query & datetime_range
    elif has_user_query:
        index_name = "AssignedToIndex"
        result = []
        for user_id_ in user_ids:
            expr = Key("assigned_to").eq(user_id_)
            result.extend(get_items(task_table, index_name, expr))
    elif datetime_range:
        index_name = "StartedAtIndex" if is_start_datetime else "LastStatusAtIndex"
        expr = Key("placeholder").eq(0) & datetime_range
    elif completed_query:
        index_name = "CompletedIndex"
        expr = completed_query
    else:
        result = get_all_items(task_table)

    if result is None:
        result = get_items(task_table, index_name, expr)
    return [task_to_front(item) for item in result]
