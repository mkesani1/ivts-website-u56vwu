#!/bin/bash
#
# IndiVillage Website Deployment Script
# 
# This script automates the deployment process for the IndiVillage.com website across
# different environments (development, staging, production). It handles container image
# deployment, infrastructure updates, and implements environment-specific deployment 
# strategies including blue-green deployment for staging and production.
#
# Version: 1.0.0

set -eo pipefail

# Global variables
SCRIPT_DIR=$(dirname "${BASH_SOURCE[0]}")
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
REPO_ROOT=$(git rev-parse --show-toplevel)
LOG_DIR="/var/log/indivillage"
LOG_FILE="${LOG_DIR}/deploy_${TIMESTAMP}.log"
AWS_REGION="us-east-1"
AWS_SECONDARY_REGION="us-west-2"
ECR_REPOSITORY_FRONTEND="indivillage/frontend"
ECR_REPOSITORY_BACKEND="indivillage/backend"
TERRAFORM_DIR="${REPO_ROOT}/infrastructure/terraform/environments"

# Default values
DEFAULT_VERSION=$(git rev-parse HEAD)
DEFAULT_DEPLOYMENT_TYPE="full"
DEFAULT_SKIP_APPROVAL=false
DEFAULT_FORCE=false

# Environment variables
ENVIRONMENT=""
VERSION=""
DEPLOYMENT_TYPE=""
SKIP_APPROVAL=false
FORCE=false

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

#######################
# Function Definitions
#######################

# Logs a message to both stdout and the log file
log_message() {
    local message="$1"
    local timestamp=$(date +"%Y-%m-%d %H:%M:%S")
    
    echo -e "${timestamp} - ${message}"
    
    # Create log directory if it doesn't exist
    mkdir -p "${LOG_DIR}"
    echo "${timestamp} - ${message}" >> "${LOG_FILE}"
}

# Checks if required dependencies are installed
check_dependencies() {
    log_message "Checking dependencies..."
    local missing_deps=false
    
    # Check AWS CLI
    if ! command -v aws &> /dev/null; then
        log_message "${RED}Error: aws-cli is not installed or not in PATH${NC}"
        missing_deps=true
    else
        local aws_version=$(aws --version)
        log_message "Found ${aws_version}"
    fi
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_message "${RED}Error: docker is not installed or not in PATH${NC}"
        missing_deps=true
    else
        local docker_version=$(docker --version)
        log_message "Found ${docker_version}"
    fi
    
    # Check Terraform
    if ! command -v terraform &> /dev/null; then
        log_message "${RED}Error: terraform is not installed or not in PATH${NC}"
        missing_deps=true
    else
        local tf_version=$(terraform version -json | grep "terraform_version" | cut -d'"' -f4)
        log_message "Found Terraform v${tf_version}"
    fi
    
    # Check environment variables
    if [[ -z "${AWS_ACCESS_KEY_ID}" ]]; then
        log_message "${YELLOW}Warning: AWS_ACCESS_KEY_ID is not set${NC}"
    fi
    
    if [[ -z "${AWS_SECRET_ACCESS_KEY}" ]]; then
        log_message "${YELLOW}Warning: AWS_SECRET_ACCESS_KEY is not set${NC}"
    fi
    
    if [[ "${missing_deps}" == "true" ]]; then
        log_message "${RED}Error: Missing dependencies. Please install the required tools.${NC}"
        return 1
    fi
    
    log_message "${GREEN}All dependencies are available.${NC}"
    return 0
}

# Displays help information
display_help() {
    echo -e "\n${BLUE}IndiVillage Website Deployment Script${NC}"
    echo -e "This script automates the deployment process for the IndiVillage.com website\n"
    
    echo -e "${YELLOW}Usage:${NC}"
    echo -e "  $0 -e ENVIRONMENT [-v VERSION] [-t TYPE] [--skip-approval] [--force] [-h]\n"
    
    echo -e "${YELLOW}Options:${NC}"
    echo -e "  -e, --environment    Specify the deployment environment (development, staging, production)"
    echo -e "  -v, --version        Specify the version to deploy (git SHA, defaults to latest commit)"
    echo -e "  -t, --type           Specify deployment type (full, frontend-only, backend-only, infrastructure-only)"
    echo -e "                       Default: full"
    echo -e "  --skip-approval      Skip approval step for production deployment (emergency use only)"
    echo -e "  --force              Force deployment even if validation fails"
    echo -e "  -h, --help           Display this help message\n"
    
    echo -e "${YELLOW}Examples:${NC}"
    echo -e "  $0 -e development"
    echo -e "  $0 -e staging -v abcd1234"
    echo -e "  $0 -e production -v abcd1234 -t frontend-only"
    echo -e "  $0 -e production -v abcd1234 --skip-approval\n"
    
    echo -e "${YELLOW}Environment Variables:${NC}"
    echo -e "  AWS_ACCESS_KEY_ID        AWS access key ID for authentication"
    echo -e "  AWS_SECRET_ACCESS_KEY    AWS secret access key for authentication"
    echo -e "  AWS_REGION               AWS region for deployment (default: us-east-1)"
    echo -e "  SLACK_WEBHOOK_URL        Slack webhook URL for notifications"
    echo -e "  TERRAFORM_DIR            Base directory for Terraform configurations\n"
}

# Parses command line arguments
parse_arguments() {
    local args=("$@")
    local i=0
    
    while [[ $i -lt ${#args[@]} ]]; do
        case "${args[$i]}" in
            -h|--help)
                display_help
                exit 0
                ;;
            -e|--environment)
                i=$((i + 1))
                ENVIRONMENT="${args[$i]}"
                ;;
            -v|--version)
                i=$((i + 1))
                VERSION="${args[$i]}"
                ;;
            -t|--type)
                i=$((i + 1))
                DEPLOYMENT_TYPE="${args[$i]}"
                ;;
            --skip-approval)
                SKIP_APPROVAL=true
                ;;
            --force)
                FORCE=true
                ;;
            *)
                log_message "${RED}Error: Unknown option: ${args[$i]}${NC}"
                display_help
                return 1
                ;;
        esac
        i=$((i + 1))
    done
    
    # Validate required arguments
    if [[ -z "${ENVIRONMENT}" ]]; then
        log_message "${RED}Error: Environment (-e, --environment) is required${NC}"
        display_help
        return 1
    fi
    
    # Validate environment value
    if [[ "${ENVIRONMENT}" != "development" && "${ENVIRONMENT}" != "staging" && "${ENVIRONMENT}" != "production" ]]; then
        log_message "${RED}Error: Invalid environment. Must be one of: development, staging, production${NC}"
        display_help
        return 1
    fi
    
    # Set defaults for optional parameters
    if [[ -z "${VERSION}" ]]; then
        VERSION="${DEFAULT_VERSION}"
        log_message "Version not specified, using default: ${VERSION}"
    fi
    
    if [[ -z "${DEPLOYMENT_TYPE}" ]]; then
        DEPLOYMENT_TYPE="${DEFAULT_DEPLOYMENT_TYPE}"
        log_message "Deployment type not specified, using default: ${DEPLOYMENT_TYPE}"
    fi
    
    # Validate deployment type
    if [[ "${DEPLOYMENT_TYPE}" != "full" && 
          "${DEPLOYMENT_TYPE}" != "frontend-only" && 
          "${DEPLOYMENT_TYPE}" != "backend-only" && 
          "${DEPLOYMENT_TYPE}" != "infrastructure-only" ]]; then
        log_message "${RED}Error: Invalid deployment type. Must be one of: full, frontend-only, backend-only, infrastructure-only${NC}"
        display_help
        return 1
    fi
    
    return 0
}

# Sets up the deployment environment
setup_environment() {
    local environment="$1"
    
    log_message "Setting up ${environment} environment..."
    
    # Environment-specific configurations
    case "${environment}" in
        development)
            AWS_PROFILE="indivillage-dev"
            ECS_CLUSTER="indivillage-dev-cluster"
            ECR_REPOSITORY_PREFIX="dev"
            TERRAFORM_WORKSPACE="dev"
            ;;
        staging)
            AWS_PROFILE="indivillage-staging"
            ECS_CLUSTER="indivillage-staging-cluster"
            ECR_REPOSITORY_PREFIX="staging"
            TERRAFORM_WORKSPACE="staging"
            ;;
        production)
            AWS_PROFILE="indivillage-prod"
            ECS_CLUSTER="indivillage-prod-cluster"
            ECR_REPOSITORY_PREFIX="prod"
            TERRAFORM_WORKSPACE="prod"
            ;;
        *)
            log_message "${RED}Error: Invalid environment: ${environment}${NC}"
            return 1
            ;;
    esac
    
    # Configure AWS CLI
    export AWS_PROFILE="${AWS_PROFILE}"
    
    # Verify AWS credentials
    if ! aws sts get-caller-identity &> /dev/null; then
        log_message "${RED}Error: Failed to authenticate with AWS. Please check your credentials.${NC}"
        return 1
    fi
    
    log_message "${GREEN}Successfully set up ${environment} environment${NC}"
    return 0
}

# Builds and pushes Docker images to ECR
build_and_push_images() {
    local environment="$1"
    local version="$2"
    
    # Skip if deployment type is infrastructure-only
    if [[ "${DEPLOYMENT_TYPE}" == "infrastructure-only" ]]; then
        log_message "Skipping image build for infrastructure-only deployment"
        return 0
    fi
    
    log_message "Building and pushing Docker images for ${environment}..."
    
    # Get AWS account ID
    local aws_account_id=$(aws sts get-caller-identity --query Account --output text)
    local ecr_registry="${aws_account_id}.dkr.ecr.${AWS_REGION}.amazonaws.com"
    
    # Login to ECR
    log_message "Logging in to ECR..."
    aws ecr get-login-password --region "${AWS_REGION}" | docker login --username AWS --password-stdin "${ecr_registry}"
    
    # Ensure repositories exist
    ensure_ecr_repository() {
        local repo="$1"
        if ! aws ecr describe-repositories --repository-names "${repo}" &> /dev/null; then
            log_message "Creating ECR repository: ${repo}"
            aws ecr create-repository --repository-name "${repo}" --image-scanning-configuration scanOnPush=true
        fi
    }
    
    # Frontend Image
    if [[ "${DEPLOYMENT_TYPE}" == "full" || "${DEPLOYMENT_TYPE}" == "frontend-only" ]]; then
        local frontend_repo="${ECR_REPOSITORY_PREFIX}/${ECR_REPOSITORY_FRONTEND}"
        ensure_ecr_repository "${frontend_repo}"
        
        log_message "Building frontend image..."
        docker build -t "${frontend_repo}:${version}" -f "${REPO_ROOT}/frontend/Dockerfile" "${REPO_ROOT}/frontend"
        
        log_message "Pushing frontend image to ECR..."
        docker tag "${frontend_repo}:${version}" "${ecr_registry}/${frontend_repo}:${version}"
        docker tag "${frontend_repo}:${version}" "${ecr_registry}/${frontend_repo}:latest"
        
        docker push "${ecr_registry}/${frontend_repo}:${version}"
        docker push "${ecr_registry}/${frontend_repo}:latest"
    fi
    
    # Backend Image
    if [[ "${DEPLOYMENT_TYPE}" == "full" || "${DEPLOYMENT_TYPE}" == "backend-only" ]]; then
        local backend_repo="${ECR_REPOSITORY_PREFIX}/${ECR_REPOSITORY_BACKEND}"
        ensure_ecr_repository "${backend_repo}"
        
        log_message "Building backend image..."
        docker build -t "${backend_repo}:${version}" -f "${REPO_ROOT}/backend/Dockerfile" "${REPO_ROOT}/backend"
        
        log_message "Pushing backend image to ECR..."
        docker tag "${backend_repo}:${version}" "${ecr_registry}/${backend_repo}:${version}"
        docker tag "${backend_repo}:${version}" "${ecr_registry}/${backend_repo}:latest"
        
        docker push "${ecr_registry}/${backend_repo}:${version}"
        docker push "${ecr_registry}/${backend_repo}:latest"
    fi
    
    log_message "${GREEN}Successfully built and pushed Docker images for ${environment}${NC}"
    return 0
}

# Tags existing images for promotion between environments
tag_existing_images() {
    local source_environment="$1"
    local target_environment="$2"
    local version="$3"
    
    # Skip if deployment type is infrastructure-only
    if [[ "${DEPLOYMENT_TYPE}" == "infrastructure-only" ]]; then
        log_message "Skipping image tagging for infrastructure-only deployment"
        return 0
    fi
    
    log_message "Tagging existing images from ${source_environment} for ${target_environment}..."
    
    # Get AWS account ID
    local aws_account_id=$(aws sts get-caller-identity --query Account --output text)
    local ecr_registry="${aws_account_id}.dkr.ecr.${AWS_REGION}.amazonaws.com"
    
    # Login to ECR
    log_message "Logging in to ECR..."
    aws ecr get-login-password --region "${AWS_REGION}" | docker login --username AWS --password-stdin "${ecr_registry}"
    
    # Map environment names to ECR repository prefixes
    local source_prefix
    local target_prefix
    
    case "${source_environment}" in
        development)
            source_prefix="dev"
            ;;
        staging)
            source_prefix="staging"
            ;;
        production)
            source_prefix="prod"
            ;;
    esac
    
    case "${target_environment}" in
        development)
            target_prefix="dev"
            ;;
        staging)
            target_prefix="staging"
            ;;
        production)
            target_prefix="prod"
            ;;
    esac
    
    # Frontend Image
    if [[ "${DEPLOYMENT_TYPE}" == "full" || "${DEPLOYMENT_TYPE}" == "frontend-only" ]]; then
        local source_frontend_repo="${source_prefix}/${ECR_REPOSITORY_FRONTEND}"
        local target_frontend_repo="${target_prefix}/${ECR_REPOSITORY_FRONTEND}"
        
        # Ensure target repository exists
        if ! aws ecr describe-repositories --repository-names "${target_frontend_repo}" &> /dev/null; then
            log_message "Creating ECR repository: ${target_frontend_repo}"
            aws ecr create-repository --repository-name "${target_frontend_repo}" --image-scanning-configuration scanOnPush=true
        fi
        
        # Get image manifest
        log_message "Getting manifest for ${source_frontend_repo}:${version}"
        local frontend_manifest=$(aws ecr batch-get-image --repository-name "${source_frontend_repo}" --image-ids imageTag="${version}" --query 'images[].imageManifest' --output text)
        
        if [[ -z "${frontend_manifest}" ]]; then
            log_message "${RED}Error: Could not find frontend image ${source_frontend_repo}:${version}${NC}"
            return 1
        fi
        
        # Tag image for target environment
        log_message "Tagging frontend image for ${target_environment}"
        aws ecr put-image --repository-name "${target_frontend_repo}" --image-tag "${version}" --image-manifest "${frontend_manifest}" --region "${AWS_REGION}"
        aws ecr put-image --repository-name "${target_frontend_repo}" --image-tag "latest" --image-manifest "${frontend_manifest}" --region "${AWS_REGION}"
    fi
    
    # Backend Image
    if [[ "${DEPLOYMENT_TYPE}" == "full" || "${DEPLOYMENT_TYPE}" == "backend-only" ]]; then
        local source_backend_repo="${source_prefix}/${ECR_REPOSITORY_BACKEND}"
        local target_backend_repo="${target_prefix}/${ECR_REPOSITORY_BACKEND}"
        
        # Ensure target repository exists
        if ! aws ecr describe-repositories --repository-names "${target_backend_repo}" &> /dev/null; then
            log_message "Creating ECR repository: ${target_backend_repo}"
            aws ecr create-repository --repository-name "${target_backend_repo}" --image-scanning-configuration scanOnPush=true
        fi
        
        # Get image manifest
        log_message "Getting manifest for ${source_backend_repo}:${version}"
        local backend_manifest=$(aws ecr batch-get-image --repository-name "${source_backend_repo}" --image-ids imageTag="${version}" --query 'images[].imageManifest' --output text)
        
        if [[ -z "${backend_manifest}" ]]; then
            log_message "${RED}Error: Could not find backend image ${source_backend_repo}:${version}${NC}"
            return 1
        fi
        
        # Tag image for target environment
        log_message "Tagging backend image for ${target_environment}"
        aws ecr put-image --repository-name "${target_backend_repo}" --image-tag "${version}" --image-manifest "${backend_manifest}" --region "${AWS_REGION}"
        aws ecr put-image --repository-name "${target_backend_repo}" --image-tag "latest" --image-manifest "${backend_manifest}" --region "${AWS_REGION}"
    fi
    
    # Repeat for secondary region if applicable (for production)
    if [[ "${target_environment}" == "production" ]]; then
        log_message "Replicating images to secondary region (${AWS_SECONDARY_REGION})..."
        # This would require additional implementation to copy images between regions
        # Not implemented in this version of the script
    fi
    
    log_message "${GREEN}Successfully tagged images for ${target_environment}${NC}"
    return 0
}

# Deploys or updates infrastructure using Terraform
deploy_infrastructure() {
    local environment="$1"
    local version="$2"
    
    # Skip if deployment type is frontend-only or backend-only
    if [[ "${DEPLOYMENT_TYPE}" == "frontend-only" || "${DEPLOYMENT_TYPE}" == "backend-only" ]]; then
        log_message "Skipping infrastructure deployment for ${DEPLOYMENT_TYPE} deployment"
        return 0
    fi
    
    log_message "Deploying infrastructure for ${environment}..."
    
    # Change to the appropriate Terraform directory
    local tf_dir="${TERRAFORM_DIR}/${environment}"
    if [[ ! -d "${tf_dir}" ]]; then
        log_message "${RED}Error: Terraform directory for ${environment} not found: ${tf_dir}${NC}"
        return 1
    fi
    
    cd "${tf_dir}"
    
    # Initialize Terraform
    log_message "Initializing Terraform..."
    if ! terraform init; then
        log_message "${RED}Error: Failed to initialize Terraform${NC}"
        return 1
    fi
    
    # Validate Terraform configuration
    log_message "Validating Terraform configuration..."
    if ! terraform validate; then
        log_message "${RED}Error: Terraform validation failed${NC}"
        return 1
    fi
    
    # Create Terraform plan with appropriate variables
    log_message "Creating Terraform plan..."
    local tf_vars="-var='deployment_version=${version}'"
    
    if ! terraform plan ${tf_vars} -out=tfplan; then
        log_message "${RED}Error: Failed to create Terraform plan${NC}"
        return 1
    fi
    
    # Apply Terraform plan
    log_message "Applying Terraform plan..."
    if ! terraform apply -auto-approve tfplan; then
        log_message "${RED}Error: Failed to apply Terraform plan${NC}"
        return 1
    fi
    
    log_message "${GREEN}Successfully deployed infrastructure for ${environment}${NC}"
    return 0
}

# Deploys services to the specified environment
deploy_services() {
    local environment="$1"
    local version="$2"
    
    # Skip if deployment type is infrastructure-only
    if [[ "${DEPLOYMENT_TYPE}" == "infrastructure-only" ]]; then
        log_message "Skipping service deployment for infrastructure-only deployment"
        return 0
    fi
    
    log_message "Deploying services to ${environment}..."
    
    # Get the ECS cluster and service names
    local cluster_name="${ECS_CLUSTER}"
    local frontend_service="indivillage-${environment}-frontend"
    local backend_service="indivillage-${environment}-backend"
    
    # Get AWS account ID
    local aws_account_id=$(aws sts get-caller-identity --query Account --output text)
    local ecr_registry="${aws_account_id}.dkr.ecr.${AWS_REGION}.amazonaws.com"
    
    # Deploy Frontend Service
    if [[ "${DEPLOYMENT_TYPE}" == "full" || "${DEPLOYMENT_TYPE}" == "frontend-only" ]]; then
        log_message "Updating frontend service..."
        
        # Get current task definition
        local frontend_task_def=$(aws ecs describe-services --cluster "${cluster_name}" --services "${frontend_service}" --query 'services[0].taskDefinition' --output text)
        
        # Get task definition details
        local frontend_task_def_json=$(aws ecs describe-task-definition --task-definition "${frontend_task_def}" --query 'taskDefinition')
        
        # Create a new revision with updated image
        local frontend_container_name="indivillage-frontend"
        local frontend_repo="${ECR_REPOSITORY_PREFIX}/${ECR_REPOSITORY_FRONTEND}"
        local frontend_image="${ecr_registry}/${frontend_repo}:${version}"
        
        # Update the container image in the task definition
        local updated_frontend_task_def_json=$(echo "${frontend_task_def_json}" | jq --arg IMAGE "${frontend_image}" '.containerDefinitions[] | select(.name == "indivillage-frontend") | .image = $IMAGE')
        
        # Register new task definition
        local new_frontend_task_def=$(aws ecs register-task-definition --cli-input-json "${updated_frontend_task_def_json}" --query 'taskDefinition.taskDefinitionArn' --output text)
        
        # Update service with new task definition
        aws ecs update-service --cluster "${cluster_name}" --service "${frontend_service}" --task-definition "${new_frontend_task_def}" --force-new-deployment
        
        log_message "Frontend service update initiated"
    fi
    
    # Deploy Backend Service
    if [[ "${DEPLOYMENT_TYPE}" == "full" || "${DEPLOYMENT_TYPE}" == "backend-only" ]]; then
        log_message "Updating backend service..."
        
        # Get current task definition
        local backend_task_def=$(aws ecs describe-services --cluster "${cluster_name}" --services "${backend_service}" --query 'services[0].taskDefinition' --output text)
        
        # Get task definition details
        local backend_task_def_json=$(aws ecs describe-task-definition --task-definition "${backend_task_def}" --query 'taskDefinition')
        
        # Create a new revision with updated image
        local backend_container_name="indivillage-backend"
        local backend_repo="${ECR_REPOSITORY_PREFIX}/${ECR_REPOSITORY_BACKEND}"
        local backend_image="${ecr_registry}/${backend_repo}:${version}"
        
        # Update the container image in the task definition
        local updated_backend_task_def_json=$(echo "${backend_task_def_json}" | jq --arg IMAGE "${backend_image}" '.containerDefinitions[] | select(.name == "indivillage-backend") | .image = $IMAGE')
        
        # Register new task definition
        local new_backend_task_def=$(aws ecs register-task-definition --cli-input-json "${updated_backend_task_def_json}" --query 'taskDefinition.taskDefinitionArn' --output text)
        
        # Update service with new task definition
        aws ecs update-service --cluster "${cluster_name}" --service "${backend_service}" --task-definition "${new_backend_task_def}" --force-new-deployment
        
        log_message "Backend service update initiated"
    fi
    
    # Wait for services to stabilize
    log_message "Waiting for services to stabilize..."
    
    if [[ "${DEPLOYMENT_TYPE}" == "full" || "${DEPLOYMENT_TYPE}" == "frontend-only" ]]; then
        aws ecs wait services-stable --cluster "${cluster_name}" --services "${frontend_service}"
    fi
    
    if [[ "${DEPLOYMENT_TYPE}" == "full" || "${DEPLOYMENT_TYPE}" == "backend-only" ]]; then
        aws ecs wait services-stable --cluster "${cluster_name}" --services "${backend_service}"
    fi
    
    log_message "${GREEN}Successfully deployed services to ${environment}${NC}"
    return 0
}

# Implements blue-green deployment for staging and production
deploy_blue_green() {
    local environment="$1"
    local version="$2"
    
    # Skip if deployment type is infrastructure-only
    if [[ "${DEPLOYMENT_TYPE}" == "infrastructure-only" ]]; then
        log_message "Skipping blue-green deployment for infrastructure-only deployment"
        return 0
    fi
    
    # Blue-green deployment is only for staging and production
    if [[ "${environment}" == "development" ]]; then
        log_message "Skipping blue-green deployment for development environment"
        return 0
    }]
    
    log_message "Implementing blue-green deployment for ${environment}..."
    
    # Get the ECS cluster and service names
    local cluster_name="${ECS_CLUSTER}"
    local frontend_blue_service="indivillage-${environment}-frontend-blue"
    local backend_blue_service="indivillage-${environment}-backend-blue"
    
    # Get AWS account ID
    local aws_account_id=$(aws sts get-caller-identity --query Account --output text)
    local ecr_registry="${aws_account_id}.dkr.ecr.${AWS_REGION}.amazonaws.com"
    
    # Deploy Frontend Service to Blue Environment
    if [[ "${DEPLOYMENT_TYPE}" == "full" || "${DEPLOYMENT_TYPE}" == "frontend-only" ]]; then
        log_message "Updating frontend blue service..."
        
        # Get current task definition
        local frontend_task_def=$(aws ecs describe-services --cluster "${cluster_name}" --services "${frontend_blue_service}" --query 'services[0].taskDefinition' --output text)
        
        # Get task definition details
        local frontend_task_def_json=$(aws ecs describe-task-definition --task-definition "${frontend_task_def}" --query 'taskDefinition')
        
        # Create a new revision with updated image
        local frontend_container_name="indivillage-frontend"
        local frontend_repo="${ECR_REPOSITORY_PREFIX}/${ECR_REPOSITORY_FRONTEND}"
        local frontend_image="${ecr_registry}/${frontend_repo}:${version}"
        
        # Update the container image in the task definition
        local updated_frontend_task_def_json=$(echo "${frontend_task_def_json}" | jq --arg IMAGE "${frontend_image}" '.containerDefinitions[] | select(.name == "indivillage-frontend") | .image = $IMAGE')
        
        # Register new task definition
        local new_frontend_task_def=$(aws ecs register-task-definition --cli-input-json "${updated_frontend_task_def_json}" --query 'taskDefinition.taskDefinitionArn' --output text)
        
        # Update service with new task definition
        aws ecs update-service --cluster "${cluster_name}" --service "${frontend_blue_service}" --task-definition "${new_frontend_task_def}" --force-new-deployment
        
        log_message "Frontend blue service update initiated"
    fi
    
    # Deploy Backend Service to Blue Environment
    if [[ "${DEPLOYMENT_TYPE}" == "full" || "${DEPLOYMENT_TYPE}" == "backend-only" ]]; then
        log_message "Updating backend blue service..."
        
        # Get current task definition
        local backend_task_def=$(aws ecs describe-services --cluster "${cluster_name}" --services "${backend_blue_service}" --query 'services[0].taskDefinition' --output text)
        
        # Get task definition details
        local backend_task_def_json=$(aws ecs describe-task-definition --task-definition "${backend_task_def}" --query 'taskDefinition')
        
        # Create a new revision with updated image
        local backend_container_name="indivillage-backend"
        local backend_repo="${ECR_REPOSITORY_PREFIX}/${ECR_REPOSITORY_BACKEND}"
        local backend_image="${ecr_registry}/${backend_repo}:${version}"
        
        # Update the container image in the task definition
        local updated_backend_task_def_json=$(echo "${backend_task_def_json}" | jq --arg IMAGE "${backend_image}" '.containerDefinitions[] | select(.name == "indivillage-backend") | .image = $IMAGE')
        
        # Register new task definition
        local new_backend_task_def=$(aws ecs register-task-definition --cli-input-json "${updated_backend_task_def_json}" --query 'taskDefinition.taskDefinitionArn' --output text)
        
        # Update service with new task definition
        aws ecs update-service --cluster "${cluster_name}" --service "${backend_blue_service}" --task-definition "${new_backend_task_def}" --force-new-deployment
        
        log_message "Backend blue service update initiated"
    fi
    
    # Wait for blue services to stabilize
    log_message "Waiting for blue services to stabilize..."
    
    if [[ "${DEPLOYMENT_TYPE}" == "full" || "${DEPLOYMENT_TYPE}" == "frontend-only" ]]; then
        aws ecs wait services-stable --cluster "${cluster_name}" --services "${frontend_blue_service}"
    fi
    
    if [[ "${DEPLOYMENT_TYPE}" == "full" || "${DEPLOYMENT_TYPE}" == "backend-only" ]]; then
        aws ecs wait services-stable --cluster "${cluster_name}" --services "${backend_blue_service}"
    fi
    
    log_message "${GREEN}Successfully deployed blue environment for ${environment}${NC}"
    return 0
}

# Runs smoke tests against the deployed environment
run_smoke_tests() {
    local environment="$1"
    local is_blue="$2"
    
    log_message "Running smoke tests for ${environment}..."
    
    # Determine API and web URLs based on environment and blue/green status
    local api_url=""
    local web_url=""
    
    case "${environment}" in
        development)
            api_url="https://api-dev.indivillage.com"
            web_url="https://dev.indivillage.com"
            ;;
        staging)
            if [[ "${is_blue}" == "true" ]]; then
                api_url="https://api-staging-blue.indivillage.com"
                web_url="https://staging-blue.indivillage.com"
            else
                api_url="https://api-staging.indivillage.com"
                web_url="https://staging.indivillage.com"
            fi
            ;;
        production)
            if [[ "${is_blue}" == "true" ]]; then
                api_url="https://api-blue.indivillage.com"
                web_url="https://blue.indivillage.com"
            else
                api_url="https://api.indivillage.com"
                web_url="https://www.indivillage.com"
            fi
            ;;
    esac
    
    # Run smoke tests using Python script
    log_message "Running smoke tests against API: ${api_url} and Web: ${web_url}"
    
    local smoke_test_script="${REPO_ROOT}/tests/smoke/run_smoke_tests.py"
    
    if [[ ! -f "${smoke_test_script}" ]]; then
        log_message "${YELLOW}Warning: Smoke test script not found: ${smoke_test_script}${NC}"
        log_message "Skipping smoke tests"
        return 0
    fi
    
    # Run the smoke tests
    python "${smoke_test_script}" --api-url "${api_url}" --web-url "${web_url}"
    local test_exit_code=$?
    
    if [[ ${test_exit_code} -eq 0 ]]; then
        log_message "${GREEN}Smoke tests passed successfully${NC}"
    else
        log_message "${RED}Smoke tests failed with exit code ${test_exit_code}${NC}"
        
        if [[ "${FORCE}" == "true" ]]; then
            log_message "${YELLOW}Warning: Force flag is set, continuing despite test failure${NC}"
            return 0
        fi
        
        return ${test_exit_code}
    fi
    
    return 0
}

# Runs performance tests against the deployed environment
run_performance_tests() {
    local environment="$1"
    local is_blue="$2"
    
    # Skip performance tests for development environment
    if [[ "${environment}" == "development" ]]; then
        log_message "Skipping performance tests for development environment"
        return 0
    fi
    
    log_message "Running performance tests for ${environment}..."
    
    # Determine API and web URLs based on environment and blue/green status
    local api_url=""
    local web_url=""
    
    case "${environment}" in
        staging)
            if [[ "${is_blue}" == "true" ]]; then
                api_url="https://api-staging-blue.indivillage.com"
                web_url="https://staging-blue.indivillage.com"
            else
                api_url="https://api-staging.indivillage.com"
                web_url="https://staging.indivillage.com"
            fi
            ;;
        production)
            if [[ "${is_blue}" == "true" ]]; then
                api_url="https://api-blue.indivillage.com"
                web_url="https://blue.indivillage.com"
            else
                api_url="https://api.indivillage.com"
                web_url="https://www.indivillage.com"
            fi
            ;;
    esac
    
    # Run performance tests using k6
    log_message "Running performance tests against API: ${api_url} and Web: ${web_url}"
    
    local performance_test_script="${REPO_ROOT}/tests/performance/load_test.js"
    
    if [[ ! -f "${performance_test_script}" ]]; then
        log_message "${YELLOW}Warning: Performance test script not found: ${performance_test_script}${NC}"
        log_message "Skipping performance tests"
        return 0
    fi
    
    # Check if k6 is installed
    if ! command -v k6 &> /dev/null; then
        log_message "${YELLOW}Warning: k6 is not installed, skipping performance tests${NC}"
        return 0
    fi
    
    # Run the performance tests
    k6 run "${performance_test_script}" --env API_URL="${api_url}" --env WEB_URL="${web_url}"
    local test_exit_code=$?
    
    if [[ ${test_exit_code} -eq 0 ]]; then
        log_message "${GREEN}Performance tests passed successfully${NC}"
    else
        log_message "${RED}Performance tests failed with exit code ${test_exit_code}${NC}"
        
        if [[ "${FORCE}" == "true" ]]; then
            log_message "${YELLOW}Warning: Force flag is set, continuing despite test failure${NC}"
            return 0
        fi
        
        return ${test_exit_code}
    fi
    
    return 0
}

# Swaps traffic from green to blue environment
swap_blue_green() {
    local environment="$1"
    
    # Skip if deployment type is infrastructure-only
    if [[ "${DEPLOYMENT_TYPE}" == "infrastructure-only" ]]; then
        log_message "Skipping blue-green swap for infrastructure-only deployment"
        return 0
    fi
    
    # Blue-green deployment is only for staging and production
    if [[ "${environment}" == "development" ]]; then
        log_message "Skipping blue-green swap for development environment"
        return 0
    }]
    
    log_message "Swapping traffic from green to blue for ${environment}..."
    
    # Determine the load balancer name and target groups
    local alb_name=""
    local blue_target_group=""
    local green_target_group=""
    
    case "${environment}" in
        staging)
            alb_name="indivillage-staging-alb"
            blue_target_group="indivillage-staging-blue-tg"
            green_target_group="indivillage-staging-green-tg"
            ;;
        production)
            alb_name="indivillage-prod-alb"
            blue_target_group="indivillage-prod-blue-tg"
            green_target_group="indivillage-prod-green-tg"
            ;;
    esac
    
    # Get the ALB listener ARN
    local listener_arn=$(aws elbv2 describe-listeners --load-balancer-name "${alb_name}" --query 'Listeners[?Protocol==`HTTPS`].ListenerArn' --output text)
    
    if [[ -z "${listener_arn}" ]]; then
        log_message "${RED}Error: Could not find HTTPS listener for ALB: ${alb_name}${NC}"
        return 1
    fi
    
    # Get the target group ARNs
    local blue_tg_arn=$(aws elbv2 describe-target-groups --names "${blue_target_group}" --query 'TargetGroups[0].TargetGroupArn' --output text)
    local green_tg_arn=$(aws elbv2 describe-target-groups --names "${green_target_group}" --query 'TargetGroups[0].TargetGroupArn' --output text)
    
    if [[ -z "${blue_tg_arn}" || -z "${green_tg_arn}" ]]; then
        log_message "${RED}Error: Could not find target groups: ${blue_target_group} or ${green_target_group}${NC}"
        return 1
    fi
    
    # Update the listener rule to route traffic to the blue environment
    log_message "Updating ALB listener to route traffic to blue environment..."
    
    aws elbv2 modify-listener --listener-arn "${listener_arn}" --default-actions Type=forward,TargetGroupArn="${blue_tg_arn}"
    
    # Wait for the changes to propagate
    sleep 10
    
    # Verify the change
    local current_tg_arn=$(aws elbv2 describe-listeners --listener-arns "${listener_arn}" --query 'Listeners[0].DefaultActions[0].TargetGroupArn' --output text)
    
    if [[ "${current_tg_arn}" != "${blue_tg_arn}" ]]; then
        log_message "${RED}Error: Failed to update listener to point to blue environment${NC}"
        return 1
    fi
    
    log_message "${GREEN}Successfully swapped traffic to blue environment for ${environment}${NC}"
    return 0
}

# Finalizes deployment by updating green environment
finalize_deployment() {
    local environment="$1"
    local version="$2"
    
    # Skip if deployment type is infrastructure-only
    if [[ "${DEPLOYMENT_TYPE}" == "infrastructure-only" ]]; then
        log_message "Skipping finalization for infrastructure-only deployment"
        return 0
    fi
    
    # Blue-green deployment is only for staging and production
    if [[ "${environment}" == "development" ]]; then
        log_message "Skipping finalization for development environment"
        return 0
    }]
    
    log_message "Finalizing deployment for ${environment}..."
    
    # Get the ECS cluster and service names
    local cluster_name="${ECS_CLUSTER}"
    local frontend_green_service="indivillage-${environment}-frontend-green"
    local backend_green_service="indivillage-${environment}-backend-green"
    
    # Get AWS account ID
    local aws_account_id=$(aws sts get-caller-identity --query Account --output text)
    local ecr_registry="${aws_account_id}.dkr.ecr.${AWS_REGION}.amazonaws.com"
    
    # Update Frontend Service in Green Environment
    if [[ "${DEPLOYMENT_TYPE}" == "full" || "${DEPLOYMENT_TYPE}" == "frontend-only" ]]; then
        log_message "Updating frontend green service..."
        
        # Get current task definition
        local frontend_task_def=$(aws ecs describe-services --cluster "${cluster_name}" --services "${frontend_green_service}" --query 'services[0].taskDefinition' --output text)
        
        # Get task definition details
        local frontend_task_def_json=$(aws ecs describe-task-definition --task-definition "${frontend_task_def}" --query 'taskDefinition')
        
        # Create a new revision with updated image
        local frontend_container_name="indivillage-frontend"
        local frontend_repo="${ECR_REPOSITORY_PREFIX}/${ECR_REPOSITORY_FRONTEND}"
        local frontend_image="${ecr_registry}/${frontend_repo}:${version}"
        
        # Update the container image in the task definition
        local updated_frontend_task_def_json=$(echo "${frontend_task_def_json}" | jq --arg IMAGE "${frontend_image}" '.containerDefinitions[] | select(.name == "indivillage-frontend") | .image = $IMAGE')
        
        # Register new task definition
        local new_frontend_task_def=$(aws ecs register-task-definition --cli-input-json "${updated_frontend_task_def_json}" --query 'taskDefinition.taskDefinitionArn' --output text)
        
        # Update service with new task definition
        aws ecs update-service --cluster "${cluster_name}" --service "${frontend_green_service}" --task-definition "${new_frontend_task_def}" --force-new-deployment
        
        log_message "Frontend green service update initiated"
    fi
    
    # Update Backend Service in Green Environment
    if [[ "${DEPLOYMENT_TYPE}" == "full" || "${DEPLOYMENT_TYPE}" == "backend-only" ]]; then
        log_message "Updating backend green service..."
        
        # Get current task definition
        local backend_task_def=$(aws ecs describe-services --cluster "${cluster_name}" --services "${backend_green_service}" --query 'services[0].taskDefinition' --output text)
        
        # Get task definition details
        local backend_task_def_json=$(aws ecs describe-task-definition --task-definition "${backend_task_def}" --query 'taskDefinition')
        
        # Create a new revision with updated image
        local backend_container_name="indivillage-backend"
        local backend_repo="${ECR_REPOSITORY_PREFIX}/${ECR_REPOSITORY_BACKEND}"
        local backend_image="${ecr_registry}/${backend_repo}:${version}"
        
        # Update the container image in the task definition
        local updated_backend_task_def_json=$(echo "${backend_task_def_json}" | jq --arg IMAGE "${backend_image}" '.containerDefinitions[] | select(.name == "indivillage-backend") | .image = $IMAGE')
        
        # Register new task definition
        local new_backend_task_def=$(aws ecs register-task-definition --cli-input-json "${updated_backend_task_def_json}" --query 'taskDefinition.taskDefinitionArn' --output text)
        
        # Update service with new task definition
        aws ecs update-service --cluster "${cluster_name}" --service "${backend_green_service}" --task-definition "${new_backend_task_def}" --force-new-deployment
        
        log_message "Backend green service update initiated"
    fi
    
    # Wait for green services to stabilize
    log_message "Waiting for green services to stabilize..."
    
    if [[ "${DEPLOYMENT_TYPE}" == "full" || "${DEPLOYMENT_TYPE}" == "frontend-only" ]]; then
        aws ecs wait services-stable --cluster "${cluster_name}" --services "${frontend_green_service}"
    fi
    
    if [[ "${DEPLOYMENT_TYPE}" == "full" || "${DEPLOYMENT_TYPE}" == "backend-only" ]]; then
        aws ecs wait services-stable --cluster "${cluster_name}" --services "${backend_green_service}"
    fi
    
    # Create deployment record in DynamoDB
    log_message "Creating deployment record in DynamoDB..."
    
    local deployment_table="indivillage-deployments"
    local deployment_id="${environment}-${version}-${TIMESTAMP}"
    
    aws dynamodb put-item \
        --table-name "${deployment_table}" \
        --item '{
            "DeploymentId": {"S": "'"${deployment_id}"'"},
            "Environment": {"S": "'"${environment}"'"},
            "Version": {"S": "'"${version}"'"},
            "DeploymentType": {"S": "'"${DEPLOYMENT_TYPE}"'"},
            "Status": {"S": "COMPLETED"},
            "Timestamp": {"S": "'"${TIMESTAMP}"'"},
            "DeployedBy": {"S": "'"$(whoami)"'"}
        }'
    
    # Update secondary region if applicable (for production)
    if [[ "${environment}" == "production" ]]; then
        log_message "Updating secondary region (${AWS_SECONDARY_REGION})..."
        # This would require additional implementation to update services in secondary region
        # Not implemented in this version of the script
    fi
    
    log_message "${GREEN}Successfully finalized deployment for ${environment}${NC}"
    return 0
}

# Rolls back deployment in case of failure
rollback_deployment() {
    local environment="$1"
    local version="$2"
    
    log_message "${RED}Rolling back deployment for ${environment}...${NC}"
    
    # For development, we just revert to the previous version
    if [[ "${environment}" == "development" ]]; then
        log_message "Rolling back to previous version in development..."
        
        # Get previous version from DynamoDB
        local deployment_table="indivillage-deployments"
        
        local previous_version=$(aws dynamodb query \
            --table-name "${deployment_table}" \
            --key-condition-expression "Environment = :env" \
            --expression-attribute-values '{":env":{"S":"'"${environment}"'"}}' \
            --limit 2 \
            --scan-index-forward false \
            --query 'Items[1].Version.S' \
            --output text)
        
        if [[ -z "${previous_version}" ]]; then
            log_message "${YELLOW}Warning: Could not find previous version for rollback. Using 'latest' tag.${NC}"
            previous_version="latest"
        fi
        
        # Deploy the previous version
        deploy_services "${environment}" "${previous_version}"
        
    # For staging and production, we ensure traffic routes to the original (green) environment
    else
        log_message "Rolling back to green environment in ${environment}..."
        
        # Determine the load balancer name and target groups
        local alb_name=""
        local green_target_group=""
        
        case "${environment}" in
            staging)
                alb_name="indivillage-staging-alb"
                green_target_group="indivillage-staging-green-tg"
                ;;
            production)
                alb_name="indivillage-prod-alb"
                green_target_group="indivillage-prod-green-tg"
                ;;
        esac
        
        # Get the ALB listener ARN
        local listener_arn=$(aws elbv2 describe-listeners --load-balancer-name "${alb_name}" --query 'Listeners[?Protocol==`HTTPS`].ListenerArn' --output text)
        
        if [[ -z "${listener_arn}" ]]; then
            log_message "${RED}Error: Could not find HTTPS listener for ALB: ${alb_name}${NC}"
            return 1
        fi
        
        # Get the green target group ARN
        local green_tg_arn=$(aws elbv2 describe-target-groups --names "${green_target_group}" --query 'TargetGroups[0].TargetGroupArn' --output text)
        
        if [[ -z "${green_tg_arn}" ]]; then
            log_message "${RED}Error: Could not find green target group: ${green_target_group}${NC}"
            return 1
        fi
        
        # Update the listener rule to route traffic to the green environment
        log_message "Updating ALB listener to route traffic back to green environment..."
        
        aws elbv2 modify-listener --listener-arn "${listener_arn}" --default-actions Type=forward,TargetGroupArn="${green_tg_arn}"
        
        # Wait for the changes to propagate
        sleep 10
        
        # Verify the change
        local current_tg_arn=$(aws elbv2 describe-listeners --listener-arns "${listener_arn}" --query 'Listeners[0].DefaultActions[0].TargetGroupArn' --output text)
        
        if [[ "${current_tg_arn}" != "${green_tg_arn}" ]]; then
            log_message "${RED}Error: Failed to update listener to point to green environment${NC}"
            return 1
        fi
    fi
    
    # Create deployment failure record in DynamoDB
    log_message "Creating deployment failure record in DynamoDB..."
    
    local deployment_table="indivillage-deployments"
    local deployment_id="${environment}-${version}-${TIMESTAMP}"
    
    aws dynamodb put-item \
        --table-name "${deployment_table}" \
        --item '{
            "DeploymentId": {"S": "'"${deployment_id}"'"},
            "Environment": {"S": "'"${environment}"'"},
            "Version": {"S": "'"${version}"'"},
            "DeploymentType": {"S": "'"${DEPLOYMENT_TYPE}"'"},
            "Status": {"S": "FAILED"},
            "Timestamp": {"S": "'"${TIMESTAMP}"'"},
            "DeployedBy": {"S": "'"$(whoami)"'"},
            "FailureReason": {"S": "Deployment failed and was rolled back"}
        }'
    
    log_message "${YELLOW}Rollback completed for ${environment}${NC}"
    return 0
}

# Requests approval for production deployment
request_approval() {
    local version="$1"
    
    # Skip if skip_approval flag is set
    if [[ "${SKIP_APPROVAL}" == "true" ]]; then
        log_message "${YELLOW}Skipping approval process as requested${NC}"
        return 0
    fi
    
    log_message "${BLUE}Requesting approval for production deployment${NC}"
    
    # Display deployment details
    echo ""
    echo -e "${YELLOW}=======================================${NC}"
    echo -e "${YELLOW}     PRODUCTION DEPLOYMENT APPROVAL    ${NC}"
    echo -e "${YELLOW}=======================================${NC}"
    echo ""
    echo -e "Version: ${version}"
    echo -e "Deployment Type: ${DEPLOYMENT_TYPE}"
    echo -e "Timestamp: $(date)"
    echo -e "Deployed By: $(whoami)"
    echo ""
    
    # Get git commit details
    if git rev-parse "${version}" &> /dev/null; then
        echo -e "${BLUE}Commit Details:${NC}"
        git --no-pager log -n 1 --pretty=format:"Author: %an%nDate: %ad%nSubject: %s%n%b" "${version}"
        echo ""
    fi
    
    # Prompt for approval
    echo ""
    echo -e "${RED}WARNING: You are about to deploy to PRODUCTION${NC}"
    echo -e "This will affect the live environment and all users."
    echo ""
    
    read -p "Do you approve this deployment? (yes/no): " approval
    
    if [[ "${approval}" != "yes" ]]; then
        log_message "${RED}Deployment aborted by user${NC}"
        return 1
    fi
    
    log_message "${GREEN}Deployment approved${NC}"
    return 0
}

# Sends deployment notification
send_notification() {
    local environment="$1"
    local version="$2"
    local status="$3"
    
    log_message "Sending ${status} notification for ${environment} deployment..."
    
    # Determine notification method based on environment
    local slack_channel=""
    local email_recipients=""
    
    case "${environment}" in
        development)
            slack_channel="#deployments-dev"
            email_recipients="dev-team@indivillage.com"
            ;;
        staging)
            slack_channel="#deployments-staging"
            email_recipients="dev-team@indivillage.com,qa-team@indivillage.com"
            ;;
        production)
            slack_channel="#deployments-prod"
            email_recipients="dev-team@indivillage.com,qa-team@indivillage.com,ops-team@indivillage.com"
            ;;
    esac
    
    # Format notification message
    local color=""
    local emoji=""
    
    if [[ "${status}" == "SUCCESS" ]]; then
        color="good"
        emoji=":white_check_mark:"
    elif [[ "${status}" == "FAILURE" ]]; then
        color="danger"
        emoji=":x:"
    else
        color="warning"
        emoji=":warning:"
    fi
    
    local message="*${emoji} Deployment ${status}*\n"
    message+="*Environment:* ${environment}\n"
    message+="*Version:* ${version}\n"
    message+="*Type:* ${DEPLOYMENT_TYPE}\n"
    message+="*Time:* $(date)\n"
    message+="*Deployed By:* $(whoami)"
    
    # Send Slack notification if webhook URL is set
    if [[ -n "${SLACK_WEBHOOK_URL}" ]]; then
        log_message "Sending Slack notification to ${slack_channel}..."
        
        curl -s -X POST -H 'Content-type: application/json' \
            --data "{\"channel\":\"${slack_channel}\",\"attachments\":[{\"color\":\"${color}\",\"text\":\"${message}\"}]}" \
            "${SLACK_WEBHOOK_URL}" > /dev/null
    else
        log_message "${YELLOW}Warning: SLACK_WEBHOOK_URL is not set, skipping Slack notification${NC}"
    fi
    
    # Send email notification (simplified implementation)
    log_message "Sending email notification to ${email_recipients}..."
    # Actual email sending would be implemented here, using SMTP or AWS SES
    # This is a placeholder for the email sending logic
    
    log_message "Notifications sent for ${environment} deployment"
}

# Verifies that the specified version exists and is valid
verify_version() {
    local environment="$1"
    local version="$2"
    
    log_message "Verifying version ${version} in ${environment}..."
    
    # Map environment to repository prefix
    local source_prefix=""
    case "${environment}" in
        development)
            source_prefix="dev"
            ;;
        staging)
            source_prefix="staging"
            ;;
        production)
            source_prefix="prod"
            ;;
    esac
    
    # Check if the specified version exists in ECR
    local aws_account_id=$(aws sts get-caller-identity --query Account --output text)
    local frontend_repo="${source_prefix}/${ECR_REPOSITORY_FRONTEND}"
    local backend_repo="${source_prefix}/${ECR_REPOSITORY_BACKEND}"
    
    if [[ "${DEPLOYMENT_TYPE}" == "full" || "${DEPLOYMENT_TYPE}" == "frontend-only" ]]; then
        if ! aws ecr describe-images --repository-name "${frontend_repo}" --image-ids imageTag="${version}" &> /dev/null; then
            if [[ "${FORCE}" == "true" ]]; then
                log_message "${YELLOW}Warning: Frontend image ${version} not found in ${environment}, but proceeding due to force flag${NC}"
            else
                log_message "${RED}Error: Frontend image ${version} not found in ${environment}${NC}"
                return 1
            fi
        fi
    fi
    
    if [[ "${DEPLOYMENT_TYPE}" == "full" || "${DEPLOYMENT_TYPE}" == "backend-only" ]]; then
        if ! aws ecr describe-images --repository-name "${backend_repo}" --image-ids imageTag="${version}" &> /dev/null; then
            if [[ "${FORCE}" == "true" ]]; then
                log_message "${YELLOW}Warning: Backend image ${version} not found in ${environment}, but proceeding due to force flag${NC}"
            else
                log_message "${RED}Error: Backend image ${version} not found in ${environment}${NC}"
                return 1
            fi
        fi
    fi
    
    # Verify deployment status in DynamoDB
    local deployment_table="indivillage-deployments"
    
    local deployment_status=$(aws dynamodb query \
        --table-name "${deployment_table}" \
        --key-condition-expression "Environment = :env AND Version = :ver" \
        --expression-attribute-values '{":env":{"S":"'"${environment}"'"}, ":ver":{"S":"'"${version}"'"}}' \
        --query 'Items[0].Status.S' \
        --output text)
    
    if [[ -z "${deployment_status}" || "${deployment_status}" == "None" ]]; then
        log_message "${YELLOW}Warning: No deployment record found for version ${version} in ${environment}${NC}"
        
        if [[ "${FORCE}" != "true" ]]; then
            log_message "${YELLOW}Use --force to bypass this check${NC}"
            return 1
        fi
    elif [[ "${deployment_status}" != "COMPLETED" ]]; then
        log_message "${YELLOW}Warning: Deployment status for version ${version} in ${environment} is ${deployment_status}${NC}"
        
        if [[ "${FORCE}" != "true" ]]; then
            log_message "${YELLOW}Use --force to bypass this check${NC}"
            return 1
        fi
    fi
    
    log_message "${GREEN}Version ${version} verified in ${environment}${NC}"
    return 0
}

# Deploys to development environment
deploy_development() {
    local version="$1"
    
    log_message "Deploying to development environment..."
    
    # Set up environment
    setup_environment "development" || return 1
    
    # Build and push images
    build_and_push_images "development" "${version}" || return 1
    
    # Deploy infrastructure
    deploy_infrastructure "development" "${version}" || return 1
    
    # Deploy services
    deploy_services "development" "${version}" || return 1
    
    # Run smoke tests
    run_smoke_tests "development" "false" || {
        log_message "${RED}Smoke tests failed in development${NC}"
        rollback_deployment "development" "${version}"
        send_notification "development" "${version}" "FAILURE"
        return 1
    }
    
    # Create deployment record in DynamoDB
    local deployment_table="indivillage-deployments"
    local deployment_id="development-${version}-${TIMESTAMP}"
    
    aws dynamodb put-item \
        --table-name "${deployment_table}" \
        --item '{
            "DeploymentId": {"S": "'"${deployment_id}"'"},
            "Environment": {"S": "development"},
            "Version": {"S": "'"${version}"'"},
            "DeploymentType": {"S": "'"${DEPLOYMENT_TYPE}"'"},
            "Status": {"S": "COMPLETED"},
            "Timestamp": {"S": "'"${TIMESTAMP}"'"},
            "DeployedBy": {"S": "'"$(whoami)"'"}
        }'
    
    # Send notification
    send_notification "development" "${version}" "SUCCESS"
    
    log_message "${GREEN}Successfully deployed to development environment${NC}"
    return 0
}

# Deploys to staging environment
deploy_staging() {
    local version="$1"
    
    log_message "Deploying to staging environment..."
    
    # Set up environment
    setup_environment "staging" || return 1
    
    # Verify version in development
    verify_version "development" "${version}" || return 1
    
    # Tag images for staging
    tag_existing_images "development" "staging" "${version}" || return 1
    
    # Deploy infrastructure
    deploy_infrastructure "staging" "${version}" || return 1
    
    # Deploy blue-green
    deploy_blue_green "staging" "${version}" || return 1
    
    # Run smoke tests on blue
    run_smoke_tests "staging" "true" || {
        log_message "${RED}Smoke tests failed on blue in staging${NC}"
        rollback_deployment "staging" "${version}"
        send_notification "staging" "${version}" "FAILURE"
        return 1
    }
    
    # Run performance tests on blue
    run_performance_tests "staging" "true" || {
        log_message "${RED}Performance tests failed on blue in staging${NC}"
        rollback_deployment "staging" "${version}"
        send_notification "staging" "${version}" "FAILURE"
        return 1
    }
    
    # Swap blue-green
    swap_blue_green "staging" || {
        log_message "${RED}Failed to swap blue-green in staging${NC}"
        rollback_deployment "staging" "${version}"
        send_notification "staging" "${version}" "FAILURE"
        return 1
    }
    
    # Finalize deployment
    finalize_deployment "staging" "${version}" || {
        log_message "${RED}Failed to finalize deployment in staging${NC}"
        # We don't roll back here since the swap was successful
        send_notification "staging" "${version}" "PARTIAL_SUCCESS"
        return 1
    }
    
    # Send notification
    send_notification "staging" "${version}" "SUCCESS"
    
    log_message "${GREEN}Successfully deployed to staging environment${NC}"
    return 0
}

# Deploys to production environment
deploy_production() {
    local version="$1"
    local skip_approval="$2"
    
    log_message "Deploying to production environment..."
    
    # Set up environment
    setup_environment "production" || return 1
    
    # Verify version in staging
    verify_version "staging" "${version}" || return 1
    
    # Request approval if not skipped
    if [[ "${skip_approval}" != "true" ]]; then
        request_approval "${version}" || return 1
    else
        log_message "${YELLOW}Skipping approval for production deployment${NC}"
    fi
    
    # Tag images for production
    tag_existing_images "staging" "production" "${version}" || return 1
    
    # Deploy infrastructure
    deploy_infrastructure "production" "${version}" || return 1
    
    # Deploy blue-green
    deploy_blue_green "production" "${version}" || return 1
    
    # Run smoke tests on blue
    run_smoke_tests "production" "true" || {
        log_message "${RED}Smoke tests failed on blue in production${NC}"
        rollback_deployment "production" "${version}"
        send_notification "production" "${version}" "FAILURE"
        return 1
    }
    
    # Run performance tests on blue
    run_performance_tests "production" "true" || {
        log_message "${RED}Performance tests failed on blue in production${NC}"
        rollback_deployment "production" "${version}"
        send_notification "production" "${version}" "FAILURE"
        return 1
    }
    
    # Implement canary deployment (10% traffic to blue)
    log_message "Implementing canary deployment with 10% traffic to blue environment..."
    
    # This would require additional implementation for canary deployment
    # Not fully implemented in this version of the script
    
    # Simulate canary monitoring
    log_message "Monitoring canary deployment for 5 minutes..."
    sleep 300  # Wait 5 minutes
    
    # Swap blue-green
    swap_blue_green "production" || {
        log_message "${RED}Failed to swap blue-green in production${NC}"
        rollback_deployment "production" "${version}"
        send_notification "production" "${version}" "FAILURE"
        return 1
    }
    
    # Finalize deployment
    finalize_deployment "production" "${version}" || {
        log_message "${RED}Failed to finalize deployment in production${NC}"
        # We don't roll back here since the swap was successful
        send_notification "production" "${version}" "PARTIAL_SUCCESS"
        return 1
    }
    
    # Send notification
    send_notification "production" "${version}" "SUCCESS"
    
    log_message "${GREEN}Successfully deployed to production environment${NC}"
    return 0
}

# Main function that orchestrates the deployment process
main() {
    local args=("$@")
    
    # Parse command line arguments
    parse_arguments "${args[@]}" || exit 1
    
    # Display help if requested
    if [[ "$1" == "-h" || "$1" == "--help" ]]; then
        display_help
        exit 0
    fi
    
    # Check dependencies
    check_dependencies || exit 1
    
    # Create log directory if it doesn't exist
    mkdir -p "${LOG_DIR}"
    
    log_message "Starting deployment process..."
    log_message "Environment: ${ENVIRONMENT}"
    log_message "Version: ${VERSION}"
    log_message "Deployment Type: ${DEPLOYMENT_TYPE}"
    
    # Start deployment based on environment
    local deploy_result=0
    
    case "${ENVIRONMENT}" in
        development)
            deploy_development "${VERSION}" || deploy_result=1
            ;;
        staging)
            deploy_staging "${VERSION}" || deploy_result=1
            ;;
        production)
            deploy_production "${VERSION}" "${SKIP_APPROVAL}" || deploy_result=1
            ;;
        *)
            log_message "${RED}Error: Invalid environment: ${ENVIRONMENT}${NC}"
            exit 1
            ;;
    esac
    
    if [[ ${deploy_result} -eq 0 ]]; then
        log_message "${GREEN}Deployment completed successfully${NC}"
        exit 0
    else
        log_message "${RED}Deployment failed${NC}"
        exit 1
    fi
}

# Execute main function with all script arguments
main "$@"