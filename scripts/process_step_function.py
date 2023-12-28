import os
import yaml
import json
import copy
import shutil
import tempfile
from collections import OrderedDict
from jinja2 import Environment, FileSystemLoader

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

                            # Retrieve the required information and organize data by module_execution_order
                            if config.get('module_execution_order') not in parsed_data:
                                parsed_data[config['module_execution_order']] = []

                            parsed_data[config['module_execution_order']].append(config)

                        except yaml.YAMLError as exc:
                            print(f"Error parsing YAML file {file_path}: {exc}")

    # Sort the dictionary by module_execution_order (ascending)
    sorted_data = OrderedDict(sorted(parsed_data.items()))

    return json.dumps(sorted_data, indent=4)

def create_step_function_file(json_data, templates_dir, output_file):
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as tmp_dir:
        # Copy template files to the temporary directory
        for filename in os.listdir(templates_dir):
            shutil.copy(os.path.join(templates_dir, filename), tmp_dir)

        # Load the JSON data
        modules = json.loads(json_data)

        # Set up Jinja environment to use the temporary directory
        env = Environment(loader=FileSystemLoader(tmp_dir), cache_size=0)

        # Initialize content outside the loop
        content = ""

        # Start with the 'beginning.yaml'
        with open(os.path.join(tmp_dir, 'beginning.yaml'), 'r') as file:
            content = file.read()

        # Process each module
        first_iteration = True
        for key, module_list in modules.items():
            for module in module_list:
                # Determine the template name based on the module type
                template_name = f"{module['module_type'].lower()}.yaml"

                try:
                    # Get the template from the Jinja2 environment
                    template = env.get_template(template_name)

                    # Create a deep copy of the module to prevent modification
                    module_copy = copy.deepcopy(module)
                    module_copy['is_first_iteration'] = first_iteration

                    # Render the template with the copied module data
                    rendered_content = template.render(module_copy)

                    # Append the rendered content to the main content
                    content += rendered_content

                    # Set first_iteration to False after the first module is processed
                    first_iteration = False

                except jinja2.TemplateNotFound:
                    print(f"Template not found: {template_name}")
                except jinja2.TemplateError as e:
                    print(f"Template error in {template_name}: {e}")

        # Append 'end.yaml'
        with open(os.path.join(tmp_dir, 'end.yaml'), 'r') as file:
            content += file.read()

        # Save the final content to the specified output file
        with open(output_file, 'w') as file:
            file.write(content)

# Example usage
json_data = parse_config_files()
templates_dir = '_deployment/templates/.step_function_snippets/'
output_file = '_deployment/templates/step_function_definition.yaml'
create_step_function_file(json_data, templates_dir, output_file)
