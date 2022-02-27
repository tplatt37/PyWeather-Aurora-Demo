import sys
import os
import boto3
import json
import pymysql
import logging
import requests

def handler(event, context):
    
    print("Event...")
    print(event)
    
    try:
        if event['RequestType'] == 'Create':
            createSchema(event)
            send_response(event, context, "SUCCESS",
                          {"Message": "Resource creation successful."})
        elif event['RequestType'] == 'Update':
            # nothing to do on update, so just indicate SUCCESS
            send_response(event, context, "SUCCESS",
                          {"Message": "Resource update successful."})
        elif event['RequestType'] == 'Delete':
            # nothing to do on Delete.
            send_response(event, context, "SUCCESS",
                          {"Message": "Resource deletion successful."})
        else:
            send_response(event, context, "FAILED",
                          {"Message": "Unexpected event ("+ event +") received from CloudFormation"})
    except: 
        send_response(event, context, "FAILED", {
            "Message": "Exception during processing"})

    
def createSchema(event):
    
    rds_host = event["ResourceProperties"]["RDSEndpoint"]
    name= "admin"
    password = "Password123"
    
    try:
        print("Connecting to " + rds_host + "...")
        conn = pymysql.connect(host=rds_host, user=name, passwd=password, connect_timeout=60)
    except pymysql.MySQLError as e:
        print("ERROR: Unexpected error: Could not connect to MySQL instance.")
        sys.exit()
    
    with conn.cursor() as cur:
       
        dml = "CREATE DATABASE IF NOT EXISTS weather;"
        cur.execute(dml)
   
        dml = "USE weather;"
        cur.execute(dml)
   
        dml = "CREATE TABLE IF NOT EXISTS WeatherHistory (id INT(8) UNSIGNED AUTO_INCREMENT PRIMARY KEY, city VARCHAR(64) NOT NULL, temp DECIMAL(5,2) NOT NULL,at_time DATETIME);"
        cur.execute(dml)
       
    conn.commit()
    
    print("Schema created.")

def send_response(event, context, response_status, response_data):
    
    # We send status back to CloudFormation by perfoming a PUT to a S3 pre-signed URL.
    # This is why the Lambda must be connected to a Private subnet with NATGW it has to be able to talk to S3.
    print("ResponseURL=" + event['ResponseURL'])
    
    # Respond back to CloudFormation
    response_body = json.dumps({
        "Status": response_status,
        "Reason": "CloudWatch Log Stream: " + context.log_stream_name,
        "PhysicalResourceId": context.log_stream_name,
        "StackId": event['StackId'],
        "RequestId": event['RequestId'],
        "LogicalResourceId": event['LogicalResourceId'],
        "Data": response_data
    })

    # Content-Type should be null string.
    headers_dict = {"content-type" : "", "content-length" : str(len(response_body)) }

    response = requests.put( event['ResponseURL'], data=response_body.encode('utf-8'), headers=headers_dict)

    print("Response...")
    print(response)


 