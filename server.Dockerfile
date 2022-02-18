FROM python:3.8-slim-buster

ENV PYTHONUNBUFFERED 1

COPY . .

RUN apt-get update && apt-get upgrade -y && pip install -r requirements.txt && apt-get install -y make && make compile

WORKDIR /chat

CMD ["python3", "chat_server.py"]