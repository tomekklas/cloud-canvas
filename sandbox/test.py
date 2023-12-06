import boto3
import json

def lambda_handler(event, context):
    # Extract information from the event
    parameters = event.get('Parameters', {})
    action = parameters.get('Action')
    stack_prefix = parameters.get('StackName')
    account_id = parameters.get('AccountId')

    # Initialize the CloudFormation client
    cloudformation = boto3.client('cloudformation')

    # Check if the stack exists and its status
    try:
        response = cloudformation.describe_stacks(StackName=f"{stack_prefix}")
        stack_exists = True
        # Check the stack status
        stack_status = response['Stacks'][0]['StackStatus']
        if stack_status.endswith('FAILED'):
            # Update the action to 'Failed' if the stack is in a failed state
            event['Parameters']['Action'] = 'Failed'
            return event
    except cloudformation.exceptions.ClientError as e:
        if 'does not exist' in str(e):
            stack_exists = False
        else:
            raise e  # Re-raise the exception if it's not a 'does not exist' error

    # Decide the action based on the existence of the stack and the input action
    if stack_exists:
        if action == 'Delete':
            updated_action = 'Delete'
        elif action == 'Create':
            updated_action = 'Update'
    else:
        if action == 'Create':
            updated_action = 'Create'
        elif action == 'Delete':
            updated_action = 'NoAction'

    # Update the event with the new action
    event['Parameters']['Action'] = updated_action
    
    # Return the modified event
    return event