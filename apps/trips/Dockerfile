FROM python:3.8-slim

# Set the working directory
WORKDIR /usr/src/apps/trips

COPY common ./common
COPY  apps/trips .

RUN apt-get update && apt-get -y install libpq-dev gcc
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8003
