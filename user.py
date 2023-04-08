import json
import logging
import aws_service

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def signup(event) -> dict:
    logger.info("signup")
    data = json.loads(event['body'])
    db = aws_service.dynamo_client_factory("user")
    db.put_item(Item={'email': data['email'], 'password': data['password']})
    return {'message': 'success'}


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
