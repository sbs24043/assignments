#!/bin/bash

sudo docker network create --driver bridge flwr-network

sudo docker run \
    -p 9094:9094 \
    --network flwr-network \
    --name supernode-1 \
    --detach \
    flwr/supernode:1.16.0.dev20250220  \
    --insecure \
    --superlink 192.168.0.41:9092 \
    --node-config "partition-id=0 num-partitions=2" \
    --clientappio-api-address 0.0.0.0:9094 \
    --isolation process

sudo docker run \
    -p 9095:9095 \
    --network flwr-network \
    --name supernode-2 \
    --detach \
    flwr/supernode:1.16.0.dev20250220  \
    --insecure \
    --superlink 192.168.0.41:9092 \
    --node-config "partition-id=1 num-partitions=2" \
    --clientappio-api-address 0.0.0.0:9095 \
    --isolation process

export CLIENT_VERSION=v0.0.1-custom

sudo docker run --rm \
    --network flwr-network \
    -e WANDB_API_KEY=65a365351610afce4d9747a748e220dd9199f986 \
    -e JOB_OWNER=node_1 \
    --detach \
    leeloodub/flwr_clientapp:$CLIENT_VERSION  \
    --insecure \
    --clientappio-api-address supernode-1:9094 

sudo docker run --rm \
    --network flwr-network \
    -e WANDB_API_KEY=65a365351610afce4d9747a748e220dd9199f986 \
    -e JOB_OWNER=node_2 \
    --detach \
    leeloodub/flwr_clientapp:$CLIENT_VERSION  \
    --insecure \
    --clientappio-api-address supernode-2:9095