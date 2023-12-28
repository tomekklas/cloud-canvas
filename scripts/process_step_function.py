import os
import yaml
import json

def parse_config_files():
    # Get the current directory
    current_directory = os.getcwd()

    # Dictionary to store the parsed data
    parsed_data = {}

    # Loop through all files and directories in the current directory
    for item in os.listdir(current_directory):
        # Construct the full path
        item_path = os.path.join(current_directory, item)

        # Check if the item is a directory
        if os.path.isdir(item_path):
            # Scan for .config.yaml files in this directory
            for file in os.listdir(item_path):
                if file.endswith(".config.yaml"):
                    # Construct the full file path
                    file_path = os.path.join(item_path, file)

                    # Open and parse the YAML file
                    with open(file_path, 'r') as f:
                        try:
                            config = yaml.safe_load(f)

                            # Retrieve the required information
                            module_execution_order = config.get('module_execution_order', 'N/A')
                            module_type = config.get('module_type', 'N/A')
                            module_directory_name = config.get('module_directory_name', 'N/A')

                            # Store the data using module_directory_name as key
                            parsed_data[module_directory_name] = {
                                'module_execution_order': module_execution_order,
                                'module_type': module_type
                            }
                        except yaml.YAMLError as exc:
                            print(f"Error parsing YAML file {file_path}: {exc}")

    return json.dumps(parsed_data, indent=4)

# Example usage
parsed_json = parse_config_files()
print(parsed_json)
