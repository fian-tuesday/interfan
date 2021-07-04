import os

PORT = 5672
HOST = os.environ.get('RABBIT_HOST', 'localhost')
USER = os.environ.get('RABBIT_USER', 'guest')
PASSWORD = os.environ.get('RABBIT_PASSWORD', '')
RPC_QUEUE_NAME = 'rpc_queue'
