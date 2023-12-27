import os
import yaml
from jinja2 import Template

def main():
    try:
        print("Running script...")

        with open('.copier-answers.yml') as f:
            answers = yaml.safe_load(f)

        print("Answers loaded:", answers)

        base_directory = '_deployment/templates/' if answers.get('add_deployment_setup') else ''

        print("Base directory:", base_directory)

        if answers.get('deployment_module_type') == 'multi':
            concatenated_content = "ok"
            output_filepath = os.path.join(base_directory, 'step_function.yaml')

            print("Output filepath:", output_filepath)

            os.makedirs(base_directory, exist_ok=True)
            with open(output_filepath, 'w') as output_file:
                output_file.write(concatenated_content)

            print(f"File created at {output_filepath}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
