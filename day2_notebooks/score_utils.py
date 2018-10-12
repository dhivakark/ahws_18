'''
@Harsha
All loss definitions and other statistical measures defined here
Losses:
    1. earth_mover_loss : loss defined in NIMA github repo
    2. root_mean_squared_loss
    3. weighted_l2 : experimental loss definitions which we formulated
    4. weighted_l1

Scores:
    1. std_score : calculates standard deviation of a score distribution
    2. mean_sore : calcultes mean of a score distribution
'''

import numpy as np
from keras import backend as K
import tensorflow as tf


# ********** Error/Score Fn definitions *************************
def earth_mover_loss(y_true, y_pred):
  '''
  Inputs:

  Outputs:
  '''
  cdf_ytrue = K.cumsum(y_true, axis=-1)
  cdf_ypred = K.cumsum(y_pred, axis=-1)
  samplewise_emd = K.sqrt(K.mean(K.square(K.abs(cdf_ytrue - cdf_ypred)), axis=-1))
  return K.mean(samplewise_emd)


def root_mean_squared_error(y_true, y_pred):
  '''
  Inputs:

  Outputs:
  '''
  return K.sqrt(K.mean(K.square(y_pred - y_true), axis=-1))


def weighted_l2(y_true, y_pred):
    '''
    Manual loss
    '''
    # shape = y_true.shape.as_list()
    shape = 5
    y_true_weighted = tf.multiply(y_true, tf.range(1.0, float(shape+1), 1.0))
    max_idx = tf.cast(tf.round(tf.reduce_sum(y_true_weighted)), tf.int32) - 1

    #si = tf.slice(kern, [4-max_idx], [5])
    si = tf.cast(tf.stack([abs(itr - max_idx)+1 for itr in range(shape)]), tf.float32)
    dif = y_true - y_pred  # vectors
    sco = dif * si
    return K.square(sco)


def weighted_l1(y_true, y_pred):
    '''
    Manual loss 
    '''
    kern = np.append(np.arange(4, 0, -1), np.arange(0, 5, 1))
    # substract to use with si
    max_idx = round(sum(y_true * np.arange(1, 6, 1))) - 1 
    si = kern[4-max_idx: 9-max_idx]
    dif = y_true - y_pred  # vectors
    sco = dif * si
    return abs(sco)

# calculate standard deviation of scores for AVA dataset
def std_score(scores):
    si = np.arange(1, 6, 1)
    mean = mean_score(scores)
    std = np.sqrt(np.sum(((si - mean) ** 2) * scores))
    return std


def mean_score(scores):
  '''
  Inputs:

  Outputs:
  '''
  si = np.arange(1, len(scores)+1, 1)
  mean = np.sum(scores * si)
  return mean
