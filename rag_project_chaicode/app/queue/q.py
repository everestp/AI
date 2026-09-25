from dotenv import load_dotenv
from redis import Redis
from rq import Queue
import  os
load_dotenv()
redis_conn = Redis.from_url(
    os.getenv("REDIS_URL"),
    ssl_cert_reqs=None,
)
q = Queue(connection=redis_conn)
