import json

from boto3.dynamodb.conditions import Key

from table_utils import DynamoDBError, get_items, json_dumps, task_table


def lambda_handler(event, context):
    qsp = event.get("queryStringParameters")
    if qsp:
        not_assigned_by = qsp.get("not_assigned_by", None)
        from_datetime = qsp.get("from_start_datetime", None)
        to_datetime = qsp.get("to_start_datetime", None)
        if from_datetime or to_datetime:
            is_start_datetime = True
        else:
            is_start_datetime = False
            from_datetime = qsp.get("from_last_status", None)
            to_datetime = qsp.get("to_last_status", None)
        status = qsp.get("status", None)
    else:
        from_datetime = None
        to_datetime = None
        from_datetime = None
        to_datetime = None
        status = None
    mqsp = event.get("multiValueQueryStringParameters")
    if mqsp:
        user_ids = mqsp.get("user_id", None)
    else:
        user_ids = None

    # バリデーション
    error_strings = []
    if not_assigned_by and not isinstance(not_assigned_by, bool):
        error_strings.append("Invalid not_assigned_by query")
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
    if user_ids:
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
    has_user_query = user_ids is not None
    has_completed_query = status is not None
    if has_completed_query:
        completed_query = Key("completed").eq(
            "true" if status == "completed" else "false"
        )
    datetime_range = None
    if from_datetime or to_datetime:
        key_name = "started_at" if is_start_datetime else "last_status_at"
        if from_datetime and to_datetime:
            datetime_range = Key(key_name).between(from_datetime, to_datetime)
        elif from_datetime:
            datetime_range = Key(key_name).gte(from_datetime)
        else:
            datetime_range = Key(key_name).lte(to_datetime)

    try:
        option = {}
        result = None
        index_name = ""
        if has_user_query and datetime_range:
            index_name = (
                "UserStartedAtIndex" if is_start_datetime else "UserLastStatusAtIndex"
            )
            result = []
            for user_id_ in user_ids:
                expr = Key("assigned_to").eq(user_id_) & datetime_range
                result.extend(get_items(task_table, index_name, expr))
            # 3つのクエリがある場合は、更に絞り込みが必要
            # NOTE: あらかじめ大量に絞り込めるものを優先して絞った
            if has_completed_query:
                status = "true" if status == "completed" else "false"
                result = [item for item in result if item["completed"] == status]
        elif has_user_query and has_completed_query:
            index_name = "UserStatusIndex"
            result = []
            for user_id_ in user_ids:
                expr = Key("assigned_to").eq(user_id_) & completed_query
                result.extend(get_items(task_table, index_name, expr))
        elif has_completed_query and datetime_range:
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
        elif has_completed_query:
            index_name = "CompletedIndex"
            expr = completed_query

        if result is None:
            result = get_items(task_table, index_name, expr)
    except DynamoDBError:
        return {"statusCode": 500, "body": "DynamoDB Error"}

    return {
        "statusCode": 200,
        "body": json_dumps(result),
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET",
            "Access-Control-Allow-Headers": "Content-Type,X-CSRF-TOKEN",
        },
    }
