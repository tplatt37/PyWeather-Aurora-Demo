#!/bin/bash

# This will create a template event for API Gateway
sam local generate-event apigateway aws-proxy --method GET > events/event.json

# You need to manually modify the queryStringParameters section as follows:
# "queryStringParameters": {
#    "city": "Scranton"
#  },
#
#
# Then, you can test local with:
# 
# sam local invoke PyWeatherSAM -e events/event.json

