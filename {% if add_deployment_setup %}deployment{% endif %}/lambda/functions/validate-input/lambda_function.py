import re

def lambda_handler(event, context):
    try:
        # Ensure the mandatory StackPrefix is present and is non-empty
        if 'StackPrefix' not in event or not event['StackPrefix']:
            raise ValueError('Missing or empty StackPrefix.')

        # Ensure the root has "Deploy"
        if 'Deploy' not in event:
            raise ValueError('Missing Deploy key.')

        deploy_data = event['Deploy']

        # Ensure there's "Include" under "Deploy"
        if 'Include' not in deploy_data:
            raise ValueError('Missing Include key under Deploy.')

        include_data = deploy_data['Include']

        # Check if there's at least one value underneath Include with at least one value provided
        if not any(include_data.values()):
            raise ValueError('Include should have at least one key with values.')

        for key, values in include_data.items():
            if not values:
                raise ValueError(f'Include\'s {key} should have at least one value.')

        # Validate TemplateUrl field
        if 'TemplateUrl' not in event or not event['TemplateUrl']:
            raise ValueError('Missing or empty TemplateUrl.')

        template_url_pattern = re.compile(
            r'^https://.+\.s3\..+\.amazonaws\.com/.+$'
        )

        if not template_url_pattern.match(event['TemplateUrl']):
            raise ValueError('Invalid TemplateUrl. It should be an HTTPS address pointing to an S3 bucket.')

        # Optional Parameters validation
        if 'Parameters' in deploy_data:
            parameters_data = deploy_data['Parameters']
            if not any(parameters_data.values()):
                raise ValueError('Parameters should have at least one key with values.')

        # If all checks pass, return the original event data
        return event

    except ValueError as e:
        # Returning an error that's easy to catch in Step Functions
        return {
            'Error': 'ManifestValidationError',
            'Cause': str(e)
        }
