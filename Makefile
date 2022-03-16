compile:
	python -m grpc_tools.protoc -I./chat_protos --python_out=./chat --grpc_python_out=./chat ./chat_protos/chat.proto

test:
	python -m unittest
