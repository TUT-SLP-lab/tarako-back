from boto3.dynamodb.conditions import Key
from table_utils import DynamoDBError, get_items, json_dumps, task_table


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
    if from_datetime and not isinstance(from_datetime, str):
        error_strings.append(
            "Invalid from_start_datetime query"
            if is_start_datetime
            else "Invalid from_last_status_datetime query"
        )
    if to_datetime and not isinstance(to_datetime, str):
        error_strings.append(
            "Invalid to_start_datetime query"
            if is_start_datetime
            else "Invalid to_last_status_datetime query"
        )
    if status and status not in ["in_progress", "completed"]:
        error_strings.append("Invalid status query")
    if not_assigned is None and user_ids:
        for user_id_ in user_ids:  # NOTE: user_idはlistで与えられる
            if not isinstance(user_id_, str):
                error_strings.append("Invalid user_id query")
                break

    if len(error_strings) > 0:
        return {
            "statusCode": 400,
            "body": json_dumps({"errors": "\n".join(error_strings)}),
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET",
                "Access-Control-Allow-Headers": "Content-Type,X-CSRF-TOKEN",
            },
        }

    # Make query
    if not_assigned:
        # not_assignedがTrueの場合は、assigned_toが存在しないアイテムを取得する
        user_ids = [""]
        has_user_query = True
    else:
        has_user_query = user_ids is not None
    completed_query = (
        None if status is None else Key("completed").eq(get_status_string(status))
    )
    datetime_range = (
        None
        if not (from_datetime or to_datetime)
        else get_datetime_range(datetime_key_name, from_datetime, to_datetime)
    )

    result = get_result(
        has_user_query,
        datetime_range,
        completed_query,
        is_start_datetime,
        user_ids,
        status,
    )

    return {
        "statusCode": 200,
        "body": json_dumps(result),
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET",
            "Access-Control-Allow-Headers": "Content-Type,X-CSRF-TOKEN",
        },
    }


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


def get_result(
    has_user_query, datetime_range, completed_query, is_start_datetime, user_ids, status
):
    try:
        result = None
        index_name = ""
        if has_user_query and datetime_range:
            index_name = (
                "UserStartedAtIndex" if is_start_datetime else "UserLastStatusAtIndex"
            )
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
            index_name = (
                "CompletedStartedAtIndex"
                if is_start_datetime
                else "CompletedLastStatusAtIndex"
            )
            expr = completed_query & datetime_range
        elif has_user_query:
            index_name = "AssignedToIndex"
            result = []
            for user_id_ in user_ids:
                expr = Key("assigned_to").eq(user_id_)
                result.extend(get_items(task_table, index_name, expr))
        elif datetime_range:
            index_name = "StartedAtIndex" if is_start_datetime else "LastStatusAtIndex"
            expr = datetime_range
        elif completed_query:
            index_name = "CompletedIndex"
            expr = completed_query
        else:
            result = task_table.scan()["Items"]

        if result is None:
            result = get_items(task_table, index_name, expr)
    except DynamoDBError:
        return {"statusCode": 500, "body": "DynamoDB Error"}
    return result
