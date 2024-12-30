from common.rabbitMQ.workers import start_worker

def handle_notification_message(message: dict):
    if message.get("event") == "notification.email":
        print(f"Sending email to: {message['recipient']}")
    elif message.get("event") == "notification.approver":
        print(f"Notifying approver: {message['approver_id']}")

if __name__ == "__main__":
    start_worker(queue="notifications.queue", handler=handle_notification_message)
