
# Cloud Canvas

Cloud Canvas is a fully-featured template for web applications, emphasizing readability and efficient scaffolding of Lambda functions and layers, along with comprehensive logging and permissions management. It leverages Copier to interactively generate project scaffolding, including build and S3 upload scripts. 

Key features include:
- **Readability:** The template prioritizes clear, readable code and configuration.
- **Lambda Functions and Layers:** Provides a structured way to scaffold AWS Lambda functions and layers, making it easier to manage serverless applications.
- **Logging and Permissions:** Integrates comprehensive logging and permissions management to ensure robust application monitoring and security.
- **Interactive Setup:** Copier prompts you with questions to tailor the project to your needs, creating a customized project shell.
- **Versioned Builds:** All builds are versioned, ensuring traceability and consistency across deployments.
- **Flexible Build Options:** Builds can be executed locally using Docker or with AWS CodeBuild, providing flexibility in your development workflow.
- **Resource Links:** The `stack.yaml` template contains absolute links to all resources, ensuring seamless integration and deployment across environments.

## Features

- CloudFormation templates for AWS infrastructure
- Shell scripts for automation
- Python scripts for custom tasks
- Copier templates for project initialization

## Prerequisites

- Copier
- Git

## Installation

1. **Install Copier:**

   ```bash
   pip install copier
   ```
   for more detailed instruction see https://github.com/copier-org/copier

## Usage

### Creating a New Project

1. **Generate a new project from this template using Copier:**

   ```bash
   copier copy https://github.com/tomekklas/cloud-canvas --trust your_project_directory
   ```

2. **Answer the prompted questions to configure your project:**

   Copier will ask a series of questions to tailor the project shell to your specifications. Answer these questions to proceed with the project setup.

### Configuration

1. **Navigate to your project directory:**

   ```bash
   cd your_project_directory
   ```

2. **Update the `.env` file with your configuration:**

   ```ini
   # Example .env configuration
   AWS_ACCESS_KEY_ID=your_access_key
   AWS_SECRET_ACCESS_KEY=your_secret_key
   REGION=your_aws_region
   ```

## Project Structure

- `copier.yaml`: Configuration file for Copier.
- `scripts/`: Directory containing various Shell and Python scripts.
- `templates/`: Directory containing CloudFormation templates.
- `.env.example`: Example environment configuration file.

## Contributing

1. Fork the repository.
2. Create a new branch (`git checkout -b feature-branch`).
3. Commit your changes (`git commit -am 'Add new feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Create a new Pull Request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
