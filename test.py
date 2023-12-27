import os
import subprocess

def get_module_name():
    return input("Enter the module name: ")

def run_copier(module_name):
    # Directory where the module will be generated
    module_dir = f"modules/{module_name}"

    # Unique answers file for each module
    answers_file = f"copier-answers-{module_name}.yml"

    # Run Copier with the specific answers file
    copier_cmd = f"copier copy . {module_dir} --answers-file={answers_file}"

    # Execute the Copier command
    subprocess.run(copier_cmd, shell=True, check=True)

def main():
    while True:
        module_name = get_module_name()
        run_copier(module_name)

        another = input("Do you want to create another module? (yes/no): ")
        if another.lower() != 'yes':
            break

if __name__ == "__main__":
    main()
