#!/bin/bash

BUCKET=builds-platt-us-east-1

sam build -t aurora.yaml
sam package --s3-bucket $BUCKET --output-template-file package.yaml

sam deploy --stack-name aurora-app \
--s3-bucket $BUCKET --capabilities CAPABILITY_IAM \
--parameter-overrides VpcId=vpc-0ddaf8d68784c47ad Subnets=subnet-0d71b9e02201d9fda,subnet-0e87b252e9cd61d4a