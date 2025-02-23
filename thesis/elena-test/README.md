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

### Building images
1. Server
docker build -f serverapp.Dockerfile -t flwr_serverapp:0.0.1 .

2. Client
docker build -f clientapp.Dockerfile -t flwr_clientapp:0.0.1 .

Multi-architecture build:
1. In Docker desktop enable containerd to be used as image store, restart
2. Run the command below:
docker buildx build  --platform linux/amd64,linux/arm64/v8 -f clientapp.Dockerfile -t flwr_clientapp:0.0.1 .

docker buildx build --platform linux/amd64,linux/arm64 .

When the image has been builts, we need to tag it:
docker tag dd939551df54 leeloodub/sbs24043:flwr_clientapp

My Docker Hub repository:
https://hub.docker.com/repository/docker/leeloodub/sbs24043/tags

ISSUES ENCOUNTERED:
exec /python/venv/bin/flwr-clientapp: exec format error

--> this is because need ot build for milti-platform architectyures 



### Running
0. Networking
docker network create --driver bridge flwr-network

``` bash
ipconfig getifaddr en0
> 192.168.0.41

ping raspberrypi.local
> 192.168.0.250
```

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
    --superlink 192.168.0.41:9092 \
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

Or if pulling the image from Dockerhub:

sudo docker run --rm \
    --network flwr-network \
    --detach \
    leeloodub/sbs24043:v0.01-tutorial \
    --insecure \
    --clientappio-api-address supernode-1:9094

5. Run

flwr run . local-deployment --stream (--run-config use-wandb=false)


### Configuring edge devices

1. Raspberry Pi (runs Ubuntu)

1.1. Add Docker's official GPG key:
```bash
sudo apt-get update
sudo apt-get install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
```

1.2. Add the repository to Apt sources:
Had issues following officia doc, so the below solved it
https://stackoverflow.com/questions/41133455/docker-repository-does-not-have-a-release-file-on-running-apt-get-update-on-ubun

```bash
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
```

1.3. Install Docker packages
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin