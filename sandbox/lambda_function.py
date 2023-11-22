import os
import json
import boto3
import requests

# Mock
# Set default values for environment variables for local testing
os.environ['ApiKey'] = '7f8g5LXLiJ2QR7biKg42PaHoGsbJxiqDQLNQF9Ri'
os.environ['ApiDomain'] = 'https://z8btaajavk.execute-api.eu-central-1.amazonaws.com'
os.environ['ApiVersion'] = 'v1'
os.environ['ConfigS3Bucket'] = 'deployment-idea-test-bucket'
os.environ['ConfigS3Prefix'] = 'config/xxx'
os.environ['DefaultRoleArnToAssume'] = 'RoileName'

# Mock event
mock_event = {
  "StackPrefix": "testing",
  "TemplateUrl": "https://deployment-idea-test-bucket.s3.eu-central-1.amazonaws.com/xxx/v1/_latest/module-4/templates/stack.yaml",
  "RoleToAssume": "CloudCanvasGenericCrossAccountAdminRole",
  "Create": {
    "Include": {
      "Accounts": [
        "821373506894",
        "660034872039",
        "548584997268"
      ],
      "OUs": [
        "ou-cevp-dlhavf71",
        "ou-cevp-gs8zwffm"
      ],
      "Tags": {
        "Test": "Yes",
        "Owner": "Alan"
      }
    },
    "Exclude": {
      "Accounts": [
        "671717135011"
      ],
      "OUs": [
        "ou-cevp-kqbf99wq"
      ],
      "Tags": {
        "Type": "Infra"
      }
    },
    "Parameters": {
      "Environment": "Dev"
    },
    "Tags": {
      "Key": "Value"
    }
  }
  ,
  "contextDetails": {
    "arn": "arn:aws:states:eu-central-1:821373506894:execution:deployment:b8193b6e-da6c-48b1-b52e-fbe83ecf7e78"
  }
}

# empty mock context
mock_context = {}

# Environment variables
API_KEY = os.environ['ApiKey']
API_DOMAIN = os.environ['ApiDomain']
API_VERSION = os.environ['ApiVersion']
S3_BUCKET = os.environ['ConfigS3Bucket']
S3_BUCKET_PREFIX = os.environ['ConfigS3Prefix']
DEFAULT_ROLE_NAME_TO_ASSUME = os.environ.get('DefaultRoleArnToAssume')

def lambda_handler(event, context):
    # Extract values from the event
    stack_prefix = event["StackPrefix"]
    template_url = event["TemplateUrl"]
    role_to_assume = event.get("RoleToAssume", DEFAULT_ROLE_NAME_TO_ASSUME)

    # Extract the execution ID from the event
    execution_arn = event.get('contextDetails', {}).get('arn', '')
    execution_id = execution_arn.split(':')[-1]

    # Determine the operation type: Create or Delete
    operation_type = "Create" if "Create" in event else "Delete"
    operation_details = event[operation_type]

    # Process include and exclude criteria
    included_accounts = process_criteria(operation_details.get('Include', {}))
    excluded_accounts = process_criteria(operation_details.get('Exclude', {}))

    # Deduplicate and filter out excluded accounts
    included_accounts = deduplicate_accounts(included_accounts)
    excluded_account_ids = {acc['id'] for acc in excluded_accounts}
    final_accounts = [acc for acc in included_accounts if acc['id'] not in excluded_account_ids]

    # Initialize the S3 client
    s3_client = boto3.client('s3')

    # Loop through each account in final_accounts and create a file in S3
    for account in final_accounts:
        file_content = json.dumps({
            "Action": operation_type,
            "StackPrefix": stack_prefix,
            "TemplateUrl": template_url,
            "AccountId": account['id'],
            "RoleArnToAssume": f"arn:aws:iam::{account['id']}:role/{role_to_assume}",
            "Parameters": operation_details.get('Parameters', {}),
            "Tags": operation_details.get('Tags', {}),
        })
        s3_key = f"{S3_BUCKET_PREFIX}/{execution_id}/{account['id']}.json"
        print(s3_key)
        s3_client.put_object(Bucket=S3_BUCKET, Key=s3_key, Body=file_content)

    return {
        'statusCode': 200,
        'body': {
            'message': 'Process completed.',
            'Bucket': S3_BUCKET,
            'Prefix': f"{S3_BUCKET_PREFIX}/{execution_id}/"
        }
    }
    return {
        "statusCode": 200,
        "body": json.dumps("Process completed successfully.")
    }

def call_api(endpoint, params=None):
    """
    Makes a GET request to the specified API endpoint with the given parameters.
    Ignores responses with 'No items found' message.

    :param endpoint: The API endpoint to call (e.g., 'account_id', 'ou', or 'tags')
    :param params: The parameters for the API call
    :return: JSON response from the API or None if 'No items found'
    """
    # Construct the full URL
    url = f"{API_DOMAIN}/{API_VERSION}/aws-org-metadata/{endpoint}"

    # Set the headers for authentication
    headers = {'x-api-key': API_KEY}

    try:
        # Make the GET request
        response = requests.get(url, headers=headers, params=params)

        # Check if the request was successful
        if response.status_code == 200:
            response_data = response.json()

            # Check if response_data is a list
            if isinstance(response_data, list):
                # Process list data (if needed)
                return response_data

            # If response_data is a dictionary, check for 'No items found' message
            if isinstance(response_data, dict) and response_data.get('message') == 'No items found':
                # Return None or an empty list if no items are found
                return None

            return response_data
        else:
            print(f"Error: Unable to call API. Status code: {response.status_code}")
            return None
    except requests.RequestException as e:
        print(f"Error: Exception during API call. Details: {e}")
        return None

def deduplicate_accounts(account_details):
    """
    Deduplicates a list of account details based on account IDs.

    :param account_details: List of dictionaries containing account details.
    :return: Deduplicated list of account details.
    """
    unique_accounts = {}
    for account in account_details:
        account_id = account.get('id')
        if account_id:
            unique_accounts[account_id] = account
    return list(unique_accounts.values())

def process_criteria(criteria):
    """
    Processes include or exclude criteria and returns account details.

    :param criteria: Dictionary containing 'Accounts', 'OUs', and 'Tags'.
    :return: List of account details based on the criteria.
    """
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

# Run the Lambda function with the mock event
if __name__ == "__main__":
    response = lambda_handler(mock_event, mock_context)
    print(response)