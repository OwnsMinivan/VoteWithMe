#! /etc/usr/bin/python3

""" This is the main backend application for our project 
"""

import json
import boto3

from flask import Flask, jsonify, request

#Create the connections to the DB for the users
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
UsersTable = dynamodb.Table('UsersDB')

# ---Start web app --
app = Flask(__name__)

def lambda_handler(event, context):
    # TODO implement
    print(event)




@app.route("/")
def Hello():
    return "Hello!"


if __name__ == '__main__':
    app.run()


