#!/bin/bash

# Create the Docker network
# ./client-run.sh "node-1" 9094 0 2 v0.0.4-custom-deploy
# ./client-run.sh "node-2" 9095 1 2 v0.0.4-custom-deploy

sudo docker network create --driver bridge flwr-network

MODE_NAME=$1
SUPERNODE_NAME="super$1"
PORT=$2
PARTITION_ID=$3
NUM_PARTITIONS=$4
CLIENT_VERSION=$5

# Function to start a supernode
start_supernode() {
    sudo docker run \
        -p $PORT:$PORT \
        --network flwr-network \
        --name $SUPERNODE_NAME \
        --detach \
        flwr/supernode:1.16.0.dev20250220 \
        --insecure \
        --superlink 192.168.0.41:9092 \
        --node-config "partition-id=$PARTITION_ID num-partitions=$NUM_PARTITIONS" \
        --clientappio-api-address 0.0.0.0:$PORT \
        --isolation process
}

# Function to start a client
start_client() {
    local job_owner=$1
    local supernode_address=$SUPERNODE_NAME:$PORT

    sudo docker run --rm \
        --network flwr-network \
        -e WANDB_API_KEY=65a365351610afce4d9747a748e220dd9199f986 \
        -e JOB_OWNER=$job_owner \
        -e RUN_ID='exp-mnist' \
        -e DATASET='ylecun/mnist' \
        --detach \
        leeloodub/flwr_clientapp:$CLIENT_VERSION \
        --insecure \
        --clientappio-api-address $supernode_address
}

start_supernode
start_client