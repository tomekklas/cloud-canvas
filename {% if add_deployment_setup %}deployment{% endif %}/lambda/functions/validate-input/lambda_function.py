import re

def lambda_handler(event, context):
    try:
        # Ensure the mandatory StackPrefix is present and is non-empty
        if 'StackPrefix' not in event or not event['StackPrefix']:
            raise ValueError('Missing or empty StackPrefix.')

        # Validate TemplateUrl field
        if 'TemplateUrl' not in event or not event['TemplateUrl']:
            raise ValueError('Missing or empty TemplateUrl.')

        template_url_pattern = re.compile(
            r'^https://.+\.s3\..+\.amazonaws\.com/.+$'
        )

        if not template_url_pattern.match(event['TemplateUrl']):
            raise ValueError('Invalid TemplateUrl. It should be an HTTPS address pointing to an S3 bucket.')

        # Ensure either Create or Delete is provided, but not both
        if 'Create' in event and 'Delete' in event:
            raise ValueError('Either Create or Delete should be provided, but not both.')
        elif 'Create' not in event and 'Delete' not in event:
            raise ValueError('Either Create or Delete is required.')

        # Function to validate the sub-module (i.e., either Create or Delete)
        def validate_submodule(data):
            # Ensure there's at least one of "Include" or "Exclude"
            if 'Include' not in data and 'Exclude' not in data:
                raise ValueError('At least one of Include or Exclude is required.')

            for key in ['Include', 'Exclude']:
                if key in data:
                    submodule_data = data[key]

                    # At least one of Accounts, OUs, or Tags should be present
                    if not any(k in submodule_data for k in ['Accounts', 'OUs', 'Tags']):
                        raise ValueError(f'{key} should have at least one of Accounts, OUs, or Tags.')

                    # Each of the keys (Accounts, OUs, Tags) should have values if present
                    for sub_key, values in submodule_data.items():
                        if not values:
                            raise ValueError(f'{key}\'s {sub_key} should have at least one value.')

            # Optional Parameters validation
            if 'Parameters' in data:
                parameters_data = data['Parameters']
                if not any(parameters_data.values()):
                    raise ValueError('Parameters should have at least one key with values.')

        if 'Create' in event:
            validate_submodule(event['Create'])

        if 'Delete' in event:
            validate_submodule(event['Delete'])

        # If all checks pass, return the original event data
        return event

    except ValueError as e:
        # Returning an error that's easy to catch in Step Functions
        return {
            'Error': 'ManifestValidationError',
            'Cause': str(e)
        }

