from common.rabbitMQ.config import RabbitMQConnection


def get_reimbursements_rabbitmq() -> RabbitMQConnection:
    rabbitmq = RabbitMQConnection(queue="reimbursements.queue")
    rabbitmq.connect()
    return rabbitmq


def get_notifications_rabbitmq() -> RabbitMQConnection:
    rabbitmq = RabbitMQConnection(queue="notifications.queue")
    rabbitmq.connect()
    return rabbitmq
