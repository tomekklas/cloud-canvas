import os
import json
import boto3
import requests

# Environment variables
API_KEY = os.environ['ApiKey']
API_DOMAIN = os.environ['ApiDomain']
API_VERSION = os.environ['ApiVersion']
S3_BUCKET = os.environ['ConfigS3Bucket']
S3_BUCKET_PREFIX = os.environ['ConfigS3Prefix']
DEFAULT_ROLE_NAME_TO_ASSUME = os.environ.get('DefaultRoleArnToAssume')

def lambda_handler(event, context):
    stack_prefix = event["StackNamePrefix"]
    role_to_assume = event.get("RoleToAssume", DEFAULT_ROLE_NAME_TO_ASSUME)

    execution_arn = event.get('contextDetails', {}).get('arn', '')
    execution_id = execution_arn.split(':')[-1]

    s3_client = boto3.client('s3')

    for step in event["Steps"]:
        step_name = step["StepName"]

        if "Create" in step:
            operation_type = "Create"
            operation_details = step["Create"]
            template_url = operation_details.get("TemplateUrl", "")

            included_accounts = process_criteria(operation_details.get('Include', {}))
            excluded_accounts = process_criteria(operation_details.get('Exclude', {}))

            included_accounts = deduplicate_accounts(included_accounts)
            excluded_account_ids = {acc['id'] for acc in excluded_accounts}
            final_accounts = [acc for acc in included_accounts if acc['id'] not in excluded_account_ids]
            final_active_accounts = filter_active_accounts(final_accounts)

            for account in final_active_accounts:
                process_account(account, operation_type, stack_prefix, template_url, role_to_assume, operation_details, step_name, execution_id, s3_client)

        elif "Delete" in step:
            operation_type = "Delete"
            operation_details = step["Delete"]
            # Assuming Delete has a similar structure to Create for Include/Exclude
        
            # Process include and exclude criteria
            included_accounts = process_criteria(operation_details.get('Include', {}))
            excluded_accounts = process_criteria(operation_details.get('Exclude', {}))
        
            # Deduplicate and filter out excluded accounts
            included_accounts = deduplicate_accounts(included_accounts)
            excluded_account_ids = {acc['id'] for acc in excluded_accounts}
            final_accounts = [acc for acc in included_accounts if acc['id'] not in excluded_account_ids]
            final_active_accounts = filter_active_accounts(final_accounts)
        
            # Process each active account for deletion
            for account in final_active_accounts:
                process_delete(account, stack_prefix, role_to_assume, operation_details, step_name, execution_id, s3_client)


    return {
        'statusCode': 200,
        'body': {
            'message': 'Process completed.',
            'Bucket': S3_BUCKET,
            'Prefix': f"{S3_BUCKET_PREFIX}/{step_name}/"
        }
    }

def process_account(account, operation_type, stack_prefix, template_url, role_to_assume, operation_details, step_name, execution_id, s3_client):
    existing_tags_dict = operation_details.get('Tags', {})
    existing_tags_dict["DeployedBy"] = "CloudCanvas"

    transformed_tags = [{"Key": k, "Value": v} for k, v in existing_tags_dict.items()]
    existing_parameters_dict = operation_details.get('Parameters', {})
    transformed_parameters = [{"ParameterKey": k, "ParameterValue": v} for k, v in existing_parameters_dict.items()]

    file_content = json.dumps({
        "Action": operation_type,
        "StepName": step_name,
        "StackName": f"{stack_prefix}-{step_name}",
        "TemplateUrl": template_url,
        "AccountId": account['id'],
        "RoleArnToAssume": f"arn:aws:iam::{account['id']}:role/{role_to_assume}",
        "Parameters": transformed_parameters,
        "Tags": transformed_tags
    })
    
    s3_key = f"{S3_BUCKET_PREFIX}/{execution_id}/{step_name}/{account['id']}.json"
    s3_client.put_object(Bucket=S3_BUCKET, Key=s3_key, Body=file_content)

def call_api(endpoint, params=None):
    url = f"{API_DOMAIN}/{API_VERSION}/aws-org-metadata/{endpoint}"
    headers = {'x-api-key': API_KEY}
    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            response_data = response.json()
            if isinstance(response_data, list):
                return response_data
            if isinstance(response_data, dict) and response_data.get('message') == 'No items found':
                return None
            return response_data
        else:
            print(f"Error: Unable to call API. Status code: {response.status_code}")
            return None
    except requests.RequestException as e:
        print(f"Error: Exception during API call. Details: {e}")
        return None

def deduplicate_accounts(account_details):
    unique_accounts = {}
    for account in account_details:
        account_id = account.get('id')
        if account_id:
            unique_accounts[account_id] = account
    return list(unique_accounts.values())

def process_criteria(criteria):
    account_details = []
    accounts = criteria.get('Accounts', [])
    for account in accounts:
        details = call_api(f"account_id/{account}")
        if details:
            account_details.extend(details)
    ous = criteria.get('OUs', [])
    if ous:
        ou_accounts = call_api(f"ou/{','.join(ous)}")
        if ou_accounts:
            account_details.extend(ou_accounts)
    tags = criteria.get('Tags', {})
    if tags:
        tag_query = ','.join([f"{k}:{v}" for k, v in tags.items()])
        tag_accounts = call_api(f"tags/{tag_query}")
        if tag_accounts:
            account_details.extend(tag_accounts)
    return account_details

def filter_active_accounts(data):
    return [account for account in data if account.get('status') == 'ACTIVE']

# Test this function thoroughly to ensure it behaves as expected.
