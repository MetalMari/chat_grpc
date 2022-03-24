#!/bin/bash

#set chat directory as main
PWD=`pwd`
export PYTHONPATH=$PWD/chat

#set name, host and port of local etcd storage
export STORAGE=etcd
export STORAGE_HOST=localhost
export STORAGE_PORT=2379

#set host name and port for server
export SERVER_HOST=localhost
export SERVER_PORT=50051

