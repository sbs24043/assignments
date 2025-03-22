import json
from logging import INFO

from tf_federation.task import create_run_dir, load_model

from flwr.common import logger, parameters_to_ndarrays
from flwr.common.typing import UserConfig
from flwr.server.strategy import FedAvg, Strategy
from tf_federation.storage import RunManager
from tf_federation.task import init_model

PROJECT_NAME = "flwr-edge-devices-custom-strategy"


# https://flower.ai/docs/framework/how-to-implement-strategies.html
class CustomStrategy(FedAvg):
    def __init__(self, run_config: UserConfig, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.run_config = run_config
        self.run_manager = RunManager(run_config)

        self.best_accuracy = 0.0
        self.model = init_model()

    # def initialize_parameters(self, client_manager):
    #     # Your implementation here
    #     pass

    # def configure_fit(self, server_round, parameters, client_manager):
    #     # Your implementation here
    #     pass

    # Maybe could put in the multiple strategies here
    # def aggregate_fit(self, server_round, results, failures):
    #     # Your implementation here
    #     pass

    # def configure_evaluate(self, server_round, parameters, client_manager):
    #     # Your implementation here
    #     pass

    def evaluate(self, server_round, parameters):
        """Run centralized evaluation if callback was passed to strategy init."""
        print("START CUSTOM DUMB SHIT IS CALLED!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        loss, metrics = super().evaluate(server_round, parameters)

        # Save model if new better central accuracy is found
        accuracy = metrics["server_accuracy"]
        if accuracy > self.best_accuracy:
            self.best_accuracy = accuracy
            logger.log(INFO, "Better accuracy achieved: %f", accuracy)
            self.model.set_weights(parameters_to_ndarrays(parameters))
            self.run_manager.save_model(self.model, accuracy, server_round)

        # Store and log
        self.run_manager.log_run(
            server_round=server_round,
            tag="server_evals",
            results_dict={"centralized_loss": loss, **metrics},
        )
        print("END CUSTOM DUMB SHIT IS CALLED!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
        return loss, metrics

    def aggregate_evaluate(self, server_round, results, failures):
        """Aggregate results from federated evaluation."""
        loss, metrics = super().aggregate_evaluate(server_round, results, failures)

        # Store and log
        self.run_manager.log_run(
            server_round=server_round,
            tag="federation_evals",
            results_dict={"federated_evaluate_loss": loss, **metrics},
        )
        return loss, metrics
