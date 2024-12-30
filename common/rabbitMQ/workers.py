from common.rabbitMQ.config import RabbitMQConnection
from typing import Callable


def start_worker(queue: str, handler: Callable[[dict], None]):
    rabbitmq = RabbitMQConnection(queue=queue)
    rabbitmq.connect()

    def message_handler(message: dict):
        handler(message)

    rabbitmq.consume(message_handler)
    rabbitmq.start_consuming()
