import boto3
import json
import requests

from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key, Attr

from flask import Flask, jsonify, request

dynamodb = boto3.resource("dynamodb", region_name='us-east-1')
UserTable = dynamodb.Table('UsersDB1')
QuestionTable = dynamodb.Table('QuestionDB')

app = Flask(__name__)

#--- Helper Functions ---

def GetQuestionID(sessionID):
    try:
        response = QuestionTable.get_item(
            Key={
                'SessionID': sessionID
            }
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        questionID = response['Item']['QuestionID']
        print("GetItem succeeded: {}".format(questionID))
        return response['Item']['QuestionID']

def IncrementQuestionID(sessionID, new_questionID):
    try:
        response = QuestionTable.update_item(
            Key={
                'SessionID': sessionID
            },
            UpdateExpression="set QuestionID = :p",
            ExpressionAttributeValues={
                ':p': str(new_questionID)
            },
            ReturnValues="UPDATED_NEW"
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        return True

def SaveSMSData(_from, _body):
    questionID = GetQuestionID("12345")
    response = UserTable.put_item(
        Item={
                'QuestionID': str(questionID),
                'From': _from,
                'Body': _body,
                'SessionID': "12345"
            }
        )

def sendReply(_from):
    """ Need to edit the secret and the from
    """
    url = "https://sms.telnyx.com/messages"
    body = "Thanks for participating!"
    headers = {
        "Content-Type: application/json",
        "Accept: application/json",
        "x-profile-secret: MESSAGING_PROFILE_SECRET"
        }
    payload = {
        'To': _from, 
        'From': '+14077511701', 
        'Body': body
        }
    r = requests.post(url, params=payload)
    return r.status.code

#-----Core Routing ---

@app.route('/sms_test', methods=['POST'])
def sms_test():
    try:
        parsed_json = json.loads(request.data)
        parsed_from = parsed_json['from']
        parsed_body = parsed_json['body']
        print("This was an SMS test. {}".format(parsed_json['body']))
        response = SaveSMSData(parsed_from, parsed_body)
    except KeyError as e:
        return "error. {}".format(request.get_json())
        print(e)
    else:
        return "Thanks for participating!"

@app.route('/sms_test/', methods=['POST'])
def sms_test_from_arrow():
    try:
        parsed_json = json.loads(request.data)
        parsed_from = parsed_json['from']
        parsed_body = parsed_json['body']
        print("This was an SMS test from Arrow. {}".format(parsed_json['body']))
        response = SaveSMSData(parsed_from, parsed_body)
    except KeyError as e:
        return "error. {}".format(request.get_json())
        print(e)
    else:
        return "Thanks for participating!"

@app.route('/inbound', methods=['POST'])
def inbound():
    print("Inbound Text: {}".format(request.form))

@app.route('/question/data/<sessionID>')
def test_update(sessionID):
    print("I got this as the session ID: {}".format(sessionID))
    questionID = GetQuestionID(sessionID)
    print("this is the questionID I have: {}".format(questionID))
    try:
        response = UserTable.query(
            KeyConditionExpression=Key('QuestionID').eq(questionID)
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        items = response['Items']
        print("GetItem succeeded:")
        return jsonify(items)

@app.route('/question/data/<sessionID>/next', methods=['POST'])
def next(sessionID):
    print("I got this sessionID to increment the question: {}".format(sessionID))
    questionID = GetQuestionID(sessionID)
    new_questionID = int(questionID) + 1
    update_response = IncrementQuestionID(sessionID, new_questionID)
    if update_response:
        return jsonify(new_questionID)
    else:
        return 500

if __name__ == '__main__':
    app.run()
