import os
import json
import argparse
import sys
import pathlib
import yaml  # pyyaml ^6.0

from app.main import create_app  # Import the FastAPI application factory function - src/backend/app/main.py
from app.core.config import settings  # Import application settings - src/backend/app/core/config.py
from app.core.logging import get_logger  # Import logging utility - src/backend/app/core/logging.py

# Initialize logger
logger = get_logger(__name__)

# Define default output directory for API documentation
DEFAULT_OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'docs', 'api')


def parse_arguments():
    """Parse command-line arguments for the script

    Returns:
        argparse.Namespace: Parsed command-line arguments
    """
    # Create an ArgumentParser instance
    parser = argparse.ArgumentParser(description="Generate API documentation for IndiVillage backend")

    # Add --format argument with choices (json, yaml, markdown, html) and default 'json'
    parser.add_argument("--format", type=str, default="json", choices=["json", "yaml", "markdown", "html"],
                        help="Output format for the API documentation (json, yaml, markdown, html)")

    # Add --output-dir argument with default value DEFAULT_OUTPUT_DIR
    parser.add_argument("--output-dir", type=str, default=DEFAULT_OUTPUT_DIR,
                        help="Output directory for the generated documentation")

    # Add --title argument with default value from settings.PROJECT_NAME
    parser.add_argument("--title", type=str, default=settings.PROJECT_NAME,
                        help="Title for the API documentation")

    # Add --version argument with default value 'v1'
    parser.add_argument("--version", type=str, default="v1",
                        help="API version to document")
    
    # Add --pretty flag to enable pretty formatting of JSON output
    parser.add_argument("--pretty", action="store_true", help="Enable pretty formatting of JSON output")

    # Parse and return the command-line arguments
    return parser.parse_args()


def ensure_output_directory(output_dir):
    """Ensure the output directory exists, creating it if necessary

    Args:
        output_dir (str): Path to the output directory

    Returns:
        str: Absolute path to the output directory
    """
    # Convert output_dir to an absolute path
    output_dir = os.path.abspath(output_dir)

    # Check if the directory exists
    if not os.path.exists(output_dir):
        # If not, create the directory and any necessary parent directories
        logger.info(f"Creating output directory: {output_dir}")
        pathlib.Path(output_dir).mkdir(parents=True, exist_ok=True)
    else:
        logger.debug(f"Output directory already exists: {output_dir}")

    # Return the absolute path to the output directory
    return output_dir


def generate_openapi_json(app, title, pretty):
    """Generate OpenAPI JSON schema from the FastAPI application

    Args:
        app (fastapi.FastAPI): The FastAPI application instance
        title (str): Title for the API documentation
        pretty (bool): Enable pretty formatting of JSON output

    Returns:
        dict: OpenAPI schema as a dictionary
    """
    # Get the OpenAPI schema from the FastAPI application
    schema = app.openapi()

    # Update the schema title with the provided title
    schema["info"]["title"] = title

    # Return the OpenAPI schema as a dictionary
    return schema


def save_openapi_json(schema, output_dir, pretty):
    """Save OpenAPI schema as JSON file

    Args:
        schema (dict): OpenAPI schema as a dictionary
        output_dir (str): Path to the output directory
        pretty (bool): Enable pretty formatting of JSON output

    Returns:
        str: Path to the saved JSON file
    """
    # Construct the output file path
    output_file = os.path.join(output_dir, "openapi.json")

    # Open the file for writing
    with open(output_file, "w") as f:
        # Serialize the schema to JSON with pretty formatting if requested
        if pretty:
            json.dump(schema, f, indent=4)
        else:
            json.dump(schema, f)

    # Log the successful save operation
    logger.info(f"Saved OpenAPI JSON schema to: {output_file}")

    # Return the path to the saved file
    return output_file


def save_openapi_yaml(schema, output_dir):
    """Save OpenAPI schema as YAML file

    Args:
        schema (dict): OpenAPI schema as a dictionary
        output_dir (str): Path to the output directory

    Returns:
        str: Path to the saved YAML file
    """
    # Construct the output file path
    output_file = os.path.join(output_dir, "openapi.yaml")

    # Open the file for writing
    with open(output_file, "w") as f:
        # Serialize the schema to YAML
        yaml.dump(schema, f, indent=2)

    # Log the successful save operation
    logger.info(f"Saved OpenAPI YAML schema to: {output_file}")

    # Return the path to the saved file
    return output_file


def generate_markdown_docs(schema, output_dir):
    """Generate Markdown documentation from OpenAPI schema

    Args:
        schema (dict): OpenAPI schema as a dictionary
        output_dir (str): Path to the output directory

    Returns:
        str: Path to the saved Markdown file
    """
    # Construct the output file path
    output_file = os.path.join(output_dir, "api.md")

    # Open the file for writing
    with open(output_file, "w") as f:
        # Write the API title and description
        f.write(f"# {schema['info']['title']}\n\n")
        f.write(f"{schema['info']['description']}\n\n")

        # Iterate through each endpoint in the schema
        for path, methods in schema['paths'].items():
            # For each endpoint, write the path, method, description, parameters, request body, and responses
            for method, details in methods.items():
                f.write(f"## {method.upper()} {path}\n\n")
                f.write(f"{details.get('summary', '')}\n\n")

                # Parameters
                if 'parameters' in details:
                    f.write("### Parameters\n\n")
                    for param in details['parameters']:
                        f.write(f"- **{param['name']}** ({param['in']}): {param['description']}  \n")

                # Request Body
                if 'requestBody' in details:
                    f.write("### Request Body\n\n")
                    if 'content' in details['requestBody']:
                        for content_type, content_schema in details['requestBody']['content'].items():
                            f.write(f"**{content_type}**\n\n")
                            if 'schema' in content_schema:
                                f.write(f"```json\n")
                                f.write(json.dumps(content_schema['schema'], indent=4))
                                f.write(f"\n```\n")

                # Responses
                f.write("### Responses\n\n")
                for code, response in details['responses'].items():
                    f.write(f"**{code}**: {response.get('description', '')}\n\n")
                    if 'content' in response:
                        for content_type, content_schema in response['content'].items():
                            f.write(f"**{content_type}**\n\n")
                            if 'schema' in content_schema:
                                f.write(f"```json\n")
                                f.write(json.dumps(content_schema['schema'], indent=4))
                                f.write(f"\n```\n")

    # Log the successful save operation
    logger.info(f"Saved OpenAPI Markdown documentation to: {output_file}")

    # Return the path to the saved file
    return output_file


def generate_html_docs(schema, output_dir):
    """Generate HTML documentation from OpenAPI schema

    Args:
        schema (dict): OpenAPI schema as a dictionary
        output_dir (str): Path to the output directory

    Returns:
        str: Path to the saved HTML file
    """
    # Construct the output file path
    output_file = os.path.join(output_dir, "api.html")

    # Create an HTML template with CSS styling
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{schema['info']['title']}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            h1, h2 {{ color: #333; }}
            h2 {{ border-bottom: 1px solid #ccc; padding-bottom: 5px; }}
            h3 {{ color: #666; }}
            pre {{ background-color: #f4f4f4; padding: 10px; border: 1px solid #ddd; overflow-x: auto; }}
            .endpoint {{ margin-bottom: 20px; }}
            .method {{ font-weight: bold; color: #0055A4; }}
            .path {{ font-style: italic; }}
            .parameter {{ margin-left: 20px; }}
        </style>
    </head>
    <body>
        <h1>{schema['info']['title']}</h1>
        <p>{schema['info']['description']}</p>
        {{content}}
    </body>
    </html>
    """

    # Initialize content string
    content = ""

    # Iterate through each endpoint in the schema
    for path, methods in schema['paths'].items():
        # For each endpoint, generate HTML sections for path, method, description, parameters, request body, and responses
        for method, details in methods.items():
            content += f"""
            <div class="endpoint">
                <h2><span class="method">{method.upper()}</span> <span class="path">{path}</span></h2>
                <p>{details.get('summary', '')}</p>
            """

            # Parameters
            if 'parameters' in details:
                content += "<h3>Parameters</h3>"
                for param in details['parameters']:
                    content += f"""
                    <div class="parameter">
                        <strong>{param['name']}</strong> ({param['in']}): {param['description']}
                    </div>
                    """

            # Request Body
            if 'requestBody' in details:
                content += "<h3>Request Body</h3>"
                if 'content' in details['requestBody']:
                    for content_type, content_schema in details['requestBody']['content'].items():
                        content += f"<h4>{content_type}</h4>"
                        if 'schema' in content_schema:
                            content += f"<pre>{json.dumps(content_schema['schema'], indent=4)}</pre>"

            # Responses
            content += "<h3>Responses</h3>"
            for code, response in details['responses'].items():
                content += f"<h4>{code}: {response.get('description', '')}</h4>"
                if 'content' in response:
                    for content_type, content_schema in response['content'].items():
                        content += f"<h5>{content_type}</h5>"
                        if 'schema' in content_schema:
                            content += f"<pre>{json.dumps(content_schema['schema'], indent=4)}</pre>"

            content += "</div>"

    # Format the HTML with proper structure and styling
    final_html = html_template.replace("{{content}}", content)

    # Open the file for writing
    with open(output_file, "w") as f:
        # Write the HTML content
        f.write(final_html)

    # Log the successful save operation
    logger.info(f"Saved OpenAPI HTML documentation to: {output_file}")

    # Return the path to the saved file
    return output_file


def main():
    """Main entry point for the script"""
    # Parse command-line arguments
    args = parse_arguments()

    # Ensure the output directory exists
    output_dir = ensure_output_directory(args.output_dir)

    # Create a FastAPI application instance using create_app()
    app = create_app()

    # Generate the OpenAPI schema from the application
    schema = generate_openapi_json(app, args.title, args.pretty)

    # Based on the requested format, save the documentation in the appropriate format
    if args.format == "json":
        output_file = save_openapi_json(schema, output_dir, args.pretty)
    elif args.format == "yaml":
        output_file = save_openapi_yaml(schema, output_dir)
    elif args.format == "markdown":
        output_file = generate_markdown_docs(schema, output_dir)
    elif args.format == "html":
        output_file = generate_html_docs(schema, output_dir)
    else:
        logger.error(f"Invalid output format: {args.format}")
        print("Error: Invalid output format. Choose from json, yaml, markdown, html.")
        return 1

    # Log the successful generation of documentation
    logger.info(f"Successfully generated API documentation in {args.format} format: {output_file}")

    # Return exit code 0 for success
    return 0


if __name__ == "__main__":
    # Execute the main function and exit with the returned code
    sys.exit(main())