#!/bin/bash

sudo apt update
sudo apt install python3-dev python3-pip  # Python 3
python3 -m venv "venv"
source "venv/bin/activate"
pip install --upgrade "pip"
pip install --ignore-requires-python --upgrade tensorflow-federated 

python -c "import tensorflow_federated as tff; print(tff.federated_computation(lambda: 'Hello World')())"