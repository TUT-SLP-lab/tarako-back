import boto3
import json
import os

SENDER_EMAIL = os.getenv('SENDER_EMAIL')
RECIPIENT_EMAIL = os.getenv('RECIPIENT_EMAIL')
REGION = "ap-northeast-1"

def send_email(title, body):
    client = boto3.client('ses', region_name=REGION)
    response = client.send_email(
        Source=SENDER_EMAIL,
        Destination={
            'ToAddresses': [
                RECIPIENT_EMAIL,
            ]
        },
        Message={
            'Subject': {
                'Data': title,
            },
            'Body': {
                'Text': {
                    'Data': body,
                },
            }
        }
    )

    return response
