import json
import logging
from datetime import datetime

import userhelper
import aws_service

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def signup(event) -> dict:
    logger.info('signup')
    data = json.loads(event['body'])

    # Create new user record in DynamoDB
    db = aws_service.dynamo_client_factory("user")
    if db.get_item(Key={'email': data['email']}).get('Item') is not None:
        logger.error("Signup failed: email already exists - %s", data['email'])
        return {'status': 'fail', 'message': 'email already exists'}

    user = {
        'email': data['email'],
        'status': 'PENDING',
        'password': data['password'],
        'created_ts': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'email_verified': False
    }
    db.put_item(Item=user)

    # Automatically send a verification email
    success = userhelper.verification_email_sender(data['email'])
    if not success:
        return {'status': 'success', 'message': 'Failed to send verification email'}

    return {'status': 'success'}


def login(event):
    logger.info("login")
    data = json.loads(event['body'])

    db = aws_service.dynamo_client_factory('user')
    user = db.get_item(Key={'email': data['email']}).get('Item')

    if user is None:
        return {'status': 'fail', 'message': 'User doesn\'t exist'}
    if user['password'] != data['password']:
        return {'status': 'fail', 'message': 'Wrong password'}

    user['password'] = None
    return {'status': 'success', 'data': user}


def change_password(event):
    logger.info("change_password")
    data = json.loads(event['body'])

    db = aws_service.dynamo_client_factory('user')
    user = db.get_item(Key={'email': data['email']}).get('Item')
    user['password'] = data['password']
    db.put_item(Item=user)

    return {'status': 'success'}


def resend_verification(event):
    logger.info("resend_verification")
    email = event['path'].split('/')[-1]

    # Check if user exists or has been verified
    db = aws_service.dynamo_client_factory('user')
    user = db.get_item(Key={'email': email}).get('Item')
    if user is None or user['email_verified'] is True:
        logger.info('User - %s email has been verified or user not exists')
        return {'status': 'fail', 'message': 'Email has been verified or user not exists!'}

    # Send out verification email
    success = userhelper.verification_email_sender(email)
    if not success:
        return {'status': 'fail', 'message': 'Failed to send verification email'}

    return {'status': 'success'}


def verify(event):
    logger.info("verify")

    # Verify the verification code passed in by path
    verification_code = event['path'].split('/')[-1]
    result = userhelper.verification_code_verifier(verification_code)
    if result is None:
        logger.error("Verification failed: no code is found in Redis, key - %s", verification_code)
        return {'status': 'fail', 'message': 'Either verification is expired or already verified'}

    # Update the user info
    db = aws_service.dynamo_client_factory('user')
    user = db.get_item(Key={'email': result}).get('Item')
    user['email_verified'] = True
    db.put_item(Item=user)

    return {'status': 'success'}


def get_user(event):
    logger.info("get_user")
    email = event['path'].split('/')[-1]
    db = aws_service.dynamo_client_factory('user')
    user = db.get_item(Key={'email': email}).get('Item')
    user['password'] = None
    return {'status': 'success', 'data': user}


def update_user(event):
    logger.info("create_user")
    user_new = json.loads(event['body'])

    db = aws_service.dynamo_client_factory('user')
    user_old = db.get_item(Key={'email': user_new['email']}).get('Item')

    user_new['password'] = user_old['password']
    user_new['created_ts'] = user_old['created_ts']
    user_new['email_verified'] = user_old['email_verified']
    user_new['status'] = 'ACTIVE'

    return {'status': 'success'}


function_register = {
    ('/user/signup', 'POST'): signup,
    ('/user/login', 'POST'): login,
    ('/user/password', 'PUT'): change_password,
    ('/user/verify/resend/{user_id}', 'POST'): resend_verification,
    ('/user/verify/{token}', 'POST'): verify,
    ('/user/{user_id}', 'GET'): get_user,
    ('/user/{user_id}', 'PUT'): update_user
}


def request_handler(_event):
    function = function_register[(_event['resource'], _event['httpMethod'])]
    return function(_event)
