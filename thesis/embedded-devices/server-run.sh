#!/bin/bash
# ./server-run.sh v0.0.4-custom-deploy

SERVER_VERSION=$1

#docker build -f serverapp.Dockerfile -t flwr_serverapp:v0.0.1-custom .

docker network create --driver bridge flwr-network

docker run \
      -p 9091:9091 -p 9092:9092 -p 9093:9093 \
      --network flwr-network \
      --name superlink \
      --detach \
      flwr/superlink:1.16.0.dev20250220 \
      --insecure \
      --isolation \
      process

docker run  \
    --network flwr-network \
    -e WANDB_API_KEY=65a365351610afce4d9747a748e220dd9199f986 \
    -e JOB_OWNER=server \
    -e RUN_ID='exp-mnist' \
    -e OPTIMIZATION_CRITERION='loss' \
    -e DATASET='ylecun/mnist' \
    --name serverapp \
    --detach \
    leeloodub/flwr_serverapp:$SERVER_VERSION \
    --insecure \
    --serverappio-api-address superlink:9091
