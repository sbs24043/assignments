#!/bin/bash

docker build -f serverapp.Dockerfile -t flwr_serverapp:0.0.1 .

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
    -e WANDB_API_KEY=123 \
    --name serverapp \
    --detach \
    leeloodub/flwr_serverapp:0.0.1 \
    --insecure \
    --serverappio-api-address superlink:9091

flwr run . local-deployment --stream --run-config use-wandb=false
