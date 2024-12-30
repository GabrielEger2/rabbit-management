from common.rabbitMQ.config import RabbitMQConnection


def get_rabbitmq(queue: str) -> RabbitMQConnection:
    rabbitmq = RabbitMQConnection(queue=queue)
    rabbitmq.connect()
    return rabbitmq
