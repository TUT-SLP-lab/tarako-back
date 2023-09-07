import datetime

from boto3.dynamodb.conditions import Key
from responses import get_response
from table_utils import (
    DynamoDBError,
    get_all_items,
    get_items,
    json_dumps,
    section_diary_table,
    section_table,
)
from validation import validate_datetime


def lambda_handler(event, context):
    qsp = event.get("queryStringParameters")
    if qsp:
        from_date = qsp.get("from", None)
        to_date = qsp.get("to", None)
    else:
        from_date = None
        to_date = None

    # validation
    is_valid, err_msg = validate_datetime(from_date, to_date)
    if not is_valid:
        return get_response(400, f"Bad Request: {err_msg}")

    try:
        # get all sections
        section_list = get_all_items(section_table)
        # get user diary list between from_date and to_date
        if from_date is None and to_date is None:
            index_name = "SectionIndex"
            datetime_range = None
        else:
            if from_date is not None and to_date is not None:
                datetime_range = Key("date").between(from_date, to_date)
            elif from_date is not None:
                datetime_range = Key("date").gte(from_date)
            elif to_date is not None:
                datetime_range = Key("date").lte(to_date)
            index_name = "SectionDateIndex"

        section_diary_list = []
        for section in section_list:
            section_id_key = Key("section_id").eq(section["section_id"])
            if datetime_range is not None:
                expr = section_id_key & datetime_range
            else:
                expr = section_id_key

            section_diary = get_items(section_diary_table, index_name, expr)

            section_diary_list += section_diary
    except DynamoDBError as e:
        return get_response(500, f"Internal Server Error: DynamoDB Error: {e}")
    except IndexError as e:
        return get_response(404, f"Not Found: {e}")

    return get_response(200, json_dumps(section_diary_list))
