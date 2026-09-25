import os

from dotenv import load_dotenv
from redis import Redis

load_dotenv()

redis_conn = Redis.from_url(
    os.getenv("REDIS_URL"),
    ssl_cert_reqs=None,
)

print("Testing Redis...")
print(redis_conn.ping())
