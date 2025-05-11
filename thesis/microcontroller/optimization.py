import os
os.environ["TF_USE_LEGACY_KERAS"] = "1" 

import tensorflow as tf
from tensorflow.keras import layers
from pathlib import Path
import numpy as np


path = "/Users/olenapleshan/data_analytics/assignments/thesis/federated_learning/outputs"
run_id = "development/20250309-172552"
model_id = "model_state_acc_0.848_round_2"

path =   f'{path}/{run_id}/export/export/{model_id}'
model = tf.keras.models.load_model(path)

# Convert the model to the TensorFlow Lite format without any optimizations
converter = tf.lite.TFLiteConverter.from_keras_model(model)
tflite_model = converter.convert()

Path(f"models/{run_id}").mkdir(parents=True, exist_ok=True)
with  open(f"models/{run_id}/{model_id}.tflite", "wb") as f:
    f.write(tflite_model)

# QUANTIZATION
# Dynamic range quantization
# https://ai.google.dev/edge/litert/models/post_training_quant
converter = tf.lite.TFLiteConverter.from_keras_model(model)
converter.optimizations = [tf.lite.Optimize.DEFAULT]
tflite_model = converter.convert()

# Save the quantized model
with open(f"models/{run_id}/dynamic_quant.{model_id}.tflite", "wb") as f:
    f.write(tflite_model)

#Post-training Integer Quantization
def representative_dataset():
    for _ in range(100):
        data = np.random.rand(1, 28, 28, 1)
        yield [data.astype(np.float32)]

converter = tf.lite.TFLiteConverter.from_keras_model(model)
converter.optimizations = [tf.lite.Optimize.DEFAULT]
converter.representative_dataset = representative_dataset
converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS_INT8]
converter.inference_input_type = tf.uint8
converter.inference_output_type = tf.uint8
tflite_model = converter.convert()

# Save the quantized model
with open(f"models/{run_id}/int_quant.{model_id}.tflite", "wb") as f:
    f.write(tflite_model)    
    

#import tensorflow_model_optimization as tfmot
    
# # Prune the model
# pruning_params = {
#     'pruning_schedule': tfmot.sparsity.keras.PolynomialDecay(initial_sparsity=0.0,
#                                                              final_sparsity=0.5,
#                                                              begin_step=0,
#                                                              end_step=1000)
# }

# pruned_model = tfmot.sparsity.keras.prune_low_magnitude(model, **pruning_params)

# # Compile and train the pruned model
# pruned_model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
# pruned_model.fit(train_data, train_labels, epochs=2)

# # Strip pruning wrappers
# model_for_export = tfmot.sparsity.keras.strip_pruning(pruned_model)

# # Convert to TensorFlow Lite
# converter = tf.lite.TFLiteConverter.from_keras_model(model_for_export)
# tflite_model = converter.convert()

# # Save the pruned model
# with open("models/development/20250309-172552/model_state_acc_0.848_round_2_pruned.tflite", "wb") as f:
#     f.write(tflite_model)

# # Cluster the model
# clustering_params = {
#     'number_of_clusters': 8,
#     'cluster_centroids_init': tfmot.clustering.keras.CentroidInitialization.KMEANS_PLUS_PLUS
# }

# clustered_model = tfmot.clustering.keras.cluster_weights(model, **clustering_params)

# # Compile and train the clustered model
# clustered_model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
# clustered_model.fit(train_data, train_labels, epochs=2)

# # Strip clustering wrappers
# model_for_export = tfmot.clustering.keras.strip_clustering(clustered_model)

# # Convert to TensorFlow Lite
# converter = tf.lite.TFLiteConverter.from_keras_model(model_for_export)
# tflite_model = converter.convert()

# # Save the clustered model
# with open("models/development/20250309-172552/model_state_acc_0.848_round_2_clustered.tflite", "wb") as f:
#     f.write(tflite_model)