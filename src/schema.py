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
    
    print("Context...")
    print(context)
    
    try:
        if event['RequestType'] == 'Create':
            createSchema()
            send_response(event, context, "SUCCESS",
                          {"Message": "Resource creation successful."})
        elif event['RequestType'] == 'Update':
            send_response(event, context, "SUCCESS",
                          {"Message": "Resource update successful."})
        elif event['RequestType'] == 'Delete':
            send_response(event, context, "SUCCESS",
                          {"Message": "Resource deletion successful."})
        else:
            send_response(event, context, "FAILED",
                          {"Message": "Unexpected event ("+ event +") received from CloudFormation"})
    except: 
        send_response(event, context, "FAILED", {
            "Message": "Exception during processing"})

    
def createSchema():
    
    rds_host = os.environ["RDS_ENDPOINT"]
    name= "admin"
    password = "Password123"
    
    # Need to check for:
    # 
    # Unexpected error: Could not connect to MySQL instance.
    #[ERROR]	2021-05-06T10:06:12.451Z	3bf6616c-1a25-4f55-8047-09cb748b4ddf	(1045, "Access denied for user 'admin'@'172.31.70.62' (using password: YES)")
    try:
        print("Connecting to " + rds_host + "...")
        conn = pymysql.connect(host=rds_host, user=name, passwd=password, connect_timeout=60)
    except pymysql.MySQLError as e:
        print("ERROR: Unexpected error: Could not connect to MySQL instance.")
        sys.exit()
    
    with conn.cursor() as cur:
       
        dml = "create database if not exists weather;"
        cur.execute(dml)
   
        dml = "use weather;"
        cur.execute(dml)
   
        dml = "CREATE TABLE IF NOTE EXISTS WeatherHistory (id INT(8) UNSIGNED AUTO_INCREMENT PRIMARY KEY, city VARCHAR(64) NOT NULL, temp DECIMAL(5,2) NOT NULL,at_time DATETIME);"
        cur.execute(dml)
       
    conn.commit()

def send_response(event, context, response_status, response_data):
    
    
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

    print("response_body...")
    print(response_body)
    
    print("headers_dict...")
    headers_dict = {"content-type" : "", "content-length" : str(len(response_body)) }
    print(headers_dict)
    
    print("About to PUT... to :" +event['ResponseURL'])
    response = requests.put( event['ResponseURL'], data=response_body.encode('utf-8'), headers=headers_dict)

    print("Response...")
    print(response)

    # Have to perform a PUT back to S3 pre-signed URL
    #opener = build_opener(HTTPHandler)
    #request = Request(event['ResponseURL'], data=response_body)
    #request.add_header('Content-Type', '')
    #request.add_header('Content-Length', len(response_body))
    #request.get_method = lambda: 'PUT'
    #response = opener.open(request)
 
 
 