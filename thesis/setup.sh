#!/bin/bash

sudo apt-get update
# Install python deps relevant for this and other examples
sudo apt-get install build-essential zlib1g-dev libssl-dev \
                libsqlite3-dev libreadline-dev libbz2-dev \
                git libffi-dev liblzma-dev libsndfile1 -y

# sudo apt install python3-dev python3-pip  # Python 3
# python3 -m venv "venv"
# source "venv/bin/activate"
# pip install --upgrade "pip"

# Install python 3.10+
pyenv install 3.10.14

# Then create a virtual environment
pyenv virtualenv 3.10.14 my-env

# Activate your environment
pyenv activate my-env

# Then, install flower
pip install flwr

# Install any other dependency needed for your device
# Likely your embedded device will run a Flower SuperNode
# This means you'll likely want to install dependencies that
# your Flower `ClientApp` needs.

pip install <your-clientapp-dependencies>
# python3 -m pip install flwr --break-system-packages

# python3 -m venv path/to/venv
# source path/to/venv/bin/activate
# python3 -m pip install xyz

# cd flower-pytorch
# pip install -e .
# flwr run .