import boto3

def lambda_handler(event, context):
    client = boto3.client('cloudformation')
    
    stack_name = event['Parameters']['StackPrefix']
    
    try:
        response = client.describe_stacks(StackName=stack_name)
        stack_status = response['Stacks'][0]['StackStatus']

        # Check for "Create/Update In Progress" statuses
        in_progress_statuses = ["CREATE_IN_PROGRESS", "UPDATE_IN_PROGRESS"]
        if stack_status in in_progress_statuses:
            return {
                'Category': 'Create/Update In Progress',
                'StackName': stack_name,
                'StackStatus': stack_status
            }

        # Check for "Failure/Rollback" statuses
        failure_statuses = [
            "DELETE_IN_PROGRESS", "ROLLBACK_IN_PROGRESS", "ROLLBACK_COMPLETE",
            "CREATE_FAILED", "ROLLBACK_FAILED", "UPDATE_ROLLBACK_COMPLETE",
            "UPDATE_ROLLBACK_FAILED", "UPDATE_ROLLBACK_IN_PROGRESS", 
            "UPDATE_ROLLBACK_COMPLETE_CLEANUP_IN_PROGRESS"
        ]
        if stack_status in failure_statuses:
            return {
                'Category': 'Failure/Rollback',
                'StackName': stack_name,
                'StackStatus': stack_status
            }
        
        # For other statuses, just return the status
        return {
            'StackName': stack_name,
            'StackStatus': stack_status
        }
        
    except client.exceptions.ClientError as e:
        error_message = str(e)
        if "Stack with id" in error_message and "does not exist" in error_message:
            return {
                'Category': 'Does Not Exist',
                'StackName': stack_name,
                'Message': 'Stack does not exist'
            }
        else:
            raise e
