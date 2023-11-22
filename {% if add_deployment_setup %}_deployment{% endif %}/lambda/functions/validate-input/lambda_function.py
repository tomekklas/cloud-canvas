import json
from jsonschema import validate, ValidationError

def load_json_file(file_path):
    """ Load JSON data from a file. """
    with open(file_path, 'r') as file:
        return json.load(file)

def lambda_handler(event, context):
    try:
        # Load the schema
        schema = load_json_file('schema.json')
        
        # Validate the event data
        validate(instance=event, schema=schema)

        # If validation is successful, return a success message
        # straight event is easier to understand in Step Function UI
        return event

    except ValidationError as ve:
        # If validation fails, return the error message
        return {
            "statusCode": 400,
            "body": json.dumps(f"Validation error: {ve.message}")
        }
    except FileNotFoundError:
        # If the file is not found, return an error message
        return {
            "statusCode": 500,
            "body": json.dumps("Required file not found.")
        }

# Run the Lambda function with a test event from a file
if __name__ == "__main__":
    # test_event = load_json_file('event-create.json')
    test_event = load_json_file('event-create.json')
    print(lambda_handler(test_event, None))