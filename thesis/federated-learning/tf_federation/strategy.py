import json
from logging import INFO
from typing import Callable

from tf_federation.utils import RunManager
from tf_federation.task import init_model

from flwr.common import logger, parameters_to_ndarrays
from flwr.common.typing import UserConfig
from flwr.server.strategy import FedAvg, FedOpt, FedAdagrad, FedAdam, Strategy, FedMedian, FedAvgAndroid


# PROJECT_NAME = "flwr-edge-devices-custom-strategy"
# https://flower.ai/docs/framework/how-to-implement-strategies.html
# https://flower.ai/docs/framework/tutorial-series-build-a-strategy-from-scratch-pytorch.html
# https://flower.ai/docs/framework/how-to-use-strategies.html#customize-an-existing-strategy-with-callback-functions

class CustomStrategy(FedAvg):
    def __init__(self, run_config: UserConfig, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.run_config = run_config
        self.run_manager = RunManager(run_config)

        self.best_accuracy = 0.0
        self.model = init_model()

        self.strategies = [
            FedAdagrad(**kwargs),
            FedAdam(**kwargs),
            FedAvg(**kwargs),
            FedOpt(**kwargs),
            FedMedian(**kwargs),
        ]

    # def initialize_parameters(self, client_manager):
    #     # Your implementation here
    #     pass

    # def configure_fit(self, server_round, parameters, client_manager):
    #     # Your implementation here
    #     pass

    # Maybe could put in the multiple strategies here
    # each run returns parameters_aggregated, metrics_aggregated
    def aggregate_fit(self, server_round, results, failures):
        parameters_aggregated_list = []
        metrics_aggregated_list = []
        eval_results = []

        for pos, strategy in enumerate(self.strategies):
            logger.log(INFO, "Using aggregation strategy: %s", strategy.__class__.__name__)
            parameters_aggregated, metrics_aggregated = strategy.aggregate_fit(server_round, results, failures)
            parameters_aggregated_list.append(parameters_aggregated)
            metrics_aggregated_list.append(metrics_aggregated)

            logger.log(INFO, "Evaluating aggregation strategy: %s", strategy.__class__.__name__)
            loss, acc = self.evaluate_fn(server_round, parameters_to_ndarrays(parameters_aggregated), {})
            eval_results.append([pos, loss, acc])

        print("Results of evaluation with multiple strategies:", eval_results)
        best_result = min(eval_results, key=lambda x: (x[1], -x[2]["centralized_eval_accuracy"]))

        print("Best strategy for the round is:", self.strategies[best_result[0]])
        
        return parameters_aggregated_list[best_result[0]], metrics_aggregated_list[best_result[0]]

    # def configure_evaluate(self, server_round, parameters, client_manager):
    #     # Your implementation here
    #     pass

    def evaluate(self, server_round, parameters):
        """Run centralized evaluation if callback was passed to strategy init."""
        loss, metrics = super().evaluate(server_round, parameters)

        # Save model if new better central accuracy is found
        accuracy = metrics["centralized_eval_accuracy"]
        if accuracy > self.best_accuracy:
            logger.log(INFO, "Better accuracy achieved: %f", accuracy)
            logger.log(INFO, "Previous accuracy: %f", self.best_accuracy)
            self.best_accuracy = accuracy
            self.model.set_weights(parameters_to_ndarrays(parameters))
            self.run_manager.save_model(self.model, accuracy, server_round)

        # Store and log
        self.run_manager.log_run(
            server_round=server_round,
            tag="server_evals",
            results_dict={"centralized_eval_loss": loss, **metrics},
        )
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



class Baseline(FedAvg):
    def __init__(self, run_config: UserConfig, *args, **kwargs):
        super().__init__(*args, **kwargs)        
        self.run_manager = RunManager(run_config)

    def aggregate_evaluate(self, server_round, results, failures):
        """Aggregate results from federated evaluation."""
        loss, metrics = super().aggregate_evaluate(server_round, results, failures)
        # Store and log
        self.run_manager.log_run(
            server_round=server_round,
            tag="federation_evals",
            results_dict={"federated_evaluate_loss": loss, **metrics},
        )
        print("Baseline evaluation results: loss ", loss, " accuracy ", metrics)
        return loss, metrics