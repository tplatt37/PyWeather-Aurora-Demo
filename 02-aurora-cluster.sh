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

REGION=${AWS_DEFAULT_REGION:-$(aws configure get default.region)}
echo "Creating in $REGION..."

# Sometimes we need a comma delimited list of subnets, other times, space delimited. 
# use $1 for the comma delimited, and SUBNETS for the space delimited.
# Subnets are needed for the ALB.
SUBNETS_NOCOMMA=$(echo $SUBNETS | sed 's/,/ /g')
echo "Subnets=$SUBNETS_NOCOMMA"

# Grab the VpcId off the first subnet. This is needed for the Security Group and Target Group.
VPC_ID=$(aws ec2 describe-subnets --subnet-ids $SUBNETS_NOCOMMA --query 'Subnets[0].VpcId' --output text)
echo "VpcId=$VPC_ID"

sam build -t aurora.yaml
sam package --s3-bucket $BUCKET --output-template-file package.yaml --region $REGION

sam deploy --stack-name pyweather-aurora-cluster \
--s3-bucket $BUCKET --capabilities CAPABILITY_IAM \
--parameter-overrides VpcId=$VPC_ID Subnets=$SUBNETS APIKeySecretArn=arn:aws:secretsmanager:us-east-2:753157545766:secret:open-weather-api-fivOn5 \
--capabilities CAPABILITY_AUTO_EXPAND CAPABILITY_IAM \
--region $REGION
