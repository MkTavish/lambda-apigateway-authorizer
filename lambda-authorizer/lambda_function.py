import os
from ipaddress import ip_address, ip_network
import uuid
import json
import boto3

def get_secret():
    secret_name = os.environ.get("API_GATEWAY_TOKEN")  # Name of the secret in Secrets Manager
    region_name = os.environ.get("AWS_REGION")   # Your AWS region

    session = boto3.session.Session()
    client = session.client(service_name='secretsmanager', region_name=region_name)

    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    except Exception as e:
        print(f"Error retrieving secret: {e}")
        return None

    secret = get_secret_value_response['SecretString']
    return json.loads(secret)

# This function checks if the IP_ADDRESS is in the allowed IP_RANGE
def is_ip_allowed(IP_ADDRESS, IP_RANGE):
    for ip_range in IP_RANGE:
        if '/' in ip_range: 
            if ip_address(IP_ADDRESS) in ip_network(ip_range):
                return True
        else:
            if IP_ADDRESS == ip_range:
                return True
    return False

def lambda_handler(event, context):
    print(event)

    # Retrieve the secret
    secret = get_secret()
    if not secret or 'EXPECTED_AUTH_TOKEN' not in secret:
        raise ValueError("Secret not found or invalid format in Secrets Manager")

    expected_auth_token = secret['EXPECTED_AUTH_TOKEN']
    whitelisted_ips = json.loads(os.environ.get("IP_WHITELIST", '[]'))

    # Extract the source IP and Authorization header from the event
    source_ip = event['requestContext']['http']['sourceIp']
    auth_header = event['headers'].get('Authorization', '')
    API_ID = event["requestContext"]["apiId"]
    ACC_ID = event["requestContext"]["accountId"]
    METHOD = event["requestContext"]["http"]["method"]
    STAGE = event["requestContext"]["stage"]
    ROUTE = event["requestContext"]["http"]["path"]
    
     # Check if the source IP is allowed and the Authorization header is valid
    is_ip_valid = is_ip_allowed(source_ip, whitelisted_ips)
    is_auth_valid = event["headers"]["authorization"] == expected_auth_token

    if is_auth_valid and is_ip_valid:
        response = {
            "principalId": f"{uuid.uuid4().hex}",
            "policyDocument": {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Action": "execute-api:Invoke",
                        "Effect": "Allow",
                        "Resource": f"arn:aws:execute-api:us-east-1:{ACC_ID}:{API_ID}/{STAGE}/{METHOD}/*",
                    }
                ],
            },
        }

        return response

    response = {
        "principalId": f"{uuid.uuid4().hex}",
        "policyDocument": {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "execute-api:Invoke",
                    "Effect": "Deny",
                    "Resource": f"arn:aws:execute-api:us-east-1:{ACC_ID}:{API_ID}/*/*/*",
                }
            ],
        },
    }

    return response
    #policy_effect = "Allow" if is_ip_valid and is_auth_valid else "Deny"
    
    # Construct the Auth Response
    # policy = {
    #     "principalId": "uzer",
    #     "policyDocument": {
    #         "Version": "2012-10-17",
    #         "Statement": [
    #             {
    #                 "Action": "execute-api:Invoke",
    #                 "Effect": policy_effect,
    #                 "Resource": f"arn:aws:execute-api:us-east-1:{ACC_ID}:{API_ID}/{STAGE}/{METHOD}/*"  # Use the route ARN from the event
    #             }
    #         ]
    #     }
    # }

    # return policy
