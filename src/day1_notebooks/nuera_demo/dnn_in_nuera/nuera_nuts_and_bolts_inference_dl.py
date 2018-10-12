#from keras.models import model_from_json
import cv2
#from keras import backend as K
#import tensorflow as tf


# def freeze_session(session, keep_var_names=None, output_names=None, clear_devices=True):
#     """
#     Freezes the state of a session into a pruned computation graph.
# 
#     Creates a new computation graph where variable nodes are replaced by
#     constants taking their current value in the session. The new graph will be
#     pruned so subgraphs that are not necessary to compute the requested
#     outputs are removed.
#     @param session The TensorFlow session to be frozen.
#     @param keep_var_names A list of variable names that should not be frozen,
#                           or None to freeze all the variables in the graph.
#     @param output_names Names of the relevant graph outputs.
#     @param clear_devices Remove the device directives from the graph for better portability.
#     @return The frozen graph definition.
#     """
#     from tensorflow.python.framework.graph_util import convert_variables_to_constants
#     graph = session.graph
#     with graph.as_default():
#         freeze_var_names = list(set(v.op.name for v in tf.global_variables()).difference(keep_var_names or []))
#         output_names = output_names or []
#         output_names += [v.op.name for v in tf.global_variables()]
#         input_graph_def = graph.as_graph_def()
#         if clear_devices:
#             for node in input_graph_def.node:
#                 node.device = ""
#         frozen_graph = convert_variables_to_constants(session, input_graph_def,
#                                                       output_names, freeze_var_names)
#         return frozen_graph
# 
# json_file = open('../models/nuts_and_bolts_dl.json', 'r')
# nuts_and_bolts_json = json_file.read()
# json_file.close()
# nuts_and_bolts_model = model_from_json(nuts_and_bolts_json)
# # load weights into new model
# nuts_and_bolts_model.load_weights("../models/nuts_and_bolts.h5")
# print("Loaded model from disk")

# frozen_graph = freeze_session(K.get_session(),
#                               output_names=[out.op.name for out in nuts_and_bolts_model.outputs])
# tf.train.write_graph(frozen_graph, "../models", "my_model.pb", as_text=False)





image = cv2.imread('./test.jpg')
resized_image = cv2.resize(image, (50,65)).reshape(1,50,65,3)
#print(nuts_and_bolts_model.predict(resized_image))

nuts_and_bolts_model = cv2.dnn.readNetFromTensorflow('./my_model.pb')
nuts_and_bolts_model.setInput(resized_image)
pred = nuts_and_bolts_model.forward()
print(pred)
