FROM python:3.8-slim

WORKDIR /usr/src/workers/reimbursements

COPY  common ./common
COPY apps/workers/reimbursements .

RUN pip install --no-cache-dir -r requirements.txt