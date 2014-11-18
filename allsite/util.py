import os
import random

import redis

class APIKeys:
    keys = os.environ['GOOGLE_API_KEYS'].split(',')

    @classmethod
    def get(cls):
        return random.choice(cls.keys).strip()

redis_conn = redis.from_url(os.environ['REDIS_URL'])
