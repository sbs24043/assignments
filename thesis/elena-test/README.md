# elena-test: A Flower / TensorFlow app

## Install dependencies and project

```bash
pip install -e .
```

## Run with the Simulation Engine

In the `elena-test` directory, use `flwr run` to run a local simulation:

```bash
flwr run .
```

## Run with the Deployment Engine

Launch superlink:

```bash
flower-superlink --insecure
```

Launch supernode:

```bash
flower-supernode      --insecure      --superlink 127.0.0.1:9092      --clientappio-api-address 127.0.0.1:9094      --node-config "partition-id=0 num-partitions=2"
```

## Starting Points

The project builds on top of https://github.com/adap/flower/tree/main/examples/advanced-tensorflow

pip install -e .
wandb login
flwr run .

The run performs centralized and federated evaluation on the same dataset.

## Running with docker

0. Networking
docker network create --driver bridge flwr-network

ipconfig getifaddr en0
> 192.168.0.41

docker network create --driver ipvlan server-network

docker network create -d ipvlan \
    --subnet=192.168.0.0/24 \
    --gateway=192.168.0.41 \
    -o ipvlan_mode=l2 \
    -o parent=eth0 server-network

1. Superlink

sudo docker run --rm \
      -p 9091:9091 -p 9092:9092 -p 9093:9093 \
      --network flwr-network \
      --name superlink \
      --detach \
      flwr/superlink:1.15.2 \
      --insecure \
      --isolation \
      process

docker network connect host superlink


2. Supernodes

sudo docker run --rm \
    -p 9094:9094 \
    --network flwr-network \
    --name supernode-1 \
    --detach \
    flwr/supernode:1.15.2  \
    --insecure \
    --superlink superlink:9092 \
    --node-config "partition-id=0 num-partitions=2" \
    --clientappio-api-address 0.0.0.0:9094 \
    --isolation process

sudo docker run --rm \
    -p 9095:9095 \
    --network flwr-network \
    --name supernode-2 \
    --detach \
    flwr/supernode:1.15.2  \
    --insecure \
    --superlink superlink:9092 \
    --node-config "partition-id=1 num-partitions=2" \
    --clientappio-api-address 0.0.0.0:9095 \
    --isolation process

3. Serverapp

sudo docker run --rm \
    --network flwr-network \
    -e WANDB_API_KEY=<KEY> \
    --name serverapp \
    --detach \
    flwr_serverapp:0.0.1 \
    --insecure \
    --serverappio-api-address superlink:9091

docker network connect server-network serverapp



4. Clientapp

docker run --rm \
    --network flwr-network \
    --detach \
    flwr_clientapp:0.0.1  \
    --insecure \
    --clientappio-api-address supernode-1:9094

docker run --rm \
    --network flwr-network \
    --detach \
    flwr_clientapp:0.0.1 \
    --insecure \
    --clientappio-api-address supernode-2:9095

5. Run

flwr run . local-deployment --stream (--run-config use-wandb=false)