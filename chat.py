import json
import logging

from services import aws_service

logger = logging.getLogger()
logger.setLevel(logging.INFO)

DELIMITER = '---'
db = aws_service.dynamo_client_factory("message")

"""
Message Architecture
In the DynamoDB table 'message', every data entity has a 'key' as partition key.

The key is a string but will have two formats:
1. '{email}'
    We name it message_user_key.
    This entity will contain all the message_keys for this user.
    For example,
    { 'key': '1@1.1', 'message_history_keys': [
        '1@1.1---2@2.2', 
        '1@1.1---14@14.14'
    ] }
    Each value in 'message_history_keys' will map to a message history between two users.
    Thus, if we want to find all the message history that has 1@1.1 involved, we need to
    iterate the 'keys' list.

2. '{email-1}---{email-2}'
    We name it message_history_key.
    This key is used to locate the entire message history between email-1 and email-2.
    For example,
    { 
        'key': '1@1.1---2@2.2', 
        '1@1.1': True,
        '2@2.2': False,
        'messages': [
            {'sender_email':'1@1.1', 'message': 'Hi', 'timestamp': '2023-05-01 12:00:00},
            {'sender_email':'2@2.2', 'message': 'Hello!', 'timestamp': '2023-05-01 12:30:00}
    ]}
    This entity also contains the is_read value for either email.

Note:
0. We use DELIMITER const var for the connection of two emails. In this case, it's '---'.
1. Use def message_key_generator to get the valid message_history_key. Enforcing use this
    function to get the key will ensure we can locate the right message history.
2. Use def get_by_user_key(message_user_key) to get the list of message_history_key.
3. Use def get_by_history_key(message_history_key) to get the list of messages between users.
"""


def message_key_generator(email1: str, email2: str) -> str:
    if email1 < email2:
        return f'{email1}{DELIMITER}{email2}'
    else:
        return f'{email2}{DELIMITER}{email1}'


def get_by_user_key(message_user_key: str) -> dict:
    entity = db.get_item(Key={'key': message_user_key}).get('Item')
    if entity is None:
        entity = {'key': message_user_key, 'message_history_keys': []}
    return entity


def get_by_history_key(message_history_key: str) -> dict:
    entity = db.get_item(Key={'key': message_history_key}).get('Item')
    if entity is None:
        entity = {
            'key': message_history_key,
            message_history_key.split(DELIMITER)[0]: False,
            message_history_key.split(DELIMITER)[1]: False,
            'messages': []}
    return entity


def update_message_user_entity(email: str, message_history_key: str):
    user_msg_entity = get_by_user_key(email)
    if message_history_key not in user_msg_entity['message_history_keys']:
        user_msg_entity['message_history_keys'].append(message_history_key)
        db.put_item(Item=user_msg_entity)


def get_chat_list(event):
    logger.info('get_chat_list')
    pass


def get_messages(event):
    logger.info('get_messages')
    pass


def send_message(event):
    logger.info('send_message')
    sender_email = event['email']
    receiver_email = event['path'].split('/')[-1]

    message = json.loads(event['body'])
    message['sender_email'] = sender_email

    # Insert new message
    message_history_key = message_key_generator(sender_email, receiver_email)
    message_history = get_by_history_key(message_history_key)
    message_history['messages'].append(message)
    message_history[sender_email] = True
    message_history[receiver_email] = False
    db.put_item(Item=message_history)

    # Update message user key
    update_message_user_entity(sender_email, message_history_key)
    update_message_user_entity(receiver_email, message_history_key)

    return {'status': 'success'}


function_register = {
    ('/chat', 'GET'): get_chat_list,
    ('/chat/message', 'GET'): get_messages,
    ('/chat/message/{target_email}', 'POST'): send_message
}


def request_handler(_event):
    function = function_register[(_event['resource'], _event['httpMethod'])]
    return function(_event)
