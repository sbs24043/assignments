1. Model to TFLite conversion
encountered multiple errors cased by issues with TFLite support for Keras3
Need to fall back to Keras 2

 Use `model.export(filepath)` if you want to export a SavedModel for use with TFLite/TFServing/etc

https://github.com/tensorflow/tensorflow/issues/64685