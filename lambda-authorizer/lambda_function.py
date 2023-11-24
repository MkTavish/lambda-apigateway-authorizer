import os
from ipaddress import ip_address, ip_network
import uuid
import json
import boto3

# This function checks if the IP_ADDRESS is in the allowed IP_RANGE
def is_ip_allowed(IP_ADDRESS, IP_RANGE):
    # Check if any of the ranges is a CIDR block
    for ip_range in IP_RANGE:
        if '/' in ip_range:  # Check if the range is a CIDR block
            if ip_address(IP_ADDRESS) in ip_network(ip_range):
                return True
        else:  # The range is a single IP
            if IP_ADDRESS == ip_range:
                return True
    return False

def lambda_handler(event, context):
    print(event)

    whitelisted_ips = json.loads(os.environ.get("IP_WHITELIST", '[]'))
    print(whitelisted_ips)
    # Extract the source IP and Authorization header from the event
    source_ip = event['requestContext']['http']['sourceIp']
    #auth_header = event['headers'].get('Authorization', '')
    API_ID = event["requestContext"]["apiId"]
    ACC_ID = event["requestContext"]["accountId"]
    METHOD = event["requestContext"]["http"]["method"]
    STAGE = event["requestContext"]["stage"]
    ROUTE = event["requestContext"]["http"]["path"]
    
     # Check if the source IP is allowed and the Authorization header is valid
    is_ip_valid = is_ip_allowed(source_ip, whitelisted_ips)


    #policy_effect = "Allow" if event["headers"]["authorizationtoken"] == "secretcode"  and is_ip_valid else "Deny"
    
    if event["headers"]["authorizationtoken"] == "secretcode"  and is_ip_valid:
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
            "context": {"exampleKey": "exampleValue"},
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
        "context": {"exampleKey": "exampleValue"},
    }

    return response


    # Construct the Auth Response
    # policy = {
    #     "principalId": "user",
    #     "policyDocument": {
    #         "Version": "2012-10-17",
    #         "Statement": [
    #             {
    #                 "Action": "execute-api:Invoke",
    #                 "Effect": policy_effect,
    #                 "Resource": f"arn:aws:execute-api:us-east-1:{ACC_ID}:{API_ID}/{STAGE}/{METHOD}{ROUTE}"  # Use the route ARN from the event
    #             }
    #         ],
    #     },
    #     "context": {"exampleKey": "exampleValue"},
    # }

    # return policy
