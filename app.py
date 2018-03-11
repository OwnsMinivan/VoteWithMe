import boto3
import json
from botocore.exceptions import ClientError

from flask import Flask, jsonify, request

dynamodb = boto3.resource("dynamodb", region_name='us-east-1')
UserTable = dynamodb.Table('UsersDB1')
QuestionTable = dynamodb.Table('QuestionDB1')

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
                ':p': new_questionID
            },
            ReturnValues="UPDATED_NEW"
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        return True


#-----Core Routing ---

@app.route('/sms_test', methods=['POST'])
def sms_test():
    try:
        parsed_json = json.loads(request.data)
        parsed_from = parsed_json['from']
        parsed_body = parsed_json['body']
        print("This was an SMS test. {}".format(parsed_json['body']))
    except KeyError as e:
        return "error. {}".format(request.get_json())
        print(e)
    else:
        return "Hello {}".format(request.get_json())

@app.route('/inbound', methods=['POST'])
def inbound():
    print("Inbound Text: {}".format(request.form))

@app.route('/question/data/<sessionID>')
def test_update(sessionID):
    print("I got this as the session ID: {}".format(sessionID))
    questionID = GetQuestionID(sessionID)
    print("this is the questionID I have: {}".format(questionID))
    try:
        response = UserTable.get_item(
            Key={
                'QuestionID': questionID
            }
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        item = response['Item']
        print("GetItem succeeded:")
        return jsonify(item)

@app.route('/question/data/<sessionID>/next/', methods=['POST'])
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
