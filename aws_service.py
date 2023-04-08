import boto3
import logging
from redis import RedisCluster

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamo_tables = {
    "user": "mulberry-user",
    "activity": "mulberry-activity",
    "coupon": "mulberry-coupon",
    "interest": "mulberry-interest",
    "message": "mulberry-message"
}


def dynamo_client_factory(table: str):
    db = boto3.resource('dynamodb')
    db_table = dynamo_tables.get(table)
    if db_table is None:
        logger.error("No DynamoDB Table {}", table)
        raise RuntimeError("Can't create dynamo db client")
    return db.Table(db_table)


def ses_send_email(target_email_address: str,
                   subject: str, body: str) -> bool:
    ses_client = boto3.client('ses')
    message = {
        'Subject': {'Data': subject},
        'Body': {'Html': {'Data': body}}
    }
    try:
        ses_client.send_email(
            Source=target_email_address,
            Destination={'ToAddresses': [target_email_address]},
            Message=message
        )
        logger.info("Email send successfully: target - {}, body - {}",
                    target_email_address, body)
        return True
    except Exception as e:
        logger.error("Failed to send email: target - {}, body - {}",
                     target_email_address, body)
        logger.error(e)
        return False


def redis_client_factory():
    redis_client = RedisCluster(
        startup_nodes=[{"host": "mulberry-radis-cache-0001-001.7tlweq.0001.use1.cache.amazonaws.com", "port": "6379"}],
        decode_responses=True,
        skip_full_coverage_check=True)

    if not redis_client.ping():
        logging.error("Cannot connect to Radis Server")
        return None
    return redis_client
