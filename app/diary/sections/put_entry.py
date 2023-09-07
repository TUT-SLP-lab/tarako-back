import json
from datetime import datetime

from responses import put_response
from table_utils import (
    DynamoDBError,
    get_item,
    json_dumps,
    put_item,
    section_diary_table,
    section_table,
)
from validation import (
    validate_diary_id_not_none,
    validate_message,
    validate_section_id_not_none,
    validate_serious_not_none,
    validate_user_ids_not_none,
)


def lambda_handler(event, context):
    ppm = event.get("pathParameters", {})
    if ppm is None:
        return put_response(400, "Bad Request: Invalid path parameters")

    section_id = ppm.get("section_id")
    diary_id = ppm.get("diary_id")
    body = event.get("body", "{}")

    if body is None:
        return put_response(400, "Bad Request: Invalid body")
    body = json.loads(body)

    details = body.get("details", None)
    serious = body.get("serious", None)
    user_ids = body.get("user_ids", None)

    # バリデーション
    error_messages = []
    is_valid, err_msg = validate_section_id_not_none(section_id)
    if not is_valid:
        error_messages.append(err_msg)
    is_valid, err_msg = validate_diary_id_not_none(diary_id)
    if not is_valid:
        error_messages.append(err_msg)
    is_valid, err_msg = validate_message(details)
    if not is_valid:
        error_messages.append("Invalid details")
    is_valid, err_msg = validate_serious_not_none(serious)
    if not is_valid:
        error_messages.append(err_msg)
    is_valid, err_msg = validate_user_ids_not_none(user_ids)
    if not is_valid:
        error_messages.append(err_msg)

    if len(error_messages) > 0:
        return put_response(400, "\n".join(error_messages))

    section_id = int(section_id)
    serious = int(serious)

    try:
        # get diary
        diary = get_item(section_diary_table, "diary_id", diary_id)

        # update
        UpdateExpression = "set details=:d, serious=:s, user_ids=:u, updated_at=:upd"
        ExpressionAttributeValues = {
            ":d": details,
            ":s": serious,
            ":u": user_ids,
            ":upd": datetime.now().isoformat(),
        }
        diary = put_item(
            section_diary_table,
            "diary_id",
            diary_id,
            UpdateExpression,
            ExpressionAttributeValues,
        )
    except DynamoDBError as e:
        return put_response(500, f"Internal Server Error: DynamoDB Error: {e}")
    except IndexError as e:
        return put_response(404, f"Failed to find diary_id: {diary_id}")

    return put_response(200, json_dumps(diary))
