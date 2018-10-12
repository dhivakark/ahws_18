import cv2
import numpy as np 


def find_homography(img1, img2):
  """
  Utility to find homography between two images.
  """
  MIN_MATCH_COUNT = 10

  # Initiate ORB detector
  orb = cv2.ORB_create()

  # find the keypoints and descriptors with ORB
  kp1, des1 = orb.detectAndCompute(img1,None)
  kp2, des2 = orb.detectAndCompute(img2,None)
  #create BFMatcher object
  bf = cv2.BFMatcher(cv2.NORM_HAMMING)

  # Match descriptors.
  matches = bf.knnMatch(des1,des2,k=2)

  good = []
  for m,n in matches:
    if m.distance < 0.7*n.distance:
      good.append(m)
  if len(good)>MIN_MATCH_COUNT:
    src_pts = np.float32([ kp1[m.queryIdx].pt for m in good ]).reshape(-1,1,2)
    dst_pts = np.float32([ kp2[m.trainIdx].pt for m in good ]).reshape(-1,1,2)
    H, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC,5.0)
    return H
  print('Less no of matches')
  return []
