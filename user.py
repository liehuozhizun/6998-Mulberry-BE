import json
import logging
import aws_service

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def signup(event) -> dict:
    logger.info("signup")
    data = json.loads(event['body'])

    # Create new user record in DynamoDB
    db = aws_service.dynamo_client_factory("user")
    if db.get_item(Key={'email': data['email']}).get('Item') is not None:
        logger.error("Signup failed: email already exists - %s", data['email'])
        return {'status': 'fail', 'message': 'email already exists'}
    db.put_item(Item={'email': data['email'], 'password': data['password']})

    # Automatically send a verification email
    ses_success = aws_service.ses_send_email(
        target_email_address=data['email'],
        subject='Welcome to Mulberry! Please verify your email!',
        body='Hi<br>Please click this link to verify your email: ' + 'xxx' + '<br>' +
        'Your verification link will expire in 30 minutes.'
    )
    if not ses_success:
        logger.error('Email sent to %s failed!', data['email'])
        return {'status': 'success', 'message': 'failed to send verification email'}

    return {'status': 'success'}


def login(event):
    logger.info("login")


def logout(event):
    logger.info("logout")


def change_password(event):
    logger.info("change_password")


def resend_verification(event):
    logger.info("resend_verification")


def verify(event):
    logger.info("verify")


def get_user(event):
    logger.info("get_user")


def create_user(event):
    logger.info("create_user")


def update_user(event):
    logger.info("update_user")


function_register = {
    ('/user/signup', 'POST'): signup,
    # ('/user/login', 'POST'): login,
    # ('/user/logout', 'POST'): logout,
    # ('/user/password', 'PUT'): change_password,
    # ('/user/verify/resend/{user_id}', 'POST'): resend_verification,
    # ('/user/verify/{token}', 'POST'): verify,
    # ('/user/{user_id}', 'GET'): get_user,
    # ('/user/{user_id}', 'POST'): create_user,
    # ('/user/{user_id}', 'PUT'): update_user
}


def request_handler(_event):
    function = function_register[(_event['resource'], _event['httpMethod'])]
    return function(_event)
