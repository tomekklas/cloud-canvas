import boto3
import yaml

s3 = boto3.client('s3')

def lambda_handler(event, context):
    # Fetching S3 details from event
    bucket_name = event['bucket_name'] # Name of S3 bucket
    file_key = event['file_key'] # Key of the file in the S3 bucket
    param = event.get('param', 'defaults') # Get the environment (defaults, dev, prod, etc.)

    # Retrieve file from S3
    file_obj = s3.get_object(Bucket=bucket_name, Key=file_key)
    file_content = file_obj["Body"].read().decode('utf-8')

    # Parse the YAML
    config = yaml.safe_load(file_content)

    # Create the configuration object based on 'param'
    result_config = config.get('defaults', {}).copy()  # Start with defaults
    environment_config = config.get(param, {})
    result_config.update(environment_config)  # Overwrite with environment-specific values

    return result_config


# {
#   "bucket_name": "my-config-bucket",
#   "file_key": "path/to/config.yaml",
#   "param": "dev"
# }