#!/bin/bash

# Must pass in an s3 bucket (private) where the source code zip can be stored...
if [ -z $1 ]; then
        echo "Need the S3 Bucket Name as a parameter. Exiting..."
        exit 0
fi
BUCKET=$1

if [ -z $2 ]; then
        echo "Need a comma delimited list of two PRIVATE subnet Ids. Exiting..."
        exit 0
fi
SUBNETS=$2

if [ -z $3 ]; then
        echo "Need the ARN of the Secret holding the OpenWeather API Key. Exiting..."
        exit 0
fi
SECRET_ARN=$3

REGION=${AWS_DEFAULT_REGION:-$(aws configure get default.region)}
echo "Creating in $REGION..."

echo "Setting up Custom Resource Lambda first..."
./01-custom-resource-lambda.sh $BUCKET $SUBNETS

echo "Setting up Aurora cluster..."
./02-aurora-cluster.sh $BUCKET $SUBNETS $SECRET_ARN

