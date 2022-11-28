import os
import numpy as np
import tensorflow as tf


converter = tf.lite.TFLiteConverter.from_saved_model("./") # path to the SavedModel directory
converter.target_spec.supported_ops = [tf.lite.OpsSet.TFLITE_BUILTINS, tf.lite.OpsSet.SELECT_TF_OPS]

converter.optimizations = [tf.lite.Optimize.OPTIMIZE_FOR_LATENCY]
tflite_model = converter.convert()


# write the model to a tflite file as binary file
tflite_no_quant_file =   "model.tflite"
with open(tflite_no_quant_file, "wb") as f:
    f.write(tflite_model)

