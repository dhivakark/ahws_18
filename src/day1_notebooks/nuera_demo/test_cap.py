import time
import cv2
import numpy as np

import camera_capture as cc
import dnn_in_nuera.nuera_nuts_and_bolts_inference_ml as nuera_ml
#import keras

def img_callback(img_data):
  '''
  '''
  ary = np.asarray(img_data['img'])
  rgb = cv2.imdecode(ary, 1)
  output_image = nuera_ml.predict_for_given_image(rgb)

  # cv2.imshow('t', rgb)
  cv2.imshow('output', output_image)
  cv2.waitKey(10)
  print(img_data['w'])
  return

 
dev = cc.CameraStreamer(img_callback, "192.168.1.201")
dev.start_capture()

while True:
    try:
        time.sleep(1)
    except KeyboardInterrupt as Err:
        dev.stop_capture()
        print("Capture closing")
        break

print("Capture Ended")
