import json

def lambda_handler(event, context):
    try:
        # Ensure the root has "Deploy"
        if 'Deploy' not in event:
            return {
                'statusCode': 400,
                'body': json.dumps('Missing Deploy key.')
            }

        deploy_data = event['Deploy']

        # Ensure there's "Include" under "Deploy"
        if 'Include' not in deploy_data:
            return {
                'statusCode': 400,
                'body': json.dumps('Missing Include key under Deploy.')
            }

        include_data = deploy_data['Include']

        # Check if there's at least one value underneath Include with at least one value provided
        if not any(include_data.values()):
            return {
                'statusCode': 400,
                'body': json.dumps('Include should have at least one key with values.')
            }

        for key, values in include_data.items():
            if not values:
                return {
                    'statusCode': 400,
                    'body': json.dumps(f'Include\'s {key} should have at least one value.')
                }

        # Optional Parameters validation
        if 'Parameters' in deploy_data:
            parameters_data = deploy_data['Parameters']
            if not any(parameters_data.values()):
                return {
                    'statusCode': 400,
                    'body': json.dumps('Parameters should have at least one key with values.')
                }

        # If all checks pass, return success
        return {
            'statusCode': 200,
            'body': json.dumps('Manifest structure is valid.')
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps(str(e))
        }

