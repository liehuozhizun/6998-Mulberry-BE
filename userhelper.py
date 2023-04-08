import logging
import random
import string

import aws_service

logger = logging.getLogger()
logger.setLevel(logging.INFO)

API_GATEWAY_BASE_URL = 'https://d0ch1hik23.execute-api.us-east-1.amazonaws.com/v1'


def verification_link_generator(email: str) -> str or None:
    redis = aws_service.redis_client_factory()
    if redis is None:
        return None

    verification_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    redis.set(verification_code, email, ex=1800)  # expires in 1800 seconds (30 min)

    return API_GATEWAY_BASE_URL + '/user/verify/' + verification_code


def verification_code_verifier(code: str) -> str or None:
    redis = aws_service.redis_client_factory()
    if redis is None:
        return False

    res = redis.get(code)
    if res is not None:
        redis.delete(code)

    return res
