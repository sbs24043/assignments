"""elena-test: A Flower / TensorFlow app."""

from typing import Tuple, Dict, Any
from flwr.client import NumPyClient, ClientApp
from flwr.common import Context
from elena_test.task import load_data, load_model
import numpy as np


# Define Flower Client and client_fn
class FlowerClient(NumPyClient):
    def __init__(
        self, 
        model: Any, 
        data: Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray], 
        epochs: int, 
        batch_size: int, 
        verbose: int
    ) -> None:
        self.model = model
        self.x_train, self.y_train, self.x_test, self.y_test = data
        self.epochs = epochs
        self.batch_size = batch_size
        self.verbose = verbose

    def fit(self, parameters: np.ndarray, config: Dict[str, Any]) -> Tuple[np.ndarray, int, Dict[str, Any]]:
        self.model.set_weights(parameters)
        self.model.fit(
            self.x_train,
            self.y_train,
            epochs=self.epochs,
            batch_size=self.batch_size,
            verbose=self.verbose,
        )
        return self.model.get_weights(), len(self.x_train), {}

    def evaluate(self, parameters: np.ndarray, config: Dict[str, Any]) -> Tuple[float, int, Dict[str, float]]:
        self.model.set_weights(parameters)
        loss, accuracy = self.model.evaluate(self.x_test, self.y_test, verbose=0)
        return loss, len(self.x_test), {"accuracy": accuracy}


def client_fn(context: Context) -> NumPyClient:
    # Load model and data
    net = load_model()

    partition_id = context.node_config["partition-id"]
    num_partitions = context.node_config["num-partitions"]
    data = load_data(partition_id, num_partitions)
    epochs = context.run_config["local-epochs"]
    batch_size = context.run_config["batch-size"]
    verbose = context.run_config.get("verbose")

    # Return Client instance
    return FlowerClient(
        net, data, epochs, batch_size, verbose
    ).to_client()


# Flower ClientApp
app = ClientApp(
    client_fn=client_fn,
)