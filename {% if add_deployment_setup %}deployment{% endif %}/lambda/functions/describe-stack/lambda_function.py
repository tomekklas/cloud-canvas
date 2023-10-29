import boto3

def lambda_handler(event, context):
    client = boto3.client('cloudformation')
    
    stack_name = event['Parameters']['StackPrefix']
    
    try:
        response = client.describe_stacks(StackName=stack_name)
        return response
    except Exception as e:
        if "Stack with id" in str(e) and "does not exist" in str(e):
            raise Exception("StackDoesNotExist")
        else:
            raise e
