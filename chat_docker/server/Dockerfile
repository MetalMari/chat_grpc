FROM python:3.8-slim-buster

ENV PYTHONUNBUFFERED 1

COPY ./chat ./app/chat
COPY ./chat_protos ./app/chat_protos
COPY ./requirements.txt ./app

WORKDIR /app

RUN pip install -r requirements.txt \
    && python -m grpc_tools.protoc -I./chat_protos --python_out=./chat --grpc_python_out=./chat ./chat_protos/chat.proto

CMD ["python3", "chat/chat_server.py"]
