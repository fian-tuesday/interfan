import os
import pickle
import pika
import uuid
import rabbit_conf


def remote(fun):
    """ Decorator to potentially call the function remotely on server. """
    def rpc_fun(*args, **kwargs):
        if not rpc_manager.connection:
            return fun(*args, **kwargs)
        else:
            print(f" [x] Requesting _RemoteCallManager to call {fun.__name__}'")
            encoded_rpc_call = pickle.dumps((fun.__name__, args))
            print(" [.] Encoded function name and its arguments.")
            response = rpc_manager.call(encoded_rpc_call)
            print(" [.] Got response.")
            decoded_response = pickle.loads(response)
            print(f" [+] Decoded response successfully.")
            return decoded_response

    return rpc_fun


class _RemoteCallManager:
    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=rabbit_conf.HOST, port=rabbit_conf.PORT,
            credentials=pika.PlainCredentials(rabbit_conf.USER, rabbit_conf.PASSWORD)))
        self.channel = self.connection.channel()
        result = self.channel.queue_declare('', exclusive=True)
        self.callback_queue = result.method.queue
        self.response = None
        self.corr_id = None
        self.channel.basic_consume(self.callback_queue, self.on_response, auto_ack=True)

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body
        else:
            raise ValueError(f'ERROR with correlation_id: {self.corr_id} awaited, ' +
                             f'but {props.correlation_id} got.')

    def call(self, body) -> bytes:
        self.response = bytes()
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(exchange='', routing_key=rabbit_conf.RPC_QUEUE_NAME,
                                   properties=pika.BasicProperties(
                                         reply_to=self.callback_queue,
                                         correlation_id=self.corr_id,
                                         ),
                                   body=body)
        while not self.response:
            self.connection.process_data_events()
        return self.response


rpc_manager = _RemoteCallManager()
