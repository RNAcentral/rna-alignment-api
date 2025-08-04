#!/bin/bash

set -euo pipefail

# Get project root and load .env file
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
ENV_FILE="$PROJECT_ROOT/.env"

if [ -f "$ENV_FILE" ]; then
    set -a
    source "$ENV_FILE"
    set +a
else
    echo "Error: .env file not found at $ENV_FILE"
    exit 1
fi

# Validate required environment variables
if [ -z "${S3_HOST:-}" ] || [ -z "${S3_KEY:-}" ] || [ -z "${S3_SECRET:-}" ] || \
   [ -z "${BUCKET_NAME:-}" ] || [ -z "${ENVIRONMENT:-}" ] || [ -z "${S3_BASE_PATH:-}" ]; then
    echo "Error: Missing required environment variables in .env file."
    exit 1
fi

# Configuration
SVN_URL="https://svn.rfam.org/svn/data_repos/trunk/Families/"
TEMP_DIR="/tmp/svn_transfer_$$"

mkdir -p "$TEMP_DIR"
trap "rm -rf $TEMP_DIR" EXIT

# Get all directories from SVN
echo "Fetching directory list from SVN..."
svn_dirs=$(svn list "$SVN_URL" | grep '/$' | sed 's/\/$//')

if [ -z "$svn_dirs" ]; then
    echo "No directories found in SVN repository"
    exit 1
fi

dir_count=$(echo "$svn_dirs" | wc -l)
echo "Found $dir_count directories to process"

function s3Upload() {
    local file_path=$1
    local s3_key=$2
    
    local date=$(date -R -u)
    local content_type="application/octet-stream"
    local string_to_sign="PUT\n\n$content_type\n${date}\n/${BUCKET_NAME}/${s3_key}"
    local signature=$(echo -en "${string_to_sign}" | openssl sha1 -hmac "${S3_SECRET}" -binary | base64)
    
    local curl_response=$(curl -X PUT -T "${file_path}" \
         -H "Host: uk1s3.embassy.ebi.ac.uk" \
         -H "Date: $date" \
         -H "Content-Type: $content_type" \
         -H "Authorization: AWS ${S3_KEY}:${signature}" \
         "${S3_HOST}/${BUCKET_NAME}/${s3_key}" \
         -w "%{http_code}" -s -o /dev/null)
    
    [ "$curl_response" = "200" ] || [ "$curl_response" = "201" ]
}

function processDirectory() {
    local dir_name=$1
    local svn_dir_url="${SVN_URL}${dir_name}"
    local local_dir="$TEMP_DIR/$dir_name"
    
    svn info "$svn_dir_url" >/dev/null 2>&1 || return 0
    svn export "$svn_dir_url" "$local_dir" >/dev/null 2>&1 || return 1
    
    local seed_file="$local_dir/SEED"
    if [ -f "$seed_file" ]; then
        local s3_key="${ENVIRONMENT}/${S3_BASE_PATH}/${dir_name}/SEED"
        if s3Upload "$seed_file" "$s3_key"; then
            echo "Successfully uploaded: ${dir_name}/SEED"
        fi
    fi
    
    rm -rf "$local_dir"
}

# Process each directory
echo "$svn_dirs" | while read -r dir_name; do
    if [ -n "$dir_name" ]; then
        processDirectory "$dir_name"
    fi
done