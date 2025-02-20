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
