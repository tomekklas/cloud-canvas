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

        # If validation is successful, return the event
        return event

    except ValidationError as ve:
        # Raise an exception for validation errors
        raise Exception("ValidationException", ve.message)

    except FileNotFoundError:
        # Raise an exception if the file is not found
        raise Exception("FileNotFoundException", "Required file not found.")

    except Exception as e:
        # General exception handling
        raise Exception("GeneralException", str(e))

# Run the Lambda function with a test event from a file
if __name__ == "__main__":
    # test_event = load_json_file('event-create.json')
    test_event = load_json_file('event-create.json')
    print(lambda_handler(test_event, None))
