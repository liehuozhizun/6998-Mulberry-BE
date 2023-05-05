import logging
import random
from datetime import datetime

import chat
from services import aws_service

logger = logging.getLogger()
logger.setLevel(logging.INFO)

db = aws_service.dynamo_client_factory("activity")

activity_name = ['A', 'B', 'C', 'D', 'E', 'F']
advertiser_name = ['AA', 'BB', 'CC', 'DD', 'EE', 'FF']
address = ['AAA', 'BBB', 'CCC', 'DDD', 'EEE', 'FFF']
discount = ['10%', '20%', '30%', '40%', '50%', '60%']

"""
Activity Architecture
In the DynamoDB table 'activity', every data entity has a 'id' as partition key.

{   "id" : integer
    "activity_name" : string,
    "advertiser_name" : string,
    "address" : string,
    "discount" : string,
    "valid_through" : string,
    "user1_name" : string,
    "user2_name" : string,
    "status" : string
    "user2_accept" : bool,
    "user1_accept" : bool
}
"""



# insert activity info
def insert_activity(user1, user2):
    logger.info('insert_activity')
    act_id = chat.message_history_key_generator(user1, user2)
    act_index = random.randint(0, len(activity_name)-1)

    activity_entity = {
        "id" : act_id,
        "activity_name" : activity_name[act_index],
        "advertiser_name" : advertiser_name[act_index],
        "address" : address[act_index],
        "discount" : discount[act_index],
        "valid_through" : datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "user1_name" : user1,
        "user2_name" : user2,
        'status' : 'PENDING',
        "user2_accept" : False,
        "user1_accept" : False
    }

    db.put_item(Item=activity_entity)

    return act_id

# check activity exist
def check_activity(user1, user2):
    logger.info('get_activity')
    act_id = chat.message_history_key_generator(user1, user2)
    act_entity = db.get_item(Key={'id': act_id}).get('Item')

    if act_entity is not None:
        return True
    else:
        return False

# get activity info
def get_activity(user1, user2):
    logger.info('get_activity')
    act_id = chat.message_history_key_generator(user1, user2)
    act_entity = db.get_item(Key={'id': act_id}).get('Item')

    if act_entity is None:
        return True
    else:
        return False


# accept activity
def accept_activity():
    logger.info('send_message')
    pass



function_register = {
    ('/activity/activity_id', 'GET'): get_activity,
    ('/activity/status/activity_id', 'PUT'): accept_activity
}

def request_handler(_event):
    function = function_register[(_event['resource'], _event['httpMethod'])]
    return function(_event)