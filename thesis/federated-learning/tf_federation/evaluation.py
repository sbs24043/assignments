"""Evaluation functionality for federated learning."""

from typing import Callable, Dict, List, Tuple, Union, Any
import numpy as np

from tf_federation.task import load_model
from keras import Sequential


class Evaluation:
    """Handles model evaluation in federated learning context."""
    def __init__(self, model: Sequential, x_test: np.ndarray, y_test: np.ndarray):
        """Initialize evaluation with test data.
        
        Args:
            model: Keras model
            x_test: Test features
            y_test: Test labels
        """
        self.model = model
        self.x_test = x_test
        self.y_test = y_test
    
    def evaluate_model(
        self, 
        server_round: int, 
        parameters_ndarrays: List[np.ndarray], 
        config: Dict[str, Any]
    ) -> Tuple[float, Dict[str, float]]:
        """Evaluate global model on centralized test set.
        
        Args:
            server_round: Current server round
            parameters_ndarrays: Model parameters as list of numpy arrays
            config: Configuration parameters
            
        Returns:
            Tuple containing loss and metrics dictionary
        """
        self.model.set_weights(parameters_ndarrays)
        loss, accuracy = self.model.evaluate(self.x_test, self.y_test, verbose=0)
        return loss, {"server_accuracy": accuracy}
    
    def get_evaluate_fn(self) -> Callable:
        """Return the evaluation function to be used by the strategy.
        
        Returns:
            Callable function for model evaluation
        """
        return self.evaluate_model
    
    @staticmethod
    def weighted_average(metrics: List[Tuple[int, Dict[str, float]]]) -> Dict[str, float]:
        """Calculate weighted average of metrics across clients.
        
        Args:
            metrics: List of tuples containing number of examples and metrics dictionary
            
        Returns:
            Aggregated metrics dictionary
        """
        # Multiply accuracy of each client by number of examples used
        accuracies = [num_examples * m["accuracy"] for num_examples, m in metrics]
        examples = [num_examples for num_examples, _ in metrics]

        # Aggregate and return custom metric (weighted average)
        return {"federated_evaluate_accuracy": sum(accuracies) / sum(examples)}