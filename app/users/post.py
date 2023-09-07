import datetime
import json
import uuid

from responses import post_response
from table_utils import json_dumps, post_item, user_table
from validation import validate_message_not_none, validate_section_id_not_none


def lambda_handler(event, context):
    body = json.loads(event.get("body", "{}"))
    name = body.get("name", None)
    icon = body.get("icon", None)
    email = body.get("email", None)
    section_id = body.get("section_id", None)

    # バリデーション
    error_msgs = []
    is_valid, err_msg = validate_message_not_none(name)
    if not is_valid:
        error_msgs.append("name is invalid")
    is_valid, err_msg = validate_message_not_none(icon)
    if not is_valid:
        error_msgs.append("icon is invalid")
    is_valid, err_msg = validate_message_not_none(email)
    if not is_valid:
        error_msgs.append("email is invalid")
    is_valid, err_msg = validate_section_id_not_none(section_id)
    if not is_valid:
        error_msgs.append(err_msg)
    if len(error_msgs) > 0:
        return post_response(400, "\n".join(error_msgs))

    user_id = str(uuid.uuid4())
    now = str(datetime.datetime.now().isoformat())
    item = {
        "user_id": user_id,
        "name": name,
        "icon": icon,
        "email": email,
        "section_id": section_id,
        "created_at": now,
        "updated_at": now,
    }

    try:
        response = post_item(user_table, item)
    except Exception as e:
        return post_response(500, json_dumps(e))
    return post_response(200, json_dumps(response))
