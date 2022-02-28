import sys
import os
import boto3
import requests
import json
import pymysql
from datetime import datetime
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
            
def get_api_secret():

    secret_name = "openweather-api-key"
    secret = ""

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
        raise e
    else:
        # Decrypts secret using the associated KMS CMK.
        # Depending on whether the secret is a string or binary, one of these fields will be populated.
        secret = json.loads(get_secret_value_response['SecretString'])
        
    return secret['apikey']


# Initialize API Key and DB Secrets outside of Handler for efficiency
# API_KEY is a global variable that will hold the API Key
# On a COLD START this code will be executed.
# On a WARM START these variables will already be populated (This code doesn't run)
API_KEY = get_api_secret()
DB_SECRETS = eval(get_db_secrets(os.environ["DB_SECRET_ARN"]))

            
def lambda_handler(event, context):
    
    print(event)
    
    print("Lambda function ARN:", context.invoked_function_arn)
    print("Lambda function Version:", context.function_version)
    print("Lambda function memory limits in MB:", context.memory_limit_in_mb)
    
    location = event['queryStringParameters']['city']
    
    print("Retrieving weather for city = " + location)
    
    
    rds_host = os.environ["RDS_ENDPOINT"]
    name= DB_SECRETS['username']
    password = DB_SECRETS['password']
    db_name = "weather"
    
    # We need to check for:
    # 
    # Unexpected error: Could not connect to MySQL instance.
    #[ERROR]	2021-05-06T10:06:12.451Z	3bf6616c-1a25-4f55-8047-09cb748b4ddf	(1045, "Access denied for user 'admin'@'172.31.70.62' (using password: YES)")
    try:
        conn = pymysql.connect(host=rds_host, user=name, passwd=password, db=db_name, connect_timeout=20)
    except pymysql.MySQLError as e:
        print("ERROR: Unexpected error: Could not connect to MySQL instance.")
        print(e)
        # If We received Access denied for user, we simply grab the secret again - presumably it has been rotated.
        if "Access denied for user" in str(e):
            print("Password may have been rotated, retrieving latest password...")
            secret_info = eval(get_db_secrets(os.environ["DB_SECRET_ARN"]))
            password = secret_info['password']
            conn = pymysql.connect(host=rds_host, user=name, passwd=password, db=db_name, connect_timeout=20)
        else:
            sys.exit()
    
    weather = get_weather(API_KEY, location)
 
    print(weather['main']['temp'])
    print(weather)  
    
    now = datetime.now()
    print(now.strftime("%Y-%m-%d %H:%M:%S"))
   
    with conn.cursor() as cur:
  
        data =  (location, str(weather['main']['temp']),  now.strftime("%Y-%m-%d %H:%M:%S"))
        cur.execute("insert into WeatherHistory (city, temp, at_time) values( %s, %s, %s)", data)
        conn.commit()
        
        cur.execute("select avg(temp) from WeatherHistory where city = %s group by city limit 100", location)
       
        result = cur.fetchone()
        # Add the Average Temperature for this city to the output result.
        weather["AverageTemperature"] = float(result[0])
        
        print(result)
    conn.commit()
    
    #Add something to the output we can use to demonstrate code changes
    weather['PyWeatherVersion'] = "1.0.0"
    
    print("Lambda time remaining in MS:", context.get_remaining_time_in_millis())
    
    # This is compatible with Lambda Proxy Integration - this is the expected response format:
    return {
       "statusCode": 200,
       "isBase64Encoded": False,
       "headers": {
          "Content-Type": "application/json"
        },
        "body": json.dumps(weather)
    }

def get_weather(api_key, location):
    url = "https://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid={}".format(location, api_key)
    r = requests.get(url)
    
    return r.json()

