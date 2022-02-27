#!/bin/bash

#REGION="us-west-2"
#SUBNETS=subnet-094e4b6294da6fec6,subnet-05d9f721231db14c3
#VPCID=vpc-0552daf3bdaf74f9d

#REGION="us-east-1"
#SUBNETS=subnet-0d71b9e02201d9fda,subnet-0e87b252e9cd61d4a
#VPCID=vpc-0ddaf8d68784c47ad

REGION="us-east-2"
SUBNETS=subnet-021d91d2ceedf5245,subnet-0953302f9523870f2
VPCID=vpc-0b01ea3196ae886be

echo "Region:$REGION..."

BUCKET=builds-platt-$REGION

sam build -t aurora.yaml
sam package --s3-bucket $BUCKET --output-template-file package.yaml --region $REGION

sam deploy --stack-name aurora-app9 \
--s3-bucket $BUCKET --capabilities CAPABILITY_IAM \
--parameter-overrides VpcId=$VPCID Subnets=$SUBNETS \
--region $REGION