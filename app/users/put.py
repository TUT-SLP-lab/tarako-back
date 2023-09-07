import datetime
import json

from responses import put_response
from table_utils import json_dumps, put_item, user_table
from validation import (
    validate_message_not_none,
    validate_section_id_not_none,
    validate_user_id_not_none,
)


def lambda_handler(event, context):
    user_id = event.get("pathParameters", {}).get("user_id")

    is_valid, err_msg = validate_user_id_not_none(user_id)
    if not is_valid:
        return put_response(400, err_msg)
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
        return put_response(400, json_dumps("\n".join(error_msgs)))

    now = datetime.datetime.now().isoformat()
    # nameは予約語なので、#nameとしている
    expression = "SET #name=:n, icon=:i, email=:e, section_id=:s, updated_at=:u"
    exp_att_names = {"#name": "name"}
    vals = {
        ":n": name,
        ":i": icon,
        ":e": email,
        ":s": section_id,
        ":u": now,
    }
    try:
        response = put_item(user_table, "user_id", user_id, expression, vals, exp_att_names)
    except Exception as e:
        return put_response(500, json_dumps(str(e)))

    return put_response(200, json_dumps(response))
