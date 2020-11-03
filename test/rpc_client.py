#!/usr/bin/env python
import pika
import uuid
import os

RABBIT_HOST = os.environ.get('RABBIT_HOST', 'localhost')
RABBIT_USER = os.environ.get('RABBIT_USER', 'guest')
RABBIT_PASSWORD = os.environ.get('RABBIT_PASSWORD', '')


class FibonacciRpcClient(object):
    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=RABBIT_HOST, port=5672,
            credentials=pika.PlainCredentials(RABBIT_USER, RABBIT_PASSWORD)))

        self.channel = self.connection.channel()

        result = self.channel.queue_declare('', exclusive=True)
        self.callback_queue = result.method.queue
        self.response = None
        self.corr_id = None

        self.channel.basic_consume(self.callback_queue,
                                   self.on_response, auto_ack=True)

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def call(self, n):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(exchange='',
                                   routing_key='rpc_queue',
                                   properties=pika.BasicProperties(
                                         reply_to=self.callback_queue,
                                         correlation_id=self.corr_id,
                                         ),
                                   body=str(n))
        while self.response is None:
            self.connection.process_data_events()
        return int(self.response)


fibonacci_rpc = FibonacciRpcClient()

for i in range(31):
    print(f" [x] Requesting fib({i})")
    response = fibonacci_rpc.call(i)
    print(" [.] Got %r" % (response,))
