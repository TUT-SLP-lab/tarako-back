from boto3.dynamodb.conditions import Key
from responses import get_response
from table_utils import get_all_items, get_items, json_dumps, user_table
from validation import validate_section_id


def lambda_handler(event, context):
    qsp = event.get("queryStringParameters")
    if qsp:
        section_id = qsp.get("section_id", None)
    else:
        section_id = None

    is_valid, err_msg = validate_section_id(section_id)
    if not is_valid:
        return get_response(400, err_msg)
    try:
        if section_id:
            section_id = int(section_id)
            response = get_items(user_table, "SectionIndex", Key("section_id").eq(section_id))
        else:
            response = get_all_items(user_table)
    except Exception as e:
        return get_response(500, json_dumps(e))

    return get_response(200, json_dumps(response))
