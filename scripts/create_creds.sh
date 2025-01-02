#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
CRED_PATH=$SCRIPT_DIR/../credentials.json

json_content='{
    "installed": {
        "client_id": "260824934414-evidd1af95f46hid2h6voba4508grsgq.apps.googleusercontent.com",
        "project_id": "becap-445610",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_secret": "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",
        "redirect_uris": [
            "http://localhost"
        ]
    }
}'

# File to write to
file_name="credentials.json"

# Check if the virtual environment exists
if [ ! -d "$CRED_PATH" ]; then
  echo "Credential not found. Creating one..."
  echo $json_content > $CRED_PATH
else
  echo "Credential already exists. Skipping creation."
fi
