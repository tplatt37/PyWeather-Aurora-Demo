import sys
import os
import boto3
import json
import pymysql
import logging

def handler(event, context):
    
    print(event)
    
    rds_host = "my-serverless-cluster.cluster-cill9lr2ub0b.us-east-1.rds.amazonaws.com" 
    name= "admin"
    password = "password"
    
    # Need to check for:
    # 
    # Unexpected error: Could not connect to MySQL instance.
    #[ERROR]	2021-05-06T10:06:12.451Z	3bf6616c-1a25-4f55-8047-09cb748b4ddf	(1045, "Access denied for user 'admin'@'172.31.70.62' (using password: YES)")
    try:
        conn = pymysql.connect(host=rds_host, user=name, passwd=password, connect_timeout=30)
    except pymysql.MySQLError as e:
        logger.error("ERROR: Unexpected error: Could not connect to MySQL instance.")
        logger.error(e)
        sys.exit()
    
    with conn.cursor() as cur:
       
        #data =  (location, str(weather['main']['temp']),  now.strftime("%Y-%m-%d %H:%M:%S"))
        #cur.execute("insert into WeatherHistory (city, temp, at_time) values( %s, %s, %s)", data)
        #conn.commit()
        
        dml = "create database weather;"
        cur.execute(dml)
   
        dml = "use weather;"
        cur.execute(dml)
   
        dml = "CREATE TABLE WeatherHistory (id INT(8) UNSIGNED AUTO_INCREMENT PRIMARY KEY, city VARCHAR(64) NOT NULL, temp DECIMAL(5,2) NOT NULL,at_time DATETIME);"
        cur.execute(dml)
       
        #esult = cur.fetchone()
        # Add the Average Temperature for this city to the output result.
        #weather["AverageTemperature"] = float(result[0])
        
        #print(result)
    conn.commit()
    
    
    
    # This is compatible with Lambda Proxy Integration - this is the expected response format:
    return {
       "statusCode": 200,
       "isBase64Encoded": False,
       "headers": {
          "Content-Type": "application/json"
        },
        "body": json.dumps(event)
    }
