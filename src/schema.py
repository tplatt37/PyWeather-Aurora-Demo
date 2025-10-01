import sys
import os
import boto3
import json
import pymysql
import logging
import requests
from botocore.exceptions import ClientError

def get_db_secrets(secret_name):

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager'
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
            print(e)
            raise e
    else:
        # Decrypts secret using the associated KMS CMK.
        if 'SecretString' in get_secret_value_response:
            secret = get_secret_value_response['SecretString']
            return secret
            
def handler(event, context):
    
    # This is the main Lambda handler.
    # Note that this Lambda is run on Create, Update, and Delete stack actions
    # It only really does anything on Create, but it still has to signal success back for all 3.
    
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
                          {"Message": "Unexpected event RequestType ("+ event +") received from CloudFormation"})
    except: 
        send_response(event, context, "FAILED", {
            "Message": "Exception during processing"})

    
def createSchema(event):
    
    # Connect to the database, and create the schema.
    # DB credentials are retrieved from SecretsManager secret.
    
    # The RDSEndpoint and Secret ARN are passed in via the CloudFormation CustomResource.
    # (See customresource-example-event.txt)
    
    rds_host = event["ResourceProperties"]["RDSEndpoint"]
    
    db_secrets = eval(get_db_secrets(event["ResourceProperties"]["DBSecret"]))
    name= db_secrets['username']
    password = db_secrets['password']
    
    try:
        print("Connecting to " + rds_host + "...")
        conn = pymysql.connect(host=rds_host, user=name, passwd=password, connect_timeout=60)
    except pymysql.MySQLError as e:
        print("ERROR: Unexpected error: Could not connect to MySQL instance.")
        sys.exit()
    
    # Create a very simple database schema.
    # NOTE that this is resilient and will skip steps if they've already been done (via IF NOT EXISTS)
    # Idempotency!
    with conn.cursor() as cur:
       
        dml1 = "CREATE DATABASE IF NOT EXISTS weather;"
        cur.execute(dml1)

        # Need this so you can use Query Editor (RDS Data API) to run queries in the console
        # such as: select * from weather.WeatherHistory;
        dml4 = "GRANT ALL PRIVILEGES ON weather.* TO 'weatheradmin'@'%';"
        cur.execute(dml4)
          
        dml2 = "USE weather;"
        cur.execute(dml2)
   
        dml3 = "CREATE TABLE IF NOT EXISTS WeatherHistory (id INT(8) UNSIGNED AUTO_INCREMENT PRIMARY KEY, city VARCHAR(64) NOT NULL, temp DECIMAL(5,2) NOT NULL,at_time DATETIME);"
        cur.execute(dml3)

        
        # This really needs more error checking...
        
    conn.commit()
    
    print("Schema created.")

def send_response(event, context, response_status, response_data):
    
    # When the Lambda is done, it needs to communicate status back to CloudFormation.
    
    # We send status back to CloudFormation by perfoming a PUT to a S3 pre-signed URL.
    # This is why the Lambda must be connected to a Private subnet with NATGW - it has to be able to talk to S3.
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

    # If you get timeouts here - double check that your Private Subnet can reach S3.
    response = requests.put( event['ResponseURL'], data=response_body.encode('utf-8'), headers=headers_dict)

    print("Response...")
    print(response)


 