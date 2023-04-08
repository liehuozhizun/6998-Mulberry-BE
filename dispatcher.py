import json
import logging
import importlib

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def request_dispatcher(event, context):
    logger.info('-------------------------')
    logger.info(event)

    try:
        module_name = event['resource'].split("/")[1]

        if module_name is None:
            logger.error("Can't find proper request handler: resource - %s, module - %s",
                         event['resource'], module_name)
            return {
                'statusCode': 400,
                'body': '{"status": "fail", "message":"No proper handler found for the endpoint"}'
            }

        module = importlib.import_module(module_name)
        handler = module.request_handler
        resp = handler(event)

        logger.info('Complete request')
        logger.info(resp)
        logger.info('-------------------------')
        return {
            'statusCode': 200,
            'body': json.dumps(resp)
        }
    except Exception as e:
        logger.error("Unhandled Exception occurs!")
        logger.exception(e)
        return {
            'statusCode': 500,
            'body': '{"status": "fail", "message":"Unhandled Exception occurs"}'
        }
