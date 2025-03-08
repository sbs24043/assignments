"""tensorflow-example: A Flower / TensorFlow app."""

import tf_federation.properties as properties

from tf_federation.strategy import CustomFedAvg
from tf_federation.task import load_model

from datasets import load_dataset
from flwr.common import Context, ndarrays_to_parameters
from flwr.server import ServerApp, ServerAppComponents, ServerConfig


def gen_evaluate_fn(
    x_test,
    y_test,
):
    """Generate the function for centralized evaluation."""

    def evaluate(server_round, parameters_ndarrays, config):
        """Evaluate global model on centralized test set."""
        model = load_model(config)
        model.set_weights(parameters_ndarrays)
        loss, accuracy = model.evaluate(x_test, y_test, verbose=0)
        return loss, {"centralized_accuracy": accuracy}

    return evaluate


def on_fit_config(server_round: int):
    """Construct `config` that clients receive when running `fit()`"""
    lr = 0.001
    # Enable a simple form of learning rate decay
    if server_round > 10:
        lr /= 2
    return {"lr": lr}


# Define metric aggregation function
def weighted_average(metrics):
    # Multiply accuracy of each client by number of examples used
    accuracies = [num_examples * m["accuracy"] for num_examples, m in metrics]
    examples = [num_examples for num_examples, _ in metrics]

    # Aggregate and return custom metric (weighted average)
    return {"federated_evaluate_accuracy": sum(accuracies) / sum(examples)}


def server_fn(context: Context):
    # Initialize model parameters
    ndarrays = load_model(None).get_weights()
    parameters = ndarrays_to_parameters(ndarrays)

    # Prepare dataset for central evaluation

    # This is the exact same dataset as the one downloaded by the clients via
    # FlowerDatasets. However, we don't use FlowerDatasets for the server since
    # partitioning is not needed.
    # We make use of the "test" split only
    global_test_set = load_dataset(properties.dataset)["test"]
    global_test_set.set_format("numpy")

    x_test, y_test = global_test_set["image"] / 255.0, global_test_set["label"]

    # Define strategy
    strategy = CustomFedAvg(
        run_config=context.run_config,
        fraction_fit=context.run_config["fraction-fit"],
        fraction_evaluate=context.run_config["fraction-evaluate"],
        initial_parameters=parameters,
        on_fit_config_fn=on_fit_config,
        evaluate_fn=gen_evaluate_fn(x_test, y_test),
        evaluate_metrics_aggregation_fn=weighted_average,
    )
    config = ServerConfig(num_rounds=context.run_config["num-server-rounds"])

    return ServerAppComponents(strategy=strategy, config=config)


# Create ServerApp
app = ServerApp(server_fn=server_fn)
