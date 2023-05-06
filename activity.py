import logging
import random

import chat
from services import aws_service

logger = logging.getLogger()
logger.setLevel(logging.INFO)

db = aws_service.dynamo_client_factory("activity")

activity_name = ['A', 'B', 'C', 'D', 'E', 'F']
advertiser_name = ['AA', 'BB', 'CC', 'DD', 'EE', 'FF']
address = ['AAA', 'BBB', 'CCC', 'DDD', 'EEE', 'FFF']
discount = ['10%', '20%', '30%', '40%', '50%', '60%']
price = ['1000', '2000', '3000', '4000', '3500', '4500']

"""
Activity Architecture
In the DynamoDB table 'activity', every data entity has a 'id' as partition key.

{   "id" : integer
    "activity_name" : string,
    "advertiser_name" : string,
    "address" : string,
    "discount" : string,
    "user1_name" : string,
    "user2_name" : string,
    "user1_email" : string,
    "user2_email" : string,
    "user2_accept" : bool,
    "user1_accept" : bool，
    "origin_price" : int
}
"""



# insert activity info
def insert_activity(user1, user2):
    logger.info('insert_activity')
    act_id = chat.message_history_key_generator(user1, user2)
    act_index = random.randint(0, len(activity_name)-1)

    db_user = aws_service.dynamo_client_factory('user')
    user_1 = db_user.get_item(Key={'email': user1}).get('Item')
    user_2 = db_user.get_item(Key={'email': user2}).get('Item')

    activity_entity = {
        "id" : act_id,
        "activity_name" : activity_name[act_index],
        "advertiser_name" : advertiser_name[act_index],
        "address" : address[act_index],
        "discount" : discount[act_index],
        "user1_name" : user_1['name'],
        "user2_name" : user_2['name'],
        "user1_email" : user1,
        "user2_email" : user2,
        "user1_accept" : False,
        "user2_accept" : False,
        "origin_price" : price[act_index]
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
def get_activity(event):
    logger.info('get_activity')

    act_id = event['path'].split('/')[-1]
    act_entity = db.get_item(Key={'id': act_id}).get('Item')

    if act_entity is not None:
        return  {'status': 'success', 'data': act_entity}
    else:
        return  {'status': 'fail', 'data': 'no such activity'}


# accept activity
def accept_activity(event):
    logger.info('accept_activity')
    # get act id
    act_id = event['path'].split('/')[-1]
    # get act info
    act_entity = db.get_item(Key={'id': act_id}).get('Item')
    # get email
    email = event['email']

    if act_entity is not None:
        if email == act_entity['user1_email']:
            act_entity['user1_accept'] = True
        else:
            act_entity['user2_accept'] = True

        db.put_item(Item=act_entity)

        return {'status': 'success'}

    else:
        return  {'status': 'fail', 'data': 'no such activity'}




function_register = {
    ('/activity/{activity_id}', 'GET'): get_activity,
    ('/activity/status/{activity_id}', 'PUT'): accept_activity
}

def request_handler(_event):
    function = function_register[(_event['resource'], _event['httpMethod'])]
    return function(_event)