"""tensorflow-example: A Flower / Tensorflow app."""

import json
from logging import INFO

import wandb
from tf_federation.task import create_run_dir, load_model

from flwr.common import logger, parameters_to_ndarrays
from flwr.common.typing import UserConfig
from flwr.server.strategy import FedAvg

PROJECT_NAME = "FLOWER-advanced-tensorflow"


class CustomFedAvg(FedAvg):
    """A class that behaves like FedAvg but has extra functionality.

    This strategy: (1) saves results to the filesystem, (2) saves a
    checkpoint of the global  model when a new best is found, (3) logs
    results to W&B if enabled.
    """

    def __init__(self, run_config: UserConfig, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.run_config = run_config
        self.save_path, self.run_dir = create_run_dir(run_config)
        
        # Initialise W&B if set
        self.use_wandb = run_config.get("use-wandb", False)
        if self.use_wandb:
            self._init_wandb_project()

        # Keep track of best acc
        self.best_acc_so_far = 0.0

        # A dictionary to store results as they come
        self.results = {}
        self.model = load_model(run_config)

    def _init_wandb_project(self):
        wandb.init(project=self.run_config["project-name"], 
                   name=f"{str(self.run_dir)}-ServerApp")

    def _store_results(self, tag: str, results_dict):
        """Store results in dictionary, then save as JSON."""
        # Update results dict
        if tag in self.results:
            self.results[tag].append(results_dict)
        else:
            self.results[tag] = [results_dict]

        # Save results to disk.
        # Note we overwrite the same file with each call to this function.
        # While this works, a more sophisticated approach is preferred
        # in situations where the contents to be saved are larger.
        with open(f"{self.save_path}/results.json", "w", encoding="utf-8") as fp:
            json.dump(self.results, fp)

    def _update_best_acc(self, round, accuracy, parameters):
        """Determines if a new best global model has been found.

        If so, the model checkpoint is saved to disk.
        """
        if accuracy > self.best_acc_so_far:
            self.best_acc_so_far = accuracy
            logger.log(INFO, "💡 New best global model found: %f", accuracy)
            # You could save the parameters object directly.
            # Instead we are going to apply them to a PyTorch
            # model and save the state dict.
            # Converts flwr.common.Parameters to ndarrays
            ndarrays = parameters_to_ndarrays(parameters)
            self.model.set_weights(ndarrays)

            # Save the Tensorflow model
            fn_w = (
                self.save_path
                / f"model_state_acc_{accuracy:.3f}_round_{round}.weights.h5"
            )
            self.model.save_weights(fn_w)

            fn_m = (
                self.save_path
                / f"model_state_acc_{accuracy:.3f}_round_{round}.h5"
            )
            self.model.save(fn_m)

            fn_e = (
                self.save_path
                / f"export/model_state_acc_{accuracy:.3f}_round_{round}"
            )
            self.model.export(fn_e)

    def store_results_and_log(self, server_round: int, tag: str, results_dict):
        """A helper method that stores results and logs them to W&B if enabled."""
        # Store results
        self._store_results(
            tag=tag,
            results_dict={"round": server_round, **results_dict},
        )

        if self.use_wandb:
            # Log centralized loss and metrics to W&B
            wandb.log(results_dict, step=server_round)

    def evaluate(self, server_round, parameters):
        """Run centralized evaluation if callback was passed to strategy init."""
        loss, metrics = super().evaluate(server_round, parameters)

        # Save model if new best central accuracy is found
        self._update_best_acc(server_round, metrics["centralized_accuracy"], parameters)

        # Store and log
        self.store_results_and_log(
            server_round=server_round,
            tag="centralized_evaluate",
            results_dict={"centralized_loss": loss, **metrics},
        )
        return loss, metrics

    def aggregate_evaluate(self, server_round, results, failures):
        """Aggregate results from federated evaluation."""
        loss, metrics = super().aggregate_evaluate(server_round, results, failures)

        # Store and log
        self.store_results_and_log(
            server_round=server_round,
            tag="federated_evaluate",
            results_dict={"federated_evaluate_loss": loss, **metrics},
        )
        return loss, metrics
