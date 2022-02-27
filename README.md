# Overview

This simple Lambda function invokes OpenWeatherMap.org API to retrieve the current weather for a city.

# Installation

First, you must request an API Key from OpenWeatherMap.org, for the "Current Weather Data" API.

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

## Install via SAM

./01-build.sh $BUCKETNAME

./02-deploy.sh $BUCKETNAME $SECRETARN

You should see any error messages on the output, or in the CloudFormation stack.

This will create the basic Lambda function, which you can then execute in the console for demonstrations (or via API Gateway endpoint)

## Create a CodeCommit repo

The CI/CD Pipeline assumes you are using CodeCommit.

Follow these steps to create a repo

aws codecommit create-repository --repository-name "PyWeather-Demo"

Then, simply add that as a new remote , and push to it. 

## Install CI/CD Pipeline

This will create a CI/CD Pipeline that you can use for DevOps demos.

This CI/CD Pipeline will peacefully co-exist with manually deploying as described above.

The pipeline subfolder contains a CF template for a CodePipeline/CodeBuild/CloudFormation CI/CD pipeline.

./03-deploy-pipeline.sh 

NOTE: The pipeline assumes you are using AWS CodeCommit - NOT GITHUB!

## Uninstall

Simply delete both Cloudformation stacks.

Then, manually delete the SecretsManager secret.

## Requirements

You need SAM CLI installed 

You need Docker (for step-through debugging demos)

You need Python3.8 installed

You need jq installed
