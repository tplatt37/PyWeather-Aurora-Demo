# Overview

This is a version of PyWeather that uses a Relational Database (Aurora Serverless - MySQL) and Secrets Manager

Use this to demonstrate:
* A Lambda function connect to a VPC (to access the Aurora DB)
* Use of Aurora Serverless V1 database.  The database will "pause" or scale down to 0 ACUs after 1,000 seconds.  It will spin back up on demand.
* Use of a CloudFormation Custom Resource to execute a Lambda to load the simple schema into the database.
* Use of SecretsManager both for the secure creation of database administrator credentials, but also for automatic rotation

This demo includes SAM templates to create all of the resources described above.

# Installation

First, you must request an API Key from OpenWeatherMap.org, for the "Current Weather Data" API.

If you've already setup your API Key from the PyWeather-Demo or JsWeather-Demo , you are already set!

## Register on OpenWeather Map.org

https://openweathermap.org/api

Request an API key.  

## Create a Secret in Secrets Manager

We'll store the OpenWeatherMap API key in Secrets manager.

First, you'll need to create the Secret (replace YOUR_API_KEY_HERE with yours!)

aws secretsmanager create-secret --name "openweather-api-key" --secret-string '{"apikey":"YOUR_API_KEY_HERE"}'

SECRETARN=$(aws secretsmanager describe-secret --secret-id openweather-api-key | jq -r '.ARN')

echo $SECRETARN

## Specify an S3 bucket to use for the sam build command

We just need any S3 bucket where any the code can be packaged via sam package command.

Replace YOUR_BUCKET_NAME with the name of a bucket in the same region as where you wish to deploy.

BUCKETNAME=YOUR_BUCKET_NAME

echo $BUCKETNAME

## Specify two PRIVATE Subnets

The Aurora Serverless V1 database cluster must reside in a Private subnet.
This Lambda must be connected to the VPC where the Aurora database will reside.
The private subnets must have a NAT GW (or s3 vpc endpoint) so the Lambda code can interact with an s3 pre-signed URL.

You private subnets should be in a simple comma delimited list.

SUBNETS=subnet-a103939399,subnet-b293829292

echo $SUBNETS

## Install via SAM

./install.sh $BUCKETNAME $SUBNETS $SECRETARN

You should see any error messages on the output, or in the CloudFormation stack.

The install is set up in two phases.

The first SAM template creates the Lambda for the CustomResource used to load a simple database schema into the Aurora cluster.

The second SAM template creates:
* An admin user/password (dynamically generated) in SecretsManager
* The Aurora Serverless V1 RDS Cluster (in the private subnets)
* The PyWeatherAurora Lambda function, connected to the VPC/Subnets
* The CustomResource created previously is used to load a DB schema
* A secret rotation is setup to run every 30 days and rotate the password.

NOTE: The PyWeather code is robust in that if the password is rotated, it will recognize this ("access denied" message) and retrieve the rotated password.


## Then what?

Run the Lambda!  

The recommended way (assuming you are doing a demo to a class) is to simply run it via the Lambda console.
(But there is also an API Gateway endpoint)

Go to the Lambda Console

Create a test Event with this content:

{"queryStringParameters":{"city":"Orlando"}}

Run the function a few times. 

Then , go to Secrets Manager and find the DB Secret. 

Rotate it 

Run the Lambda again - and note that the output will show "access denied" but the code will recognize this an pull the updated password.

You can also go the "Query Editor" in the RDS console and retrieve the data from the table.

## Uninstall

Simply delete both Cloudformation stacks or run:

./99-uninstall.sh

Then, manually delete the SecretsManager secret.

## Requirements

You need SAM CLI installed 

You need Python3.8 installed
