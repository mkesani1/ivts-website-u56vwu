#!/bin/bash
#
# backup.sh - Automated backup script for IndiVillage.com website
#
# This script creates backups of databases, S3 storage, and configuration files
# for the IndiVillage.com website. Backups are compressed, optionally encrypted,
# and uploaded to AWS S3 for long-term storage.
#
# Dependencies:
# - aws-cli (latest version)
# - postgresql-client (latest version)
#

set -e

# Global variables
SCRIPT_DIR=$(dirname "${BASH_SOURCE[0]}")
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
LOG_FILE="/var/log/indivillage/backup_${TIMESTAMP}.log"
BACKUP_RETENTION_DAYS=30

# Default values
DEFAULT_BACKUP_DIR="/var/backups/indivillage"
DEFAULT_BACKUP_TYPE="full"
DEFAULT_ENVIRONMENT=""
ENCRYPT_BACKUP=true
UPLOAD_TO_S3=true
CLEAN_OLD_BACKUPS=true

# Function to log messages
log_message() {
    local message="$1"
    local timestamp=$(date +"%Y-%m-%d %H:%M:%S")
    echo "[${timestamp}] ${message}"
    
    # Make sure log directory exists
    mkdir -p "$(dirname "${LOG_FILE}")"
    echo "[${timestamp}] ${message}" >> "${LOG_FILE}"
}

# Function to check dependencies
check_dependencies() {
    log_message "Checking dependencies..."
    
    # Check for aws command
    if ! command -v aws &> /dev/null; then
        log_message "ERROR: aws command not found. Please install AWS CLI."
        return 1
    fi
    
    # Check for pg_dump command
    if ! command -v pg_dump &> /dev/null; then
        log_message "ERROR: pg_dump command not found. Please install postgresql-client."
        return 1
    fi
    
    # Check for openssl command
    if ! command -v openssl &> /dev/null; then
        log_message "ERROR: openssl command not found. Please install openssl."
        return 1
    fi
    
    # Check for required environment variables
    if [[ -z "${AWS_ACCESS_KEY_ID}" || -z "${AWS_SECRET_ACCESS_KEY}" ]]; then
        log_message "WARNING: AWS credentials not found in environment variables."
        log_message "Attempting to use AWS credential file or IAM role..."
    fi
    
    log_message "All dependencies available."
    return 0
}

# Function to create backup directory
create_backup_directory() {
    local backup_dir="$1"
    
    if [[ ! -d "${backup_dir}" ]]; then
        log_message "Creating backup directory: ${backup_dir}"
        mkdir -p "${backup_dir}"
    else
        log_message "Using existing backup directory: ${backup_dir}"
    fi
    
    # Check if directory is writable
    if [[ ! -w "${backup_dir}" ]]; then
        log_message "ERROR: Backup directory ${backup_dir} is not writable."
        return 1
    fi
    
    echo "${backup_dir}"
}

# Function to get database connection parameters
get_db_connection_params() {
    local environment="$1"
    local config_file="${SCRIPT_DIR}/../config/database_${environment}.conf"
    
    # Check if config file exists
    if [[ ! -f "${config_file}" ]]; then
        log_message "ERROR: Database configuration file not found: ${config_file}"
        return 1
    fi
    
    # Source the config file to get DB params
    source "${config_file}"
    
    # Return connection parameters as an array
    echo "${DB_HOST} ${DB_PORT} ${DB_NAME} ${DB_USER} ${DB_PASSWORD}"
}

# Function to backup database
backup_database() {
    local environment="$1"
    local output_dir="$2"
    local format="${3:-custom}"  # Default to custom format
    
    log_message "Starting database backup for ${environment} environment..."
    
    # Get database connection parameters
    read -r DB_HOST DB_PORT DB_NAME DB_USER DB_PASSWORD <<< "$(get_db_connection_params "${environment}")"
    
    if [[ -z "${DB_HOST}" || -z "${DB_NAME}" || -z "${DB_USER}" ]]; then
        log_message "ERROR: Failed to get database connection parameters."
        return 1
    fi
    
    # Create backup filename
    local backup_file="${output_dir}/database_${environment}_${TIMESTAMP}"
    
    if [[ "${format}" == "custom" ]]; then
        backup_file="${backup_file}.dump"
        format_option="-Fc"
    elif [[ "${format}" == "plain" ]]; then
        backup_file="${backup_file}.sql"
        format_option="-Fp"
    else
        log_message "ERROR: Unsupported backup format: ${format}"
        return 1
    fi
    
    # Temporarily set PGPASSWORD environment variable
    export PGPASSWORD="${DB_PASSWORD}"
    
    # Execute pg_dump
    if pg_dump -h "${DB_HOST}" -p "${DB_PORT}" -U "${DB_USER}" -d "${DB_NAME}" ${format_option} -f "${backup_file}"; then
        log_message "Database backup completed successfully: ${backup_file}"
        # Unset password
        unset PGPASSWORD
        echo "${backup_file}"
        return 0
    else
        log_message "ERROR: Database backup failed."
        unset PGPASSWORD
        return 1
    fi
}

# Function to backup S3 files
backup_s3_files() {
    local environment="$1"
    local output_dir="$2"
    
    log_message "Starting S3 files backup for ${environment} environment..."
    
    # Determine S3 bucket names based on environment
    local s3_config_file="${SCRIPT_DIR}/../config/s3_${environment}.conf"
    
    if [[ ! -f "${s3_config_file}" ]]; then
        log_message "ERROR: S3 configuration file not found: ${s3_config_file}"
        return 1
    fi
    
    # Source the config file to get S3 bucket names
    source "${s3_config_file}"
    
    if [[ -z "${S3_BUCKETS}" ]]; then
        log_message "ERROR: No S3 buckets defined in configuration."
        return 1
    fi
    
    # Create backup filename
    local backup_file="${output_dir}/s3_files_${environment}_${TIMESTAMP}.tar"
    
    # Create temporary directory for S3 files
    local temp_dir=$(mktemp -d)
    
    # Download files from each S3 bucket
    local bucket_count=0
    local success=true
    
    for bucket in ${S3_BUCKETS}; do
        log_message "Downloading files from bucket: ${bucket}"
        local bucket_dir="${temp_dir}/${bucket}"
        
        mkdir -p "${bucket_dir}"
        
        if aws s3 sync "s3://${bucket}" "${bucket_dir}" --quiet; then
            log_message "Successfully downloaded files from bucket: ${bucket}"
            ((bucket_count++))
        else
            log_message "ERROR: Failed to download files from bucket: ${bucket}"
            success=false
        fi
    done
    
    if [[ "${success}" == "true" && ${bucket_count} -gt 0 ]]; then
        # Create tar archive
        if tar -cf "${backup_file}" -C "${temp_dir}" .; then
            log_message "S3 files backup completed successfully: ${backup_file}"
            rm -rf "${temp_dir}"
            echo "${backup_file}"
            return 0
        else
            log_message "ERROR: Failed to create tar archive for S3 files."
            rm -rf "${temp_dir}"
            return 1
        fi
    else
        log_message "ERROR: S3 files backup failed."
        rm -rf "${temp_dir}"
        return 1
    fi
}

# Function to backup configuration files
backup_config() {
    local environment="$1"
    local output_dir="$2"
    
    log_message "Starting configuration backup for ${environment} environment..."
    
    # Determine configuration directories based on environment
    local config_dirs="${SCRIPT_DIR}/../config"
    
    # Additional environment-specific directories
    if [[ -d "${SCRIPT_DIR}/../config/${environment}" ]]; then
        config_dirs="${config_dirs} ${SCRIPT_DIR}/../config/${environment}"
    fi
    
    # Create backup filename
    local backup_file="${output_dir}/config_${environment}_${TIMESTAMP}.tar"
    
    # Create tar archive
    if tar -cf "${backup_file}" ${config_dirs}; then
        log_message "Configuration backup completed successfully: ${backup_file}"
        echo "${backup_file}"
        return 0
    else
        log_message "ERROR: Configuration backup failed."
        return 1
    fi
}

# Function to compress a backup file
compress_backup() {
    local file_path="$1"
    
    log_message "Compressing backup file: ${file_path}"
    
    if gzip -f "${file_path}"; then
        local compressed_file="${file_path}.gz"
        log_message "Compression completed successfully: ${compressed_file}"
        echo "${compressed_file}"
        return 0
    else
        log_message "ERROR: Compression failed for file: ${file_path}"
        return 1
    fi
}

# Function to encrypt a backup file
encrypt_backup() {
    local file_path="$1"
    local encryption_key="$2"
    
    log_message "Encrypting backup file: ${file_path}"
    
    if [[ -z "${encryption_key}" ]]; then
        log_message "ERROR: Encryption key not provided."
        return 1
    fi
    
    local encrypted_file="${file_path}.enc"
    
    if openssl enc -aes-256-cbc -salt -in "${file_path}" -out "${encrypted_file}" -pass "pass:${encryption_key}"; then
        log_message "Encryption completed successfully: ${encrypted_file}"
        # Remove the unencrypted file
        rm -f "${file_path}"
        echo "${encrypted_file}"
        return 0
    else
        log_message "ERROR: Encryption failed for file: ${file_path}"
        return 1
    fi
}

# Function to upload backup to S3
upload_to_s3() {
    local file_path="$1"
    local environment="$2"
    local backup_type="$3"
    
    log_message "Uploading backup to S3: ${file_path}"
    
    # Determine S3 backup bucket based on environment
    local s3_config_file="${SCRIPT_DIR}/../config/s3_${environment}.conf"
    
    if [[ ! -f "${s3_config_file}" ]]; then
        log_message "ERROR: S3 configuration file not found: ${s3_config_file}"
        return 1
    fi
    
    # Source the config file to get S3 bucket names
    source "${s3_config_file}"
    
    if [[ -z "${S3_BACKUP_BUCKET}" ]]; then
        log_message "ERROR: S3 backup bucket not defined in configuration."
        return 1
    fi
    
    # Get filename from path
    local filename=$(basename "${file_path}")
    
    # Create S3 key with appropriate prefix
    local s3_key="${backup_type}/${filename}"
    
    # Upload to S3
    if aws s3 cp "${file_path}" "s3://${S3_BACKUP_BUCKET}/${s3_key}"; then
        log_message "Successfully uploaded to S3: s3://${S3_BACKUP_BUCKET}/${s3_key}"
        return 0
    else
        log_message "ERROR: Failed to upload to S3: ${file_path}"
        return 1
    fi
}

# Function to clean up old backup files
cleanup_old_backups() {
    local backup_dir="$1"
    local retention_days="$2"
    
    log_message "Cleaning up backup files older than ${retention_days} days..."
    
    # Find files older than retention_days and delete them
    local files_to_delete=$(find "${backup_dir}" -type f -name "*.gz" -o -name "*.enc" -mtime +${retention_days})
    local count=0
    
    for file in ${files_to_delete}; do
        if rm -f "${file}"; then
            log_message "Deleted old backup file: ${file}"
            ((count++))
        else
            log_message "ERROR: Failed to delete file: ${file}"
        fi
    done
    
    log_message "Cleanup completed. Deleted ${count} old backup files."
    return ${count}
}

# Function to clean up old S3 backup objects
cleanup_s3_backups() {
    local environment="$1"
    local backup_type="$2"
    local retention_days="$3"
    
    log_message "Cleaning up S3 backup objects older than ${retention_days} days..."
    
    # Determine S3 backup bucket based on environment
    local s3_config_file="${SCRIPT_DIR}/../config/s3_${environment}.conf"
    
    if [[ ! -f "${s3_config_file}" ]]; then
        log_message "ERROR: S3 configuration file not found: ${s3_config_file}"
        return 1
    fi
    
    # Source the config file to get S3 bucket names
    source "${s3_config_file}"
    
    if [[ -z "${S3_BACKUP_BUCKET}" ]]; then
        log_message "ERROR: S3 backup bucket not defined in configuration."
        return 1
    fi
    
    # Calculate cutoff date in seconds since epoch
    local cutoff_date=$(date -d "${retention_days} days ago" +%s)
    
    # List objects in the bucket with the specified prefix
    local objects=$(aws s3api list-objects --bucket "${S3_BACKUP_BUCKET}" --prefix "${backup_type}/" --query "Contents[?LastModified]" --output json)
    
    if [[ -z "${objects}" || "${objects}" == "null" ]]; then
        log_message "No objects found in S3 bucket: s3://${S3_BACKUP_BUCKET}/${backup_type}/"
        return 0
    fi
    
    # Process each object
    local count=0
    
    while read -r obj; do
        local key=$(echo "${obj}" | jq -r '.Key')
        local last_modified=$(echo "${obj}" | jq -r '.LastModified')
        local obj_date=$(date -d "${last_modified}" +%s)
        
        if [[ ${obj_date} -lt ${cutoff_date} ]]; then
            if aws s3 rm "s3://${S3_BACKUP_BUCKET}/${key}"; then
                log_message "Deleted old S3 backup object: s3://${S3_BACKUP_BUCKET}/${key}"
                ((count++))
            else
                log_message "ERROR: Failed to delete S3 object: s3://${S3_BACKUP_BUCKET}/${key}"
            fi
        fi
    done < <(echo "${objects}" | jq -c '.[]')
    
    log_message "S3 cleanup completed. Deleted ${count} old backup objects."
    return ${count}
}

# Function to send notification about backup status
send_notification() {
    local status="$1"
    local environment="$2"
    local details="$3"
    
    log_message "Sending backup notification: ${status}"
    
    # Determine notification method based on environment
    local notification_config="${SCRIPT_DIR}/../config/notification_${environment}.conf"
    
    if [[ ! -f "${notification_config}" ]]; then
        log_message "WARNING: Notification configuration file not found: ${notification_config}"
        return 1
    fi
    
    # Source the config file to get notification settings
    source "${notification_config}"
    
    if [[ -z "${NOTIFICATION_METHOD}" ]]; then
        log_message "ERROR: Notification method not defined in configuration."
        return 1
    fi
    
    # Format notification message
    local subject="Backup ${status} - ${environment} environment"
    local message="Backup status: ${status}\nEnvironment: ${environment}\nTimestamp: $(date)\n\nDetails:\n${details}"
    
    # Send notification based on method
    case "${NOTIFICATION_METHOD}" in
        email)
            if [[ -z "${NOTIFICATION_EMAIL}" ]]; then
                log_message "ERROR: Notification email not defined in configuration."
                return 1
            fi
            
            echo -e "${message}" | mail -s "${subject}" "${NOTIFICATION_EMAIL}"
            ;;
        sns)
            if [[ -z "${NOTIFICATION_SNS_TOPIC}" ]]; then
                log_message "ERROR: Notification SNS topic not defined in configuration."
                return 1
            fi
            
            aws sns publish --topic-arn "${NOTIFICATION_SNS_TOPIC}" --subject "${subject}" --message "${message}"
            ;;
        *)
            log_message "ERROR: Unsupported notification method: ${NOTIFICATION_METHOD}"
            return 1
            ;;
    esac
    
    log_message "Notification sent successfully."
    return 0
}

# Function to verify backup integrity
verify_backup() {
    local file_path="$1"
    local backup_type="$2"
    
    log_message "Verifying backup integrity: ${file_path}"
    
    # Check if file exists and is readable
    if [[ ! -f "${file_path}" || ! -r "${file_path}" ]]; then
        log_message "ERROR: Backup file not found or not readable: ${file_path}"
        return 1
    fi
    
    # Verify based on backup type and file extension
    if [[ "${file_path}" == *.gz ]]; then
        # Verify gzip integrity
        if gzip -t "${file_path}"; then
            log_message "Gzip integrity check passed: ${file_path}"
        else
            log_message "ERROR: Gzip integrity check failed: ${file_path}"
            return 1
        fi
        
        # For database backups, additional verification
        if [[ "${backup_type}" == "database" && "${file_path}" == *.dump.gz ]]; then
            # Create temporary file
            local temp_file=$(mktemp)
            
            # Extract to temporary file
            if gzip -dc "${file_path}" > "${temp_file}"; then
                # Test with pg_restore
                if pg_restore --list "${temp_file}" > /dev/null; then
                    log_message "Database backup verification passed: ${file_path}"
                    rm -f "${temp_file}"
                else
                    log_message "ERROR: Database backup verification failed: ${file_path}"
                    rm -f "${temp_file}"
                    return 1
                fi
            else
                log_message "ERROR: Failed to extract backup for verification: ${file_path}"
                rm -f "${temp_file}"
                return 1
            fi
        elif [[ "${backup_type}" == "s3_files" && "${file_path}" == *.tar.gz ]]; then
            # Create temporary file
            local temp_file=$(mktemp)
            
            # Extract to temporary file
            if gzip -dc "${file_path}" > "${temp_file}"; then
                # Test tar archive
                if tar -tf "${temp_file}" > /dev/null; then
                    log_message "S3 files backup verification passed: ${file_path}"
                    rm -f "${temp_file}"
                else
                    log_message "ERROR: S3 files backup verification failed: ${file_path}"
                    rm -f "${temp_file}"
                    return 1
                fi
            else
                log_message "ERROR: Failed to extract backup for verification: ${file_path}"
                rm -f "${temp_file}"
                return 1
            fi
        elif [[ "${backup_type}" == "config" && "${file_path}" == *.tar.gz ]]; then
            # Create temporary file
            local temp_file=$(mktemp)
            
            # Extract to temporary file
            if gzip -dc "${file_path}" > "${temp_file}"; then
                # Test tar archive
                if tar -tf "${temp_file}" > /dev/null; then
                    log_message "Configuration backup verification passed: ${file_path}"
                    rm -f "${temp_file}"
                else
                    log_message "ERROR: Configuration backup verification failed: ${file_path}"
                    rm -f "${temp_file}"
                    return 1
                fi
            else
                log_message "ERROR: Failed to extract backup for verification: ${file_path}"
                rm -f "${temp_file}"
                return 1
            fi
        fi
    elif [[ "${file_path}" == *.enc ]]; then
        # For encrypted files, we can only check if the file exists
        log_message "Encrypted backup file exists: ${file_path}"
        # Note: Full verification would require decryption key and is not performed here
    else
        log_message "WARNING: Unknown backup format, skipping verification: ${file_path}"
    fi
    
    return 0
}

# Function to display usage information
display_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo
    echo "Options:"
    echo "  -e, --environment ENV   Specify the environment (development, staging, production)"
    echo "  -t, --type TYPE         Specify backup type (full, db-only, files-only, config-only)"
    echo "                          Default: full"
    echo "  -d, --directory DIR     Specify the backup directory"
    echo "                          Default: /var/backups/indivillage"
    echo "  -r, --retention DAYS    Specify the backup retention period in days"
    echo "                          Default: 30"
    echo "  --no-encrypt            Disable backup encryption"
    echo "  --no-upload             Disable S3 upload"
    echo "  --no-cleanup            Disable cleanup of old backups"
    echo "  -h, --help              Display this help message"
    echo
    echo "Environment variables:"
    echo "  ENCRYPTION_KEY          Key used for backup encryption"
    echo "  AWS_ACCESS_KEY_ID       AWS access key ID for S3 operations"
    echo "  AWS_SECRET_ACCESS_KEY   AWS secret access key for S3 operations"
}

# Main function
main() {
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case "$1" in
            -e|--environment)
                shift
                ENVIRONMENT="$1"
                ;;
            -t|--type)
                shift
                BACKUP_TYPE="$1"
                ;;
            -d|--directory)
                shift
                BACKUP_DIR="$1"
                ;;
            -r|--retention)
                shift
                BACKUP_RETENTION_DAYS="$1"
                ;;
            --no-encrypt)
                ENCRYPT_BACKUP=false
                ;;
            --no-upload)
                UPLOAD_TO_S3=false
                ;;
            --no-cleanup)
                CLEAN_OLD_BACKUPS=false
                ;;
            -h|--help)
                display_usage
                exit 0
                ;;
            *)
                echo "Unknown option: $1" >&2
                display_usage
                exit 1
                ;;
        esac
        shift
    done
    
    # Validate required parameters
    if [[ -z "${ENVIRONMENT}" ]]; then
        echo "ERROR: Environment not specified." >&2
        display_usage
        exit 1
    fi
    
    # Set default backup type if not specified
    if [[ -z "${BACKUP_TYPE}" ]]; then
        BACKUP_TYPE="${DEFAULT_BACKUP_TYPE}"
    fi
    
    # Set default backup directory if not specified
    if [[ -z "${BACKUP_DIR}" ]]; then
        BACKUP_DIR="${DEFAULT_BACKUP_DIR}"
    fi
    
    # Validate backup type
    case "${BACKUP_TYPE}" in
        full|db-only|files-only|config-only)
            # Valid backup type
            ;;
        *)
            echo "ERROR: Invalid backup type: ${BACKUP_TYPE}" >&2
            display_usage
            exit 1
            ;;
    esac
    
    # Setup logging
    mkdir -p "$(dirname "${LOG_FILE}")"
    
    log_message "Starting backup process for ${ENVIRONMENT} environment"
    log_message "Backup type: ${BACKUP_TYPE}"
    log_message "Backup directory: ${BACKUP_DIR}"
    log_message "Retention period: ${BACKUP_RETENTION_DAYS} days"
    
    # Check dependencies
    if ! check_dependencies; then
        log_message "ERROR: Dependency check failed. Aborting."
        exit 1
    fi
    
    # Create backup directory
    if ! create_backup_directory "${BACKUP_DIR}"; then
        log_message "ERROR: Failed to create backup directory. Aborting."
        exit 1
    fi
    
    # Initialize variables for backup status tracking
    backup_files=()
    backup_success=true
    error_details=""
    
    # Perform backups based on backup type
    if [[ "${BACKUP_TYPE}" == "full" || "${BACKUP_TYPE}" == "db-only" ]]; then
        # Database backup
        db_backup_file=$(backup_database "${ENVIRONMENT}" "${BACKUP_DIR}")
        
        if [[ -n "${db_backup_file}" && -f "${db_backup_file}" ]]; then
            backup_files+=("${db_backup_file}:database")
        else
            backup_success=false
            error_details="${error_details}Database backup failed.\n"
        fi
    fi
    
    if [[ "${BACKUP_TYPE}" == "full" || "${BACKUP_TYPE}" == "files-only" ]]; then
        # S3 files backup
        s3_backup_file=$(backup_s3_files "${ENVIRONMENT}" "${BACKUP_DIR}")
        
        if [[ -n "${s3_backup_file}" && -f "${s3_backup_file}" ]]; then
            backup_files+=("${s3_backup_file}:s3_files")
        else
            backup_success=false
            error_details="${error_details}S3 files backup failed.\n"
        fi
    fi
    
    if [[ "${BACKUP_TYPE}" == "full" || "${BACKUP_TYPE}" == "config-only" ]]; then
        # Configuration backup
        config_backup_file=$(backup_config "${ENVIRONMENT}" "${BACKUP_DIR}")
        
        if [[ -n "${config_backup_file}" && -f "${config_backup_file}" ]]; then
            backup_files+=("${config_backup_file}:config")
        else
            backup_success=false
            error_details="${error_details}Configuration backup failed.\n"
        fi
    fi
    
    # Compress, encrypt, verify, and upload backups
    for backup_info in "${backup_files[@]}"; do
        IFS=':' read -r backup_file backup_type <<< "${backup_info}"
        
        # Compress backup
        compressed_file=$(compress_backup "${backup_file}")
        
        if [[ -z "${compressed_file}" || ! -f "${compressed_file}" ]]; then
            backup_success=false
            error_details="${error_details}Failed to compress ${backup_file}.\n"
            continue
        fi
        
        current_file="${compressed_file}"
        
        # Encrypt backup if enabled
        if [[ "${ENCRYPT_BACKUP}" == "true" ]]; then
            if [[ -z "${ENCRYPTION_KEY}" ]]; then
                log_message "ERROR: Encryption enabled but no encryption key provided."
                log_message "Set the ENCRYPTION_KEY environment variable or disable encryption with --no-encrypt."
                backup_success=false
                error_details="${error_details}Encryption failed for ${current_file} (no key provided).\n"
                continue
            fi
            
            encrypted_file=$(encrypt_backup "${current_file}" "${ENCRYPTION_KEY}")
            
            if [[ -z "${encrypted_file}" || ! -f "${encrypted_file}" ]]; then
                backup_success=false
                error_details="${error_details}Failed to encrypt ${current_file}.\n"
                continue
            fi
            
            current_file="${encrypted_file}"
        fi
        
        # Verify backup
        if ! verify_backup "${current_file}" "${backup_type}"; then
            backup_success=false
            error_details="${error_details}Verification failed for ${current_file}.\n"
            continue
        fi
        
        # Upload to S3 if enabled
        if [[ "${UPLOAD_TO_S3}" == "true" ]]; then
            if ! upload_to_s3 "${current_file}" "${ENVIRONMENT}" "${backup_type}"; then
                backup_success=false
                error_details="${error_details}Failed to upload ${current_file} to S3.\n"
                continue
            fi
        fi
    done
    
    # Clean up old backups if enabled
    if [[ "${CLEAN_OLD_BACKUPS}" == "true" ]]; then
        # Clean up local backups
        cleanup_old_backups "${BACKUP_DIR}" "${BACKUP_RETENTION_DAYS}"
        
        # Clean up S3 backups if upload was enabled
        if [[ "${UPLOAD_TO_S3}" == "true" ]]; then
            if [[ "${BACKUP_TYPE}" == "full" || "${BACKUP_TYPE}" == "db-only" ]]; then
                cleanup_s3_backups "${ENVIRONMENT}" "database" "${BACKUP_RETENTION_DAYS}"
            fi
            
            if [[ "${BACKUP_TYPE}" == "full" || "${BACKUP_TYPE}" == "files-only" ]]; then
                cleanup_s3_backups "${ENVIRONMENT}" "s3_files" "${BACKUP_RETENTION_DAYS}"
            fi
            
            if [[ "${BACKUP_TYPE}" == "full" || "${BACKUP_TYPE}" == "config-only" ]]; then
                cleanup_s3_backups "${ENVIRONMENT}" "config" "${BACKUP_RETENTION_DAYS}"
            fi
        fi
    fi
    
    # Send notification
    if [[ "${backup_success}" == "true" ]]; then
        log_message "Backup process completed successfully."
        send_notification "SUCCESS" "${ENVIRONMENT}" "All backup operations completed successfully."
        exit 0
    else
        log_message "Backup process completed with errors."
        send_notification "FAILURE" "${ENVIRONMENT}" "${error_details}"
        exit 1
    fi
}

# Call main function with all arguments
main "$@"