"""tensorflow-example: A Flower / Tensorflow app."""

import keras
from tf_federation.task import load_data, load_model

from flwr.client import ClientApp, NumPyClient
from flwr.common import Context, ParametersRecord, RecordSet, array_from_numpy
from flwr.common.typing import UserConfig

from tf_federation.utils import RunManager
from wandb.integration.keras import WandbMetricsLogger, WandbModelCheckpoint

import tf_federation.properties as properties

# https://flower.ai/docs/framework/tutorial-series-customize-the-client-pytorch.html
# Define Flower Client and client_fn
class FlowerClient(NumPyClient):
    """A simple client that showcases how to use the state.

    It implements a basic version of `personalization` by which
    the classification layer of the CNN is stored locally and used
    and updated during `fit()` and used during `evaluate()`.
    """

    def __init__(self, client_state: RecordSet, data, run_config: UserConfig):
        self.client_state = client_state
        self.x_train, self.y_train, self.x_test, self.y_test = data

        self.batch_size = run_config["batch-size"]
        self.local_epochs = run_config["local-epochs"]
        self.local_layer_name = "classification-head"

        self.run_manager = RunManager(run_config)


    def fit(self, parameters, config):
        """Train model locally.

        The client stores in its context the parameters of the last layer in the model
        (i.e. the classification head). The classifier is saved at the end of the
        training and used the next time this client participates.
        """

        model = load_model(config)
        # Apply weights from global models (the whole model is replaced)
        model.set_weights(parameters)
        # Override weights in classification layer with those this client  had at the end of the last fit() round it participated in
        self._load_layer_weights_from_state(model)

        # Create base fit parameters
        fit_params = {
            "x": self.x_train,
            "y": self.y_train,
            "epochs": self.local_epochs,
            "batch_size": self.batch_size,
            "verbose": 0,
        }
        
        # Conditionally add callbacks for wandb logging
        if self.run_manager.use_wandb:
            fit_params["callbacks"] = [
                WandbMetricsLogger(),
                WandbModelCheckpoint("models.keras", monitor="val_accuracy"),
            ]
        
        # Train the model with the configured parameters
        model.fit(**fit_params)

        # Save classification head to context's state to use in a future fit() call
        self._save_layer_weights_to_state(model)

        # Return locally-trained model and metrics
        return (
            model.get_weights(),
            len(self.x_train),
            {},
        )

    def _save_layer_weights_to_state(self, model):
        """Save last layer weights to state."""
        state_dict_arrays = {}
        # Get weights from the last layer
        layer_name = "dense"
        for variable in model.get_layer(layer_name).trainable_variables:
            state_dict_arrays[f"{layer_name}.{variable.name}"] = array_from_numpy(
                variable.numpy()
            )

        # Add to recordset (replace if already exists)
        self.client_state.parameters_records[self.local_layer_name] = ParametersRecord(
            state_dict_arrays
        )

    def _load_layer_weights_from_state(self, model):
        """Load last layer weights to state."""
        if self.local_layer_name not in self.client_state.parameters_records:
            return

        param_records = self.client_state.parameters_records
        list_weights = []
        for v in param_records[self.local_layer_name].values():
            list_weights.append(v.numpy())

        # Apply weights
        model.get_layer("dense").set_weights(list_weights)

    def evaluate(self, parameters, config):
        """Evaluate the global model on the local validation set.

        Note the classification head is replaced with the weights this client had the
        last time it trained the model.
        """
        # Instantiate model
        model = load_model(config)
        # Apply global model weights received
        model.set_weights(parameters)
        # Override weights in classification layer with those this client
        # had at the end of the last fit() round it participated in
        # DO I NEED THE BELOW???
        #self._load_layer_weights_from_state(model)
        loss, accuracy = model.evaluate(self.x_test, self.y_test, verbose=0)
        
        # Store and log
        # self.run_manager.log_run(
        #     server_round=server_round,
        #     tag="server_evals",
        #     results_dict={"centralized_loss": loss, **accuracy},
        # )
        return loss, len(self.x_test), {"accuracy": accuracy}


def client_fn(context: Context):

    # Ensure a new session is started
    keras.backend.clear_session()
    # Load config and dataset of this ClientApp
    partition_id = context.node_config["partition-id"]
    num_partitions = context.node_config["num-partitions"]
    data = load_data(partition_id, num_partitions)

    # Return Client instance
    # We pass the state to persist information across
    # participation rounds. =
    client_state = context.state
    return FlowerClient(client_state, data, context.run_config).to_client()


# Flower ClientApp
app = ClientApp(
    client_fn,
)
