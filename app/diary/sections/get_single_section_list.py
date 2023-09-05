import datetime

from boto3.dynamodb.conditions import Key
from table_utils import (DynamoDBError, get_item, get_items, json_dumps,
                         section_diary_table, section_table)


def lambda_handler(event, context):
    ppm = event.get("pathParameters", {})
    if ppm:
        section_id = ppm.get("section_id")
    else:
        section_id = None
    section_id = ppm.get("section_id", None)

    qsp = event.get("queryStringParameters", None)
    if qsp:
        from_date = qsp.get("from")
        to_date = qsp.get("to")
    else:
        from_date = None
        to_date = None

    # section_idのバリデーション
    if section_id is None:
        return {"statusCode": 400, "body": "Bad Request: section_id is None"}
    try:
        section_id = int(section_id)
    except ValueError:
        return {"statusCode": 400, "body": "Bad Request: section_id is not int"}
    # 日付のバリデーション
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
        # get section diary
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

        section_id_key = Key("section_id").eq(section_id)
        if datetime_range is not None:
            expr = section_id_key & datetime_range
        else:
            expr = section_id_key

        section_diary = get_items(section_diary_table, index_name, expr)

    except DynamoDBError as e:
        return {"statusCode": 500, "body": f"error: {e}"}
    except IndexError as e:
        return {"statusCode": 500, "body": f"error: {e}"}
    return {
        "statusCode": 200,
        "body": json_dumps(section_diary),
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET",
            "Access-Control-Allow-Headers": "Content-Type,X-CSRF-TOKEN",
        },
    }
