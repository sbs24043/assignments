# elena-test: A Flower / TensorFlow app

## Install dependencies and project

```bash
pip install -e .
```

## Run with the Simulation Engine

In the `federated-learning` directory, use `flwr run` to run a local simulation:

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

When running the real world embedded federation:

```
flwr run . local-deployment --stream
```

## Starting Points

The project builds on top of https://github.com/adap/flower/tree/main/examples/advanced-tensorflow

pip install -e .
wandb login
flwr run .

The run performs centralized and federated evaluation on the same dataset.

## Running with Docker

### Building images
1. Server
docker build -f serverapp.Dockerfile -t flwr_serverapp:0.0.1-cust .
2. Client
docker build -f clientapp.Dockerfile -t flwr_clientapp:0.0.1-cust .

**Multi-architecture build**:
https://medium.com/@life-is-short-so-enjoy-it/docker-how-to-build-and-push-multi-arch-docker-images-to-docker-hub-64dea4931df9

1. In Docker desktop enable containerd to be used as image store, restart
2. Run the command below:
docker buildx build  --platform linux/arm64/v8 -f clientapp.Dockerfile -t flwr_clientapp:0.0.1-cust .

docker buildx build --platform linux/amd64,linux/arm64 .

3. Tagging and pushing
When the image has been builts, we need to tag it:
docker image ls
docker tag <hash> leeloodub/flwr_clientapp:<version>
docker tag sha256:de43756b41d201488068a93241f64c1ab156530929577ab81146a2e9adf0af3d leeloodub/flwr_serverapp:0.0.1

My Docker Hub repository:
https://hub.docker.com/repository/docker/leeloodub/flwr_clientapp/tags

ISSUES ENCOUNTERED:
exec /python/venv/bin/flwr-clientapp: exec format error

--> this is because need ot build for milti-platform architectyures 

Another issue: error getting credentials - err: exec: "docker-credential-desktop": executable file not found in $PATH,
https://stackoverflow.com/questions/65896681/exec-docker-credential-desktop-exe-executable-file-not-found-in-path

Tried building from Dev build: 
https://hub.docker.com/layers/flwr/clientapp/1.16.0.dev20250220/images/sha256-3e5cc002b08516ab042b5607ef17395c3a8a5278adc715c0f80edb17e5020cae


### Running
0. Networking
docker network create --driver bridge flwr-network

``` bash
ipconfig getifaddr en0
> 192.168.0.41

ping raspberrypi.local
> 192.168.0.250
```

1. Superlink

docker run --rm \
      -p 9091:9091 -p 9092:9092 -p 9093:9093 \
      --network flwr-network \
      --name superlink \
      --detach \
      flwr/superlink:1.17.0 \
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
    flwr/supernode:1.17.0  \
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
    flwr/supernode:1.17.0  \
    --insecure \
    --superlink 192.168.0.41:9092 \
    --node-config "partition-id=1 num-partitions=2" \
    --clientappio-api-address 0.0.0.0:9095 \
    --isolation process

3. Serverapp

sudo docker run \
      -p 9091:9091 -p 9092:9092 -p 9093:9093 \
      --network flwr-network \
      --name superlink \
      --detach \
      flwr/superlink:1.16.0.dev20250220 \
      --insecure \
      --isolation \
      process
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
    -e WANDB_API_KEY=65a365351610afce4d9747a748e220dd9199f986 \
    -e JOB_OWNER=node_1 \
    --detach \
    leeloodub/flwr_clientapp:v0.0.2 \
    --insecure \
    --clientappio-api-address supernode-1:9094

sudo docker run --rm \
    --network flwr-network \
    -e WANDB_API_KEY=65a365351610afce4d9747a748e220dd9199f986 \
    -e JOB_OWNER=node_2 \
    --detach \
    leeloodub/flwr_clientapp:v0.0.2 \
    --insecure \
    --clientappio-api-address supernode-2:9095

5. Run
```
flwr run . local-deployment --stream --run-config use-wandb=false
```

or 
```
flwr run . --stream
```

or

To run the baseline algorithm:
```
export STRATEGY='baseline' && flwr run . 
```

To run the custom algorithm with Loss (DEFAULT) optimization:
```
export STRATEGY='' && OPTIMIZATION_CRITERION='loss' && flwr run . 
```

To run the custom algorithm with Accuracy optimization:
```
export STRATEGY='' && OPTIMIZATION_CRITERION='accuracy' && flwr run . 
```

To run on a different size images:
```
export IMG_SHAPE_1=32 && export IMG_SHAPE_2=32 && export IMG_SHAPE_3=3 && export STRATEGY='baseline' && OPTIMIZATION_CRITERION='' && flwr run .

export IMG_SHAPE_1=32 && export IMG_SHAPE_2=32 && export IMG_SHAPE_3=3 && export STRATEGY='' && OPTIMIZATION_CRITERION='accuracy' && flwr run .

export IMG_SHAPE_1=32 && export IMG_SHAPE_2=32 && export IMG_SHAPE_3=3 && export STRATEGY='' && OPTIMIZATION_CRITERION='loss' && flwr run .
```

### Configuring edge devices
#### Raspberry Pi (runs Ubuntu)

ssh to raspberry pi:
```
ssh olenapleshan@raspberrypi.local
```

```
ssh olenapleshan@192.168.0.250
```

1.1. Add Docker's official GPG key:
```bash
sudo apt-get update
sudo apt-get install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
```

1.2. Add the repository to Apt sources:
Had issues following official doc, so the below solved it
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

**Shut down Raspberry Device**

sudo shutdown -h -P now

**Clearing docker**
docker system prune -a

#### Docker on RockPi:
1. SSH'ing into RockPi https://wiki.radxa.com/Rock4/Debian
On Rockpi, run `hostname -I`
Install Open SSH:
```bash
sudo apt update
sudo apt install openssh-server
sudo systemctl status ssh
sudo systemctl start ssh
sudo systemctl enable ssh
```

Get IP address, then:
```bash
$ ping ip-of-device
$ ssh radxa@192.168.0.112
```

2. Installing Docker See https://wiki.radxa.com/Rockpi4/Docker
Should be similar and possible. Rockpi runs Debian though.
https://stackoverflow.com/questions/41133455/docker-repository-does-not-have-a-release-file-on-running-apt-get-update-on-ubun

```
sudo apt-get remove docker docker-engine docker.io

sudo apt-get update

sudo apt-get install apt-transport-https ca-certificates curl software-properties-common

curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -

sudo apt-key fingerprint 0EBFCD88

sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
xenial \
stable"

sudo apt-get update

sudo apt-get install docker-ce

sudo docker run hello-world
```

Notebale Issues: Base image was not multi-arch, thus building from a Dev build

### Troubleshooting
Releasing ports: 

lsof -i tcp:<port>
kill -9 <PID>


### Cleaning up
 sudo docker stop $(sudo docker ps -a -q) && sudo docker rm $(sudo docker ps -a -q)