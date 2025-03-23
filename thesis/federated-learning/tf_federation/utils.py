"""Storage functionality for saving TensorFlow models and weights."""

import json
import wandb
import os

from pathlib import Path
from keras import Model
from datetime import datetime
from pathlib import Path
from typing import Dict, Tuple
import tf_federation.properties as properties


class RunManager:
    """Handles saving TensorFlow models, weights, and exports."""

    def __init__(self, config: Dict[str, str]):
        """Initialize storage with a configuration dictionary.
        
        Args:
            config: A dictionary containing the configuration for the run.
                Expected keys:
                    - "run-identifier" (str): A unique identifier for the run.
        """
        self.save_path, self.run_dir = self._create_run_dir(config)
        
        self.results = {"server_evals": [], "federation_evals": []}

        # Initialise W&B if set
        self.use_wandb = config.get("use-wandb", False)
        if self.use_wandb:
            wandb.init(project=config["project-name"], 
                       name=f"experiment-{str(self.run_dir)}",
                       config={
                            "learning_rate": 0.001,
                            "architecture": "CNN",
                            "dataset": properties.dataset,
                            "epochs": int(config["num-server-rounds"]),  
                        },
                        # TODO  - change job type to server vs client 1,2 
                        job_type=os.environ.get(
                            'JOB_OWNER', 'server'
                        ))

    def _create_run_dir(self, config: Dict[str, str]) -> Tuple[Path, str]:
        """Create a directory to save results from this run.
        
        Args:
            config: A dictionary containing the configuration for the run.
        
        Returns:
            Tuple[Path, str]: A tuple containing the path to the created directory and the run identifier.
        """
        # Generate the run directory name using the run identifier and current timestamp
        run_identifier = config["run-identifier"]
        timestamp = datetime.now().strftime("%Y%m%d-%H%M")
        run_dir = f"{run_identifier}/{timestamp}"

        # Create the full path to the run directory
        save_path = Path.cwd() / f"outputs/{run_dir}/export"
        save_path.mkdir(parents=True, exist_ok=True)

        # Save the run configuration to a JSON file in the run directory
        config_path = save_path / "run_config.json"
        with open(config_path, "w", encoding="utf-8") as fp:
            json.dump(config, fp, indent=4)

        return save_path, run_dir

    def save_model(self, model: Model, accuracy: float, server_round: int) -> None:
        """Save the model weights, full model, and export format.
        
        Args:
            model: The TensorFlow model to save
            accuracy: Accuracy value to include in the filename
            server_round: Current server round
        """
        # Save model weights
        weights_path = self.save_path / f"model_state_acc_{accuracy:.3f}_round_{server_round}.weights.h5"
        model.save_weights(weights_path)
        print(f"Model weights saved to {weights_path}")

        # Save the full model
        model_path = self.save_path / f"model_state_acc_{accuracy:.3f}_round_{server_round}.h5"
        model.save(model_path)
        print(f"Full model saved to {model_path}")

        # Export the model
        export_path = self.save_path / f"model_state_acc_{accuracy:.3f}_round_{server_round}"
        model.export(export_path)
        print(f"Model exported to {export_path}")

        # Log to W&B if enabled
        # if self.use_wandb:
        #   wandb.log_model(model_path, "fed_model", aliases=[f"server_round_dropout-{round(wandb.config.dropout, 4)}"])
    
    def _store_results(self, tag: str, results_dict: Dict) -> None:
        """Store results in a dictionary and save them as JSON.
        
        Args:
            tag: A tag to categorize the results (e.g., "evaluation").
            results_dict: A dictionary containing the results to store.
        """
        # Update results dictionary
        if tag in self.results:
            self.results[tag].append(results_dict)
        else:
            self.results[tag] = [results_dict]

        # Save results to disk
        results_path = self.save_path / "results.json"
        with open(results_path, "w", encoding="utf-8") as fp:
            json.dump(self.results, fp, indent=4)

    def log_run(self, server_round: int, tag: str, results_dict: Dict) -> None:
        """Store results and log them to W&B if enabled.
        
        Args:
            server_round: The current server round.
            tag: A tag to categorize the results (e.g., "evaluation").
            results_dict: A dictionary containing the results to store and log.
        """
        # Update results dictionary
        if tag in self.results:
            self.results[tag].append(results_dict)
        else:
            self.results[tag] = [results_dict]

        # Save results to disk
        results_path = self.save_path / "results.json"
        with open(results_path, "w", encoding="utf-8") as fp:
            json.dump(self.results, fp, indent=4)

        # Log to W&B if enabled
        if self.use_wandb:
            wandb.log(results_dict, step=server_round)
