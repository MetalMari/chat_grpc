FROM python:3.8-slim-buster

ENV PYTHONUNBUFFERED 1

WORKDIR /chat

COPY . .

RUN pip install -r requirements.txt

RUN apt-get update && apt-get install make && make compile

COPY ./chat/ .

RUN ls

CMD ["python3", "chat_server.py"]