from common.rabbitMQ.workers import start_worker


def handle_reimbursement_message(message: dict):
    if message.get("event") == "reimbursement.submitted":
        print(f"Validating reimbursement: {message['reimbursement_id']}")
    elif message.get("event") == "reimbursement.updated":
        print(f"Reimbursement updated: {message['reimbursement_id']}")


if __name__ == "__main__":
    start_worker(queue="reimbursements.queue", handler=handle_reimbursement_message)
