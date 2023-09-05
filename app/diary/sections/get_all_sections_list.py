import datetime

from boto3.dynamodb.conditions import Key
from table_utils import (
    DynamoDBError,
    get_all_items,
    get_items,
    json_dumps,
    section_diary_table,
    section_table,
)


def lambda_handler(event, context):
    qsp = event.get("queryStringParameters")
    if qsp:
        from_date = qsp.get("from", None)
        to_date = qsp.get("to", None)
    else:
        from_date = None
        to_date = None

    # validation
    if from_date:
        if not isinstance(from_date, str):
            return {"statusCode": 400, "body": "Bad Request: Invalid from_date"}
        try:
            from_date_datetime = datetime.date.fromisoformat(from_date)
        except ValueError:
            return {
                "statusCode": 400,
                "body": "Bad Request: 'from' is invalid date format",
            }
    if to_date:
        if not isinstance(to_date, str):
            return {"statusCode": 400, "body": "Bad Request: Invalid to_date"}
        try:
            to_date_datetime = datetime.date.fromisoformat(to_date)
        except ValueError:
            return {
                "statusCode": 400,
                "body": "Bad Request: 'to' is invalid date format",
            }
    if from_date and to_date and from_date_datetime >= to_date_datetime:
        return {"statusCode": 400, "body": "Bad Request: from_date >= to_date"}

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
        return {"statusCode": 500, "body": f"Internal Server Error: {e}"}
    except IndexError as e:
        return {"statusCode": 404, "body": f"Not Found: {e}"}

    return {
        "statusCode": 200,
        "body": json_dumps(section_diary_list),
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET",
            "Access-Control-Allow-Headers": "Content-Type,X-CSRF-TOKEN",
        },
    }
