import json
import os
from http.client import HTTPSConnection
from urllib.parse import urlparse
import boto3

def get_slack_webhook_url():
    #boto3 SSM client
    ssm_client = boto3.client('ssm')
    # parameter name
    parameter_name = '/slack/webhook/url'
    
    try:
        # Get the parameter from SSM
        parameter = ssm_client.get_parameter(Name=parameter_name, WithDecryption=True)
        return parameter['Parameter']['Value']
    except Exception as e:
        print(f"Error getting parameter: {e}")
        raise e

def lambda_handler(event, context):
    print('Received CloudWatch event:', json.dumps(event))

    # Parse details from the CloudWatch event
    alarm_name = event['AlarmName']
    new_state = event['NewStateValue']
    reason = event['NewStateReason']
    link_to_alarm = event['LinkToAlarm']

    # Determine the color based on the state of the alarm
    color = "#FF0000" if new_state == "ALARM" else "#36A64F"
    
    #Slack webhook URL from SSM Parameter Store
    webhook_url = get_slack_webhook_url()
    parsed_url = urlparse(webhook_url)
    domain = parsed_url.netloc
    path = parsed_url.path

    # Slack message
    slack_message = {
        "attachments": [
            {
                "fallback": f"CloudWatch Alarm: {alarm_name} state is now {new_state}",
                "color": color,
                "title": alarm_name,
                "title_link": link_to_alarm,
                "text": reason,
                "fields": [
                    {"title": "Alarm Name", "value": alarm_name, "short": True},
                    {"title": "New State", "value": new_state, "short": True},
                    {"title": "Reason", "value": reason, "short": False}
                ],
                "footer": "AWS CloudWatch Alarm",
                "ts": event['StateChangeTime']
            }
        ]
    }
    
    # Send Slack message using http.client
    headers = {'Content-Type': 'application/json'}
    connection = HTTPSConnection(domain)
    connection.request('POST', path, body=json.dumps(slack_message), headers=headers)
    
    response = connection.getresponse()
    if response.status != 200:
        raise ValueError(f"Request to Slack returned an error {response.status}, the response is:\n{response.read().decode()}")

    connection.close()
    
    # Return a success response
    return {
        "statusCode": 200,
        "body": json.dumps("Notification sent to Slack successfully.")
    }
