import os
import yaml
import json
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

                            # Retrieve the required information
                            add_deployment_setup = config.get('add_deployment_setup', '')
                            copyright_license = config.get('copyright_license', '')
                            deployment_default_role_to_assume = config.get('deployment_default_role_to_assume', '')
                            deployment_dev_bucket = config.get('deployment_dev_bucket', '')
                            deployment_prod_bucket = config.get('deployment_prod_bucket', '')
                            deployment_stack_name_prefix = config.get('deployment_stack_name_prefix', '')
                            include_lambda_scaffolding = config.get('include_lambda_scaffolding', '')
                            module_directory_name = config.get('module_directory_name', '')
                            module_execution_order = config.get('module_execution_order', '')
                            module_name = config.get('module_name', '')
                            module_type = config.get('module_type', '')
                            owner_email = config.get('owner_email', '')
                            owner_name = config.get('owner_name', '')
                            short_module_description = config.get('short_module_description', '')



                            # Organize data by module_execution_order
                            if module_execution_order not in parsed_data:
                                parsed_data[module_execution_order] = []

                            parsed_data[module_execution_order].append({
                                'module_name': module_name,
                                'module_directory_name': module_directory_name,
                                'module_type': module_type,
                                'add_deployment_setup': add_deployment_setup,
                                'copyright_license': copyright_license,
                                'deployment_default_role_to_assume': deployment_default_role_to_assume,
                                'deployment_dev_bucket': deployment_dev_bucket,
                                'deployment_prod_bucket': deployment_prod_bucket,
                                'deployment_stack_name_prefix': deployment_stack_name_prefix,
                                'include_lambda_scaffolding': include_lambda_scaffolding,
                                'module_execution_order': module_execution_order,
                                'owner_email': owner_email,
                                'owner_name': owner_name,
                                'short_module_description': short_module_description
                            })

                        except yaml.YAMLError as exc:
                            print(f"Error parsing YAML file {file_path}: {exc}")

    # Sort the dictionary by module_execution_order (ascending)
    sorted_data = OrderedDict(sorted(parsed_data.items()))

    return json.dumps(sorted_data, indent=4)

def create_step_function_file(json_data, templates_dir, output_file):
    # Load the JSON data
    modules = json.loads(json_data)

    # Set up Jinja environment
    env = Environment(loader=FileSystemLoader(templates_dir))

    # Start with the 'beginning.yaml'
    with open(os.path.join(templates_dir, 'beginning.yaml'), 'r') as file:
        content = file.read()

    # Process each module
    first_iteration = True  # Variable to track the first iteration
    for key, module_list in modules.items():
        for module in module_list:
            # Determine the template name based on the module type
            template_name = f"{module['module_type'].lower()}.yaml"

            try:
                # Get the template from the Jinja2 environment
                template = env.get_template(template_name)

                # Add a flag to the module data to indicate the first iteration
                module['is_first_iteration'] = first_iteration

                # Render the template with the module data
                rendered_content = template.render(module)

                # Append the rendered content to the main content
                content += rendered_content

                # Set first_iteration to False after the first module is processed
                first_iteration = False

            except jinja2.TemplateNotFound:
                print(f"Template not found: {template_name}")
            except jinja2.TemplateError as e:
                print(f"Template error in {template_name}: {e}")


    # Append 'end.yaml'
    with open(os.path.join(templates_dir, 'end.yaml'), 'r') as file:
        content += file.read()

    # Save the final content to 'step_function.yaml'
    with open(output_file, 'w') as file:
        file.write(content)


json_data = parse_config_files()
print(json_data)

templates_dir = '_deployment/templates/.step_function_snippets/'
output_file = '_deployment/templates/step_function_definition.yaml'

create_step_function_file(json_data, templates_dir, output_file)
