#!/bin/bash

aws cloudformation deploy --template-file pipeline/pipeline.yaml --stack-name PyWeather-Demo-Pipeline --capabilities CAPABILITY_IAM