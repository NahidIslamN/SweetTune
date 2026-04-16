import os
import redis
from django.conf import settings

# Prefer an env-configured URL; fallback to localhost DB 1
REDIS_URL = getattr(settings, 'CHANNEL_REDIS_URL', os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/1'))

try:
    r = redis.from_url(REDIS_URL, decode_responses=True)
except Exception:
    r = None


def should_enqueue_task(user_id):
    key = f"delivered_task:{user_id}"
    try:
        if r is None:
            # If redis not available, be conservative and allow enqueue
            return True

        # If key exists → skip
        if r.exists(key):
            return False

        # Set key for 60 seconds
        r.set(key, "1", ex=60)
        return True
    except Exception:
        # On redis errors, allow enqueue to avoid silently dropping work
        return True
