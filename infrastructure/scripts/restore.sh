#!/bin/bash
#
# IndiVillage.com Website Restoration Script
# 
# This script automates the restoration process for the IndiVillage.com website,
# including database restoration, file storage restoration, and configuration
# restoration from backups.
#
# The script handles environment-specific settings, decryption, and
# verification of restored components.
#
# Version: 1.0.0
# Dependencies: aws-cli v2.x, postgresql-client 13.x

# Set strict mode
set -eo pipefail

# Global variables
SCRIPT_DIR=$(dirname "${BASH_SOURCE[0]}")
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="/var/log/indivillage/restore_${TIMESTAMP}.log"
TEMP_DIR="/tmp/indivillage_restore_${TIMESTAMP}"

# Default values
ENVIRONMENT=""
RESTORE_TYPE="full"
BACKUP_FILE=""
ENCRYPTION_KEY=""
SKIP_VERIFY=false
FORCE=false

# Create log directory if it doesn't exist
mkdir -p "$(dirname "${LOG_FILE}")"

# Function to log messages
log_message() {
    local message="$1"
    local timestamp=$(date "+%Y-%m-%d %H:%M:%S")
    echo "[${timestamp}] ${message}"
    echo "[${timestamp}] ${message}" >> "${LOG_FILE}"
}

# Function to check if required dependencies are installed
check_dependencies() {
    log_message "Checking dependencies..."
    
    # Check for AWS CLI
    if ! command -v aws &> /dev/null; then
        log_message "ERROR: AWS CLI is not installed. Please install aws-cli v2.x."
        return 1
    fi
    
    # Check for PostgreSQL client
    if ! command -v pg_restore &> /dev/null; then
        log_message "ERROR: PostgreSQL client is not installed. Please install postgresql-client."
        return 1
    fi
    
    # Check for required environment variables
    if [[ -z "${AWS_ACCESS_KEY_ID}" || -z "${AWS_SECRET_ACCESS_KEY}" ]]; then
        log_message "WARNING: AWS credentials not found in environment variables."
        log_message "         Ensure AWS credentials are configured via ~/.aws/credentials or instance role."
    fi
    
    log_message "All required dependencies are available."
    return 0
}

# Function to create temporary directory
create_temp_directory() {
    if [[ ! -d "${TEMP_DIR}" ]]; then
        mkdir -p "${TEMP_DIR}"
        log_message "Created temporary directory: ${TEMP_DIR}"
    else
        log_message "Using existing temporary directory: ${TEMP_DIR}"
    fi
    
    return "${TEMP_DIR}"
}

# Function to get database connection parameters
get_db_connection_params() {
    local environment="$1"
    local config_file="${SCRIPT_DIR}/../config/${environment}/database.conf"
    
    if [[ ! -f "${config_file}" ]]; then
        log_message "ERROR: Database configuration file not found: ${config_file}"
        return 1
    fi
    
    # Source the configuration file to get the parameters
    source "${config_file}"
    
    # Return parameters as an array
    echo "${DB_HOST} ${DB_PORT} ${DB_NAME} ${DB_USER} ${DB_PASSWORD}"
}

# Function to list available backups
list_available_backups() {
    local environment="$1"
    local backup_type="$2"
    local bucket_name="indivillage-backups-${environment}"
    local prefix=""
    
    case "${backup_type}" in
        "full")
            prefix="full/"
            ;;
        "db-only")
            prefix="database/"
            ;;
        "files-only")
            prefix="files/"
            ;;
        "config-only")
            prefix="config/"
            ;;
        *)
            log_message "ERROR: Invalid backup type: ${backup_type}"
            return 1
            ;;
    esac
    
    log_message "Listing available ${backup_type} backups for ${environment} environment..."
    
    # Get list of backups from S3
    local backups=$(aws s3 ls "s3://${bucket_name}/${prefix}" | grep -v "PRE" | sort -r | awk '{print $4}')
    
    if [[ -z "${backups}" ]]; then
        log_message "ERROR: No backups found for ${environment} environment of type ${backup_type}"
        return 1
    fi
    
    # Print available backups
    log_message "Available backups:"
    local i=1
    local backup_array=()
    
    while IFS= read -r line; do
        backup_array+=("$line")
        log_message "  ${i}. ${line}"
        ((i++))
    done <<< "${backups}"
    
    echo "${backup_array[@]}"
}

# Function to download backup from S3
download_backup() {
    local environment="$1"
    local backup_type="$2"
    local backup_file="$3"
    local output_dir="$4"
    local bucket_name="indivillage-backups-${environment}"
    local prefix=""
    
    case "${backup_type}" in
        "full")
            prefix="full/"
            ;;
        "db-only")
            prefix="database/"
            ;;
        "files-only")
            prefix="files/"
            ;;
        "config-only")
            prefix="config/"
            ;;
        *)
            log_message "ERROR: Invalid backup type: ${backup_type}"
            return ""
            ;;
    esac
    
    local s3_key="${prefix}${backup_file}"
    local output_file="${output_dir}/$(basename "${backup_file}")"
    
    log_message "Downloading backup: s3://${bucket_name}/${s3_key}"
    if aws s3 cp "s3://${bucket_name}/${s3_key}" "${output_file}"; then
        log_message "Successfully downloaded backup to ${output_file}"
        echo "${output_file}"
    else
        log_message "ERROR: Failed to download backup from S3"
        echo ""
    fi
}

# Function to decrypt backup file
decrypt_backup() {
    local file_path="$1"
    local encryption_key="$2"
    local output_file="${file_path%.enc}"
    
    if [[ "${file_path}" != *".enc" ]]; then
        log_message "File does not appear to be encrypted: ${file_path}"
        echo "${file_path}"
        return
    fi
    
    log_message "Decrypting file: ${file_path}"
    if openssl enc -aes-256-cbc -d -in "${file_path}" -out "${output_file}" -k "${encryption_key}"; then
        log_message "Successfully decrypted to ${output_file}"
        echo "${output_file}"
    else
        log_message "ERROR: Failed to decrypt file"
        echo ""
    fi
}

# Function to decompress backup file
decompress_backup() {
    local file_path="$1"
    local output_file=""
    
    if [[ "${file_path}" == *".gz" ]]; then
        output_file="${file_path%.gz}"
        log_message "Decompressing file: ${file_path}"
        if gunzip -c "${file_path}" > "${output_file}"; then
            log_message "Successfully decompressed to ${output_file}"
            echo "${output_file}"
        else
            log_message "ERROR: Failed to decompress file"
            echo ""
        fi
    else
        log_message "File does not appear to be compressed with gzip: ${file_path}"
        echo "${file_path}"
    fi
}

# Function to extract tar archive
extract_backup() {
    local file_path="$1"
    local output_dir="$2"
    
    if [[ "${file_path}" != *".tar" && "${file_path}" != *".tar.gz" ]]; then
        log_message "File does not appear to be a tar archive: ${file_path}"
        return 1
    fi
    
    log_message "Extracting archive: ${file_path} to ${output_dir}"
    if tar -xf "${file_path}" -C "${output_dir}"; then
        log_message "Successfully extracted archive"
        return 0
    else
        log_message "ERROR: Failed to extract archive"
        return 1
    fi
}

# Function to restore database
restore_database() {
    local environment="$1"
    local backup_file="$2"
    
    log_message "Restoring database from ${backup_file} for ${environment} environment..."
    
    # Get database connection parameters
    read -r DB_HOST DB_PORT DB_NAME DB_USER DB_PASSWORD <<< "$(get_db_connection_params "${environment}")"
    
    if [[ -z "${DB_HOST}" ]]; then
        log_message "ERROR: Failed to get database connection parameters"
        return 1
    fi
    
    # Export password for pg_restore
    export PGPASSWORD="${DB_PASSWORD}"
    
    # Verify if this is a PostgreSQL dump file
    if ! file "${backup_file}" | grep -q "PostgreSQL"; then
        log_message "ERROR: The backup file does not appear to be a valid PostgreSQL dump"
        return 1
    fi
    
    # Drop and recreate database if it exists
    if [[ "${FORCE}" == "true" ]]; then
        log_message "Force flag is set. Dropping existing database if it exists..."
        psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -d "postgres" -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='${DB_NAME}';" > /dev/null 2>&1 || true
        psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -d "postgres" -c "DROP DATABASE IF EXISTS ${DB_NAME};" > /dev/null 2>&1
        psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -d "postgres" -c "CREATE DATABASE ${DB_NAME};" > /dev/null 2>&1
    fi
    
    # Restore the database
    if pg_restore -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -d "${DB_NAME}" -v "${backup_file}" > "${TEMP_DIR}/pg_restore.log" 2>&1; then
        log_message "Successfully restored database"
        return 0
    else
        # Check if there were only non-fatal errors
        if grep -q "warning" "${TEMP_DIR}/pg_restore.log" && ! grep -q "error" "${TEMP_DIR}/pg_restore.log"; then
            log_message "Database restored with warnings. See log for details: ${TEMP_DIR}/pg_restore.log"
            return 0
        else
            log_message "ERROR: Failed to restore database. See log for details: ${TEMP_DIR}/pg_restore.log"
            return 1
        fi
    fi
}

# Function to restore S3 files
restore_s3_files() {
    local environment="$1"
    local backup_dir="$2"
    
    log_message "Restoring files to S3 buckets for ${environment} environment..."
    
    # Define bucket names based on environment
    local uploads_bucket="indivillage-uploads-${environment}"
    local assets_bucket="indivillage-assets-${environment}"
    local processed_bucket="indivillage-processed-${environment}"
    
    # Check if backup directory contains the expected subdirectories
    if [[ ! -d "${backup_dir}/uploads" || ! -d "${backup_dir}/assets" || ! -d "${backup_dir}/processed" ]]; then
        log_message "ERROR: Backup directory does not contain expected subdirectories"
        return 1
    fi
    
    # Restore uploads bucket
    log_message "Restoring uploads bucket..."
    if aws s3 sync "${backup_dir}/uploads/" "s3://${uploads_bucket}/" --delete; then
        log_message "Successfully restored uploads bucket"
    else
        log_message "ERROR: Failed to restore uploads bucket"
        return 1
    fi
    
    # Restore assets bucket
    log_message "Restoring assets bucket..."
    if aws s3 sync "${backup_dir}/assets/" "s3://${assets_bucket}/" --delete; then
        log_message "Successfully restored assets bucket"
    else
        log_message "ERROR: Failed to restore assets bucket"
        return 1
    fi
    
    # Restore processed bucket
    log_message "Restoring processed bucket..."
    if aws s3 sync "${backup_dir}/processed/" "s3://${processed_bucket}/" --delete; then
        log_message "Successfully restored processed bucket"
    else
        log_message "ERROR: Failed to restore processed bucket"
        return 1
    fi
    
    log_message "Successfully restored all S3 buckets"
    return 0
}

# Function to restore configuration files
restore_config() {
    local environment="$1"
    local backup_dir="$2"
    
    log_message "Restoring configuration files for ${environment} environment..."
    
    # Define configuration directories based on environment
    local config_dir="/etc/indivillage/${environment}"
    local app_config_dir="/opt/indivillage/config/${environment}"
    
    # Create directories if they don't exist
    mkdir -p "${config_dir}"
    mkdir -p "${app_config_dir}"
    
    # Check if backup directory contains the expected configuration files
    if [[ ! -d "${backup_dir}/etc" || ! -d "${backup_dir}/app" ]]; then
        log_message "ERROR: Backup directory does not contain expected configuration directories"
        return 1
    fi
    
    # Restore system configuration files
    log_message "Restoring system configuration files..."
    if rsync -av "${backup_dir}/etc/" "${config_dir}/" --delete; then
        log_message "Successfully restored system configuration files"
    else
        log_message "ERROR: Failed to restore system configuration files"
        return 1
    fi
    
    # Restore application configuration files
    log_message "Restoring application configuration files..."
    if rsync -av "${backup_dir}/app/" "${app_config_dir}/" --delete; then
        log_message "Successfully restored application configuration files"
    else
        log_message "ERROR: Failed to restore application configuration files"
        return 1
    fi
    
    log_message "Successfully restored all configuration files"
    return 0
}

# Function to verify database restoration
verify_database_restoration() {
    local environment="$1"
    
    log_message "Verifying database restoration for ${environment} environment..."
    
    # Get database connection parameters
    read -r DB_HOST DB_PORT DB_NAME DB_USER DB_PASSWORD <<< "$(get_db_connection_params "${environment}")"
    
    if [[ -z "${DB_HOST}" ]]; then
        log_message "ERROR: Failed to get database connection parameters"
        return 1
    fi
    
    # Export password for psql
    export PGPASSWORD="${DB_PASSWORD}"
    
    # Check if database is accessible
    if ! psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -d "${DB_NAME}" -c "SELECT 1;" > /dev/null 2>&1; then
        log_message "ERROR: Failed to connect to the restored database"
        return 1
    fi
    
    # Check for critical tables
    log_message "Checking for critical tables..."
    critical_tables=("services" "case_studies" "impact_stories" "uploads" "form_submissions")
    
    for table in "${critical_tables[@]}"; do
        if ! psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -d "${DB_NAME}" -c "SELECT COUNT(*) FROM ${table};" > /dev/null 2>&1; then
            log_message "ERROR: Critical table not found: ${table}"
            return 1
        fi
    done
    
    # Check for data integrity with a few sample queries
    log_message "Checking data integrity with sample queries..."
    
    # Check total number of services
    services_count=$(psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -d "${DB_NAME}" -t -c "SELECT COUNT(*) FROM services;")
    log_message "  Total services: ${services_count}"
    
    # Check total number of case studies
    case_studies_count=$(psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -d "${DB_NAME}" -t -c "SELECT COUNT(*) FROM case_studies;")
    log_message "  Total case studies: ${case_studies_count}"
    
    # Check total number of impact stories
    impact_stories_count=$(psql -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -d "${DB_NAME}" -t -c "SELECT COUNT(*) FROM impact_stories;")
    log_message "  Total impact stories: ${impact_stories_count}"
    
    # Additional checks can be added here based on application-specific requirements
    
    log_message "Database verification complete. All checks passed."
    return 0
}

# Function to verify S3 restoration
verify_s3_restoration() {
    local environment="$1"
    
    log_message "Verifying S3 buckets restoration for ${environment} environment..."
    
    # Define bucket names based on environment
    local uploads_bucket="indivillage-uploads-${environment}"
    local assets_bucket="indivillage-assets-${environment}"
    local processed_bucket="indivillage-processed-${environment}"
    
    # Check if buckets exist
    log_message "Checking if buckets exist and are accessible..."
    
    if ! aws s3 ls "s3://${uploads_bucket}" > /dev/null 2>&1; then
        log_message "ERROR: Uploads bucket does not exist or is not accessible: ${uploads_bucket}"
        return 1
    fi
    
    if ! aws s3 ls "s3://${assets_bucket}" > /dev/null 2>&1; then
        log_message "ERROR: Assets bucket does not exist or is not accessible: ${assets_bucket}"
        return 1
    fi
    
    if ! aws s3 ls "s3://${processed_bucket}" > /dev/null 2>&1; then
        log_message "ERROR: Processed bucket does not exist or is not accessible: ${processed_bucket}"
        return 1
    fi
    
    # Check for key files/directories in each bucket
    log_message "Checking for key files in buckets..."
    
    # Count objects in each bucket
    uploads_count=$(aws s3 ls "s3://${uploads_bucket}" --recursive | wc -l)
    assets_count=$(aws s3 ls "s3://${assets_bucket}" --recursive | wc -l)
    processed_count=$(aws s3 ls "s3://${processed_bucket}" --recursive | wc -l)
    
    log_message "  Uploads bucket contains ${uploads_count} objects"
    log_message "  Assets bucket contains ${assets_count} objects"
    log_message "  Processed bucket contains ${processed_count} objects"
    
    # Additional checks can be added here based on application-specific requirements
    
    log_message "S3 buckets verification complete. All checks passed."
    return 0
}

# Function to verify configuration restoration
verify_config_restoration() {
    local environment="$1"
    
    log_message "Verifying configuration files restoration for ${environment} environment..."
    
    # Define configuration directories based on environment
    local config_dir="/etc/indivillage/${environment}"
    local app_config_dir="/opt/indivillage/config/${environment}"
    
    # Check if directories exist
    if [[ ! -d "${config_dir}" ]]; then
        log_message "ERROR: System configuration directory does not exist: ${config_dir}"
        return 1
    fi
    
    if [[ ! -d "${app_config_dir}" ]]; then
        log_message "ERROR: Application configuration directory does not exist: ${app_config_dir}"
        return 1
    fi
    
    # Check for critical configuration files
    log_message "Checking for critical configuration files..."
    critical_files=(
        "${config_dir}/database.conf"
        "${config_dir}/aws.conf"
        "${config_dir}/app.conf"
        "${app_config_dir}/settings.json"
        "${app_config_dir}/environment.js"
    )
    
    for file in "${critical_files[@]}"; do
        if [[ ! -f "${file}" ]]; then
            log_message "ERROR: Critical configuration file not found: ${file}"
            return 1
        fi
        
        # Check if file is readable
        if [[ ! -r "${file}" ]]; then
            log_message "ERROR: Configuration file is not readable: ${file}"
            return 1
        fi
    done
    
    # Check syntax of critical configuration files
    log_message "Checking syntax of critical configuration files..."
    
    # Check JSON files
    json_files=($(find "${app_config_dir}" -name "*.json"))
    for file in "${json_files[@]}"; do
        if ! jq . "${file}" > /dev/null 2>&1; then
            log_message "ERROR: Invalid JSON syntax in file: ${file}"
            return 1
        fi
    done
    
    # Additional checks can be added here based on application-specific requirements
    
    log_message "Configuration verification complete. All checks passed."
    return 0
}

# Function to clean up temporary files
cleanup_temp_files() {
    local temp_dir="$1"
    
    log_message "Cleaning up temporary files..."
    if [[ -d "${temp_dir}" ]]; then
        rm -rf "${temp_dir}"
        log_message "Removed temporary directory: ${temp_dir}"
    fi
}

# Function to send notification about restoration status
send_notification() {
    local status="$1"
    local environment="$2"
    local details="$3"
    
    log_message "Sending notification about restoration status..."
    
    # Determine notification method based on environment
    local notification_method=""
    case "${environment}" in
        "development")
            notification_method="email"
            ;;
        "staging"|"production")
            notification_method="sns"
            ;;
        *)
            notification_method="email"
            ;;
    esac
    
    # Format notification message
    local message="IndiVillage Restoration ${status}: ${environment} environment\n\nDetails:\n${details}\n\nLog file: ${LOG_FILE}"
    
    # Send notification via appropriate channel
    case "${notification_method}" in
        "email")
            # Email notification (simplified, replace with actual email sending logic)
            log_message "Sending email notification to admin@indivillage.com"
            echo -e "${message}" | mail -s "IndiVillage Restoration ${status}" admin@indivillage.com
            ;;
        "sns")
            # SNS notification
            log_message "Sending SNS notification"
            local topic_arn="arn:aws:sns:us-east-1:123456789012:IndiVillage-${environment}-Notifications"
            aws sns publish --topic-arn "${topic_arn}" --message "${message}" --subject "IndiVillage Restoration ${status}"
            ;;
    esac
    
    log_message "Notification sent"
}

# Function to print help message
print_help() {
    echo "IndiVillage Website Restoration Script"
    echo ""
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  -e, --environment ENV    Specify the environment (development, staging, production)"
    echo "  -t, --type TYPE          Specify restore type (full, db-only, files-only, config-only)"
    echo "                           Default: full"
    echo "  -b, --backup FILE        Specify the backup file to restore from"
    echo "  -d, --directory DIR      Specify the temporary directory for restoration work"
    echo "                           Default: /tmp/indivillage_restore_<timestamp>"
    echo "  -k, --key KEY            Specify the encryption key for encrypted backups"
    echo "  --no-verify              Skip verification after restoration"
    echo "  --force                  Force restoration without confirmation prompts"
    echo "  -h, --help               Display this help message"
    echo ""
    echo "Examples:"
    echo "  $0 -e production -t full"
    echo "  $0 -e staging -t db-only -b database_backup_20230101.sql.gz"
    echo "  $0 -e development -t files-only --no-verify"
    echo ""
}

# Main function
main() {
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case "$1" in
            -e|--environment)
                ENVIRONMENT="$2"
                shift 2
                ;;
            -t|--type)
                RESTORE_TYPE="$2"
                shift 2
                ;;
            -b|--backup)
                BACKUP_FILE="$2"
                shift 2
                ;;
            -d|--directory)
                TEMP_DIR="$2"
                shift 2
                ;;
            -k|--key)
                ENCRYPTION_KEY="$2"
                shift 2
                ;;
            --no-verify)
                SKIP_VERIFY=true
                shift
                ;;
            --force)
                FORCE=true
                shift
                ;;
            -h|--help)
                print_help
                exit 0
                ;;
            *)
                echo "Unknown option: $1" >&2
                print_help
                exit 1
                ;;
        esac
    done
    
    # Validate required parameters
    if [[ -z "${ENVIRONMENT}" ]]; then
        echo "ERROR: Environment must be specified" >&2
        print_help
        exit 1
    fi
    
    # Validate environment
    if [[ "${ENVIRONMENT}" != "development" && "${ENVIRONMENT}" != "staging" && "${ENVIRONMENT}" != "production" ]]; then
        echo "ERROR: Invalid environment. Must be one of: development, staging, production" >&2
        exit 1
    fi
    
    # Validate restore type
    if [[ "${RESTORE_TYPE}" != "full" && "${RESTORE_TYPE}" != "db-only" && "${RESTORE_TYPE}" != "files-only" && "${RESTORE_TYPE}" != "config-only" ]]; then
        echo "ERROR: Invalid restore type. Must be one of: full, db-only, files-only, config-only" >&2
        exit 1
    fi
    
    # Set up logging
    log_message "Starting IndiVillage.com website restoration"
    log_message "Environment: ${ENVIRONMENT}"
    log_message "Restore type: ${RESTORE_TYPE}"
    
    # Check dependencies
    if ! check_dependencies; then
        log_message "ERROR: Dependency check failed. Aborting."
        exit 1
    fi
    
    # Create temporary directory
    create_temp_directory
    
    # If backup file not specified, list available backups and prompt user to select one
    if [[ -z "${BACKUP_FILE}" ]]; then
        backup_array=($(list_available_backups "${ENVIRONMENT}" "${RESTORE_TYPE}"))
        if [[ "${#backup_array[@]}" -eq 0 ]]; then
            log_message "ERROR: No backups found. Aborting."
            exit 1
        fi
        
        echo ""
        echo "Please select a backup to restore (or press Ctrl+C to abort):"
        select backup in "${backup_array[@]}"; do
            if [[ -n "${backup}" ]]; then
                BACKUP_FILE="${backup}"
                break
            else
                echo "Invalid selection. Please try again."
            fi
        done
        
        log_message "Selected backup: ${BACKUP_FILE}"
    fi
    
    # Confirm restoration if not forced
    if [[ "${FORCE}" != "true" ]]; then
        echo ""
        echo "WARNING: This will restore the ${ENVIRONMENT} environment with backup ${BACKUP_FILE}."
        echo "         All existing data will be overwritten."
        echo ""
        read -p "Are you sure you want to continue? (y/N): " confirm
        if [[ "${confirm}" != "y" && "${confirm}" != "Y" ]]; then
            log_message "Restoration aborted by user."
            exit 0
        fi
    fi
    
    # Download backup
    backup_path=$(download_backup "${ENVIRONMENT}" "${RESTORE_TYPE}" "${BACKUP_FILE}" "${TEMP_DIR}")
    if [[ -z "${backup_path}" ]]; then
        log_message "ERROR: Failed to download backup. Aborting."
        exit 1
    fi
    
    # Decrypt backup if encrypted
    if [[ "${backup_path}" == *".enc" ]]; then
        if [[ -z "${ENCRYPTION_KEY}" ]]; then
            read -sp "Enter encryption key: " ENCRYPTION_KEY
            echo ""
        fi
        
        decrypted_path=$(decrypt_backup "${backup_path}" "${ENCRYPTION_KEY}")
        if [[ -z "${decrypted_path}" ]]; then
            log_message "ERROR: Failed to decrypt backup. Aborting."
            exit 1
        fi
        backup_path="${decrypted_path}"
    fi
    
    # Decompress backup if compressed
    if [[ "${backup_path}" == *".gz" ]]; then
        decompressed_path=$(decompress_backup "${backup_path}")
        if [[ -z "${decompressed_path}" ]]; then
            log_message "ERROR: Failed to decompress backup. Aborting."
            exit 1
        fi
        backup_path="${decompressed_path}"
    fi
    
    # Extract backup if it's a tarball
    if [[ "${backup_path}" == *".tar" ]]; then
        extract_dir="${TEMP_DIR}/extracted"
        mkdir -p "${extract_dir}"
        
        if ! extract_backup "${backup_path}" "${extract_dir}"; then
            log_message "ERROR: Failed to extract backup. Aborting."
            exit 1
        fi
        backup_path="${extract_dir}"
    fi
    
    # Perform restoration based on type
    exit_code=0
    case "${RESTORE_TYPE}" in
        "full")
            # Full restoration includes database, files, and configuration
            if [[ -f "${backup_path}/database.sql" ]]; then
                if ! restore_database "${ENVIRONMENT}" "${backup_path}/database.sql"; then
                    log_message "ERROR: Failed to restore database."
                    exit_code=1
                fi
            else
                log_message "ERROR: Database backup file not found in full backup."
                exit_code=1
            fi
            
            if [[ -d "${backup_path}/files" ]]; then
                if ! restore_s3_files "${ENVIRONMENT}" "${backup_path}/files"; then
                    log_message "ERROR: Failed to restore S3 files."
                    exit_code=1
                fi
            else
                log_message "ERROR: Files directory not found in full backup."
                exit_code=1
            fi
            
            if [[ -d "${backup_path}/config" ]]; then
                if ! restore_config "${ENVIRONMENT}" "${backup_path}/config"; then
                    log_message "ERROR: Failed to restore configuration files."
                    exit_code=1
                fi
            else
                log_message "ERROR: Config directory not found in full backup."
                exit_code=1
            fi
            ;;
            
        "db-only")
            # Database-only restoration
            if ! restore_database "${ENVIRONMENT}" "${backup_path}"; then
                log_message "ERROR: Failed to restore database."
                exit_code=1
            fi
            ;;
            
        "files-only")
            # Files-only restoration
            if ! restore_s3_files "${ENVIRONMENT}" "${backup_path}"; then
                log_message "ERROR: Failed to restore S3 files."
                exit_code=1
            fi
            ;;
            
        "config-only")
            # Configuration-only restoration
            if ! restore_config "${ENVIRONMENT}" "${backup_path}"; then
                log_message "ERROR: Failed to restore configuration files."
                exit_code=1
            fi
            ;;
    esac
    
    # Verify restoration if not skipped
    if [[ "${SKIP_VERIFY}" != "true" && "${exit_code}" -eq 0 ]]; then
        log_message "Verifying restoration..."
        
        case "${RESTORE_TYPE}" in
            "full")
                if ! verify_database_restoration "${ENVIRONMENT}"; then
                    log_message "ERROR: Database verification failed."
                    exit_code=1
                fi
                
                if ! verify_s3_restoration "${ENVIRONMENT}"; then
                    log_message "ERROR: S3 files verification failed."
                    exit_code=1
                fi
                
                if ! verify_config_restoration "${ENVIRONMENT}"; then
                    log_message "ERROR: Configuration verification failed."
                    exit_code=1
                fi
                ;;
                
            "db-only")
                if ! verify_database_restoration "${ENVIRONMENT}"; then
                    log_message "ERROR: Database verification failed."
                    exit_code=1
                fi
                ;;
                
            "files-only")
                if ! verify_s3_restoration "${ENVIRONMENT}"; then
                    log_message "ERROR: S3 files verification failed."
                    exit_code=1
                fi
                ;;
                
            "config-only")
                if ! verify_config_restoration "${ENVIRONMENT}"; then
                    log_message "ERROR: Configuration verification failed."
                    exit_code=1
                fi
                ;;
        esac
    fi
    
    # Clean up temporary files
    cleanup_temp_files "${TEMP_DIR}"
    
    # Send notification about restoration status
    if [[ "${exit_code}" -eq 0 ]]; then
        status="SUCCESS"
        log_message "Restoration completed successfully"
    else
        status="FAILURE"
        log_message "Restoration failed with errors"
    fi
    
    send_notification "${status}" "${ENVIRONMENT}" "Restore type: ${RESTORE_TYPE}, Backup: ${BACKUP_FILE}"
    
    return "${exit_code}"
}

# Execute main function
main "$@"
exit $?