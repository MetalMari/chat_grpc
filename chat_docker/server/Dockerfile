FROM python:3.8-alpine

ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt && make compile

CMD ["python3", "chat_server.py"]