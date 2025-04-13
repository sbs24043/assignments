"""tensorflow-example: A Flower / TensorFlow app."""

import json
from logging import INFO
import os
from datetime import datetime
from pathlib import Path

import keras
from flwr_datasets import FederatedDataset
from flwr_datasets.partitioner import DirichletPartitioner, IidPartitioner

from keras import layers

import tf_federation.properties as properties
from flwr.common.typing import UserConfig
from flwr.common import logger


# Make TensorFlow log less verbose
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["KERAS_BACKEND"] = "tensorflow"

DEFAULT_LR = 0.001

MODEL_ARCHITECTURE = keras.Sequential(
        [
            keras.Input(shape=(int(os.getenv('IMG_SHAPE_1', 28)), 
                               int(os.getenv('IMG_SHAPE_2', 28)), 
                               int(os.getenv('IMG_SHAPE_3', 1)))),
            layers.Conv2D(32, kernel_size=(3, 3), activation="relu"),
            layers.MaxPooling2D(pool_size=(2, 2)),
            layers.Conv2D(128, kernel_size=(3, 3), activation="relu"),
            layers.MaxPooling2D(pool_size=(2, 2)),
            layers.Flatten(),
            layers.Dropout(0.5),
            layers.Dense(10, activation="softmax"),
        ]
    )

def init_model(learning_rate: float = DEFAULT_LR):
    logger.log(INFO, "No base model found: Initializing new model")
    # Define a simple CNN and set Adam optimizer
    model = MODEL_ARCHITECTURE
    #optimizer = keras.optimizers.Adam(learning_rate)
    model.compile(
        optimizer='adam',
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model

def load_base_model(weights_path: str, learning_rate: float = DEFAULT_LR):
    logger.log(INFO, f"Loading base model from {weights_path}")
    base_model = MODEL_ARCHITECTURE
    base_model.load_weights(weights_path)

    # Freeze the base layers: Freeze the layers of the base model to prevent them from being trained.
    for layer in base_model.layers:
        layer.trainable = False

    # Add new layers on top of the base model
    model = keras.Sequential(
        [
            base_model,
            layers.Dense(64, activation="relu"),
            layers.Dropout(0.5),
            layers.Dense(10, activation="softmax"),
        ]
    )

    # Compile the model
    optimizer = keras.optimizers.Adam(learning_rate)
    model.compile(
        optimizer=optimizer,
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )

    return model

def load_model(run_config: UserConfig):
    """
    Load and initialize a Keras model based on the provided configuration.

    This function loads a pre-trained model if a weights path is provided in the
    run configuration. If no weights path is provided, it initializes a new model.

    Args:
        run_config (UserConfig): A dictionary containing the configuration for the run.
            Expected keys:
                - "base-weights-path" (str): Path to the pre-trained model weights. Will init a default model when not provided

    Returns:
        keras.Model: A compiled Keras model ready for training or evaluation.
    """
    if "base-weights-path" in run_config and run_config["base-weights-path"]:
      return load_base_model(run_config["base-weights-path"])
    
    learning_rate = float(run_config.get("lr", DEFAULT_LR))
    model = init_model(learning_rate)
    return model

fds = None  # Cache FederatedDataset


def load_data(partition_id: int, num_partitions: int) -> tuple:
    """
    Load and prepare data for a specific client in federated learning.
    
    This function retrieves a partition of the dataset set in DATASET env variable or 
    specified in properties.dataset and prepares it for training and evaluation. The data 
    is partitioned using Dirichlet distribution to create non-IID data distribution across clients.
    The function caches the FederatedDataset to avoid reloading for multiple clients.
    
    Args:
        partition_id: The ID of the partition to load (client ID)
        num_partitions: Total number of partitions to create (total number of clients)
        
    Returns:
        tuple: A tuple containing four elements:
            - x_train (np.ndarray): Normalized training images with shape (n_samples, 28, 28, 1)
            - y_train (np.ndarray): Training labels
            - x_test (np.ndarray): Normalized testing images with shape (n_samples, 28, 28, 1)
            - y_test (np.ndarray): Testing labels
            
    Note:
        - Images are normalized by dividing pixel values by 255.0
        - The dataset is split into 80% training and 20% testing data
        - The function uses a global variable 'fds' to cache the FederatedDataset
    """
    global fds
    if fds is None:
        if os.getenv("PARTITIONER") == "iid":
            partitioner = IidPartitioner(
                num_partitions=num_partitions,
            )
        else:
            partitioner = DirichletPartitioner(
                num_partitions=num_partitions,
                partition_by="label",
                alpha=1.0,
                seed=42,
            )
        fds = FederatedDataset(
            dataset=os.environ.get("DATASET", properties.dataset),
            partitioners={"train": partitioner},
        )
    partition = fds.load_partition(partition_id, "train")
    partition.set_format("numpy")

    # Divide data on each node: 80% train, 20% test
    partition = partition.train_test_split(test_size=0.2)
    try:
        x_train, y_train = partition["train"]["img"] / 255.0, partition["train"]["label"]
        x_test, y_test = partition["test"]["img"] / 255.0, partition["test"]["label"]
    except KeyError:
        x_train, y_train = partition["train"]["img"] / 255.0, partition["train"]["label"]
        x_test, y_test = partition["test"]["img"] / 255.0, partition["test"]["label"]

    return x_train, y_train, x_test, y_test

