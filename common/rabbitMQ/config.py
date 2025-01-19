import pika
import json
import os
from dotenv import load_dotenv

load_dotenv()

RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@localhost:5672/")


class RabbitMQConnection:
    def __init__(self, queue: str):
        self.queue = queue
        self.connection = None
        self.channel = None

    def connect(self):
        params = pika.URLParameters(RABBITMQ_URL)
        self.connection = pika.BlockingConnection(params)
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.queue, durable=True)

    def publish(self, message: dict, routing_key: str = None, headers: dict = None):
        if not self.channel:
            self.connect()
        self.channel.basic_publish(
            exchange="",
            routing_key=routing_key or self.queue,
            body=json.dumps(message),
            properties=pika.BasicProperties(
                headers=headers,
                delivery_mode=2,
            ),
        )

    def consume(self, callback):
        if not self.channel:
            self.connect()

        def _callback(ch, method, properties, body):
            message = json.loads(body)
            callback(message)
            ch.basic_ack(delivery_tag=method.delivery_tag)

        self.channel.basic_consume(queue=self.queue, on_message_callback=_callback)

    def start_consuming(self):
        self.channel.start_consuming()
