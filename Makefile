compile:
	python -m grpc_tools.protoc -I./protos --python_out=./chat --grpc_python_out=./chat ./protos/chat.proto