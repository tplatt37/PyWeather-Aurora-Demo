#!/bin/bash
# Must pass in an s3 bucket (private) to use...
if [ -z $1 ]; then
        echo "Need the S3 Bucket Name as a parameter. Exiting..."
        exit 0
fi

sam build && sam package --s3-bucket $1 --output-template-file package.yaml
