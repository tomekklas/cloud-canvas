import os
import json
import boto3
import requests

API_KEY = os.environ['ApiKey']
API_DOMAIN = os.environ['ApiDomain']
API_VERSION = os.environ['ApiVersion']
S3_BUCKET = os.environ['ConfigS3Bucket']
S3_BUCKET_PREFIX = os.environ['ConfigS3Prefix']

s3_client = boto3.client('s3')

def lambda_handler(event, context):
    try:
        # Extract StackPrefix and TemplateUrl
        stack_prefix = event["StackPrefix"]
        template_url = event["TemplateUrl"]

        # Determine the operation type: Create or Delete
        operation_type = "Create" if "Create" in event else "Delete"
        operation_details = event[operation_type]
        
        include_details = operation_details["Include"]
        parameters = operation_details.get("Parameters", {})  # Using get to handle missing Parameters

        # Ensure at least one criterion (Accounts, OUs, Tags) is present under Include.
        if not any(criterion in include_details for criterion in ['Accounts', 'OUs', 'Tags']):
            raise Exception("At least one criterion (Accounts, OUs, Tags) must be present under Include.")
        
        # Gather accounts from Include criteria
        include_accounts = gather_accounts(include_details)
        
        # Extract exclude details if present and gather accounts
        exclude_accounts = []
        if "Exclude" in operation_details:
            exclude_details = operation_details["Exclude"]
            exclude_accounts = gather_accounts(exclude_details)
        
        # Exclude the accounts specified in the Exclude section from the Include accounts
        final_accounts = [account for account in include_accounts if account['id'] not in [excl['id'] for excl in exclude_accounts]]
        
        # Remove non-ACTIVE accounts and deduplicate
        active_accounts = {account['id']: account for account in final_accounts if account['status'] == 'ACTIVE'}.values()

        # Create files in S3 for each of the resultant active accounts
        for account in active_accounts:
            file_content = json.dumps({
                "Action": operation_type,
                "StackPrefix": stack_prefix,
                "TemplateUrl": template_url,
                "AccountId": account['id'],
                "Parameters": parameters
            })
            s3_key = f"{S3_BUCKET_PREFIX}/{context.aws_request_id}/{account['id']}.json"
            s3_client.put_object(Bucket=S3_BUCKET, Key=s3_key, Body=file_content)
            
        return {
            'statusCode': 200,
            'body': {
                'message': 'Process completed.',
                'Bucket': S3_BUCKET,
                'Prefix': f"{S3_BUCKET_PREFIX}/{context.aws_request_id}/"
            }
        }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(str(e))
        }

def gather_accounts(details):
    all_accounts = []

    # Fetch account details if present
    if "Accounts" in details:
        account_ids_url = f"https://{API_DOMAIN}/{API_VERSION}/aws-org-metadata/account_id/{','.join(map(str, details['Accounts']))}"
        all_accounts += query_api(account_ids_url)
    
    # Fetch OUs details if present
    if "OUs" in details:
        ou_url = f"https://{API_DOMAIN}/{API_VERSION}/aws-org-metadata/ou/{','.join(details['OUs'])}"
        all_accounts += query_api(ou_url)
    
    # Fetch tags details if present
    if "Tags" in details:
        tags_params = ','.join([f"{k}:{v}" for k, v in details["Tags"].items()])
        tags_url = f"https://{API_DOMAIN}/{API_VERSION}/aws-org-metadata/tags/{tags_params}"
        all_accounts += query_api(tags_url)
    
    return all_accounts

def query_api(url):
    headers = {
        'x-api-key': API_KEY
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    
    data = response.json()
    if 'error' in data:
        raise Exception(data['error'])
    
    return data
