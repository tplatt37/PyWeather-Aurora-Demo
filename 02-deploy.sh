#!/bin/bash
# Must pass in the Name of an S3 bucket (private)
# Must pass in the ARN of the Secret holding the OpenWeather Map API Key
if [ -z $1 ]; then
        echo "Need the S3 Bucket Name as first parameter. Exiting..."
        exit 0
elif [ -z $2 ]; then
        echo "Need the ARN of the Secret with the API key as second paramter. Exiting..."
fi
        
sam deploy --stack-name PyWeather-Demo --template-file package.yaml \
--s3-bucket $1 --capabilities CAPABILITY_IAM \
--parameter-overrides SecretArn=$2
