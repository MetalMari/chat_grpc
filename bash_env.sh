#!/bin/bash

PWD=`pwd`
export PYTHONPATH=$PWD/chat
export FILL_USERS=True
export STORAGE=etcd
export SERVER_HOST=localhost
export SERVER_PORT=50051
export STORAGE_HOST=localhost
export STORAGE_PORT=2379
