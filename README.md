# Chat app using grpc

## Description
Chat is  client-server app uses gRPC protocol for communication. It supports next operations:
 - Get list of users
 - Send a message to user
 - Get messages in queue and subscribe to new ones.

As data storage is used `etcd` storage.

## Environment Setup
Create new directory and go to it (optionally):
```bash
mkdir my_directory
cd my_directory
```
Create and activate virtual environment:
```bash
python3 -m venv virtualvenv
source virtualvenv/bin/activate
```

## Checkout
Clone repository, go to `chat_protos` directory and update submodules:
```bash
git clone https://github.com/MetalMari/chat_grpc.git
cd chat_grpc/chat_protos
git submodule update --init --recursive
```

## Installation
Go to `chat_grpc` directory to install requirements and env variables:
```bash
pip install -r requirements.txt
source bash_env.sh
```

## gRPC Code Generation
Generate gRPC files for python using Makefile:
```bash
make compile-proto
```
Generate gRPC code without make:
```bash
python -m grpc_tools.protoc -I./chat_protos --python_out=./chat --grpc_python_out=./chat ./chat_protos/chat.proto
```

## Usage Instructions
Install `etcd` and run it in terminal:
```bash
etcd
```
In new terminal go to `chat`directory and run chat server:
```bash
python chat_server.py
```
Open new terminal, in `chat` directory run chat client.
1. to get list of users:
```bash
python chat_client.py users
```
2. to send message:
```bash
python chat_client.py -m login_from login_to text_body message
```
3. to subscribe for getting messages:
```bash
python chat_client.py login subscribe
```

## Run Unit Tests
Run all tests using Makefile:
```bash
make unittest
```
or with pytest module:
```bash
make pytest
```
Run tests without make:
```bash
python -m unittest
```
or with pytest module:
```bash
python -m pytest
```
For measuring code coverage and effectiveness of tests run:
```bash
coverage run -m unittest
coverage report
```
For a nicer presentation, use `coverage html` to get annotated HTML listings detailing missed lines:
```bash
coverage html
```
Go to `htmlcov` directory, open index.html report in browser.

## Run Chat With Docker
At `chat_grpc` directory run command:
```bash
sudo docker-compose up -d
```
