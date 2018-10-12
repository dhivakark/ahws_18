import cv2
import numpy as np

def resize_image(img, size, padding=255):
    '''
    Resize the given image to specified size
    Inputs:
        img = Image to be resized (Numpy NDArray)
        size = Scalar value. Image will be resized to (size, size)
    Returns:
        reszd_img = Resized image (Numpy NDArray)
    '''
    # Append zeros or ones based on the choice of padding
    # to maintain the aspect ratio of the image
    rows, cols = img.shape[:2]
    max_size = max(rows, cols)
    canvas = np.ones((max_size, max_size), np.uint8) * padding
    
    # Place the actual image at the center of the canvas
    c_x, c_y = max_size / 2, max_size / 2
    x_beg = max(0, int(c_x - (cols / 2)))
    y_beg = max(0, int(c_y - (rows / 2)))
    x_end, y_end = x_beg + cols, y_beg + rows
    print(y_beg, x_beg, x_beg, x_end)
    canvas[y_beg: y_end, x_beg: x_end] = img
        
    # Resize the image and write to op_dir_path specified
    #reszd_img = transform.resize(canvas, (size, size))
    reszd_img = cv2.resize(canvas, (size, size))
    reszd_img = np.asarray(reszd_img, np.uint8)
    # reszd_img = np.asarray(reszd_img * 255, np.uint8)
    return reszd_img

def extract_features(image):
    '''
    Extract the features from the Image
    '''
    if(len(image.shape) == 3):
      gray_img = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray_img = resize_image(gray_img, 250)
    gray_img = cv2.GaussianBlur(gray_img, (5, 5), 0)
    
    # Binarize the image using Adaptive thresholding
    th, bin_img = cv2.threshold(gray_img, 250, 255, cv2.THRESH_BINARY_INV)
    
    # Close the holes by Morphological operations (Erosion and Dilation)
    struct_elem = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    smooth_bin_img = cv2.erode(bin_img, struct_elem, iterations=1)
    smooth_bin_img = cv2.dilate(smooth_bin_img, struct_elem, iterations=2)
    
    # Find all the contours from the binary image
    img, contours, heirarchy = cv2.findContours(smooth_bin_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Find the circularity
    x, y, w, h = cv2.boundingRect(contours[0])
    rect_area = w * h
    contour_area = cv2.contourArea(contours[0])
    circularity = contour_area / rect_area
    
    # Find the compactness
    mask_img = np.zeros_like(smooth_bin_img)
    mask_img = cv2.drawContours(mask_img, [contours[0]], -1, 255, -1)
    white_mask_img = cv2.bitwise_and(smooth_bin_img, smooth_bin_img, mask=mask_img)
    white_area = cv2.countNonZero(white_mask_img)
    compactness = white_area / contour_area
    
    features = [circularity, compactness]
    
    return features

def predict_for_given_image(image):

    svm = cv2.ml.SVM_load('./dnn_in_nuera/svm_data.dat')
    image_features = np.array(extract_features(image), dtype=np.float32).reshape(1,-1)
    _, result = svm.predict(image_features)
    result = 'nuts' if result == 0 else 'bolts'
    row, column,_  = image.shape
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(image,result,(row // 2, column // 2), font, 4,(255,0,0),2,cv2.LINE_AA)
    return image

if __name__ == '__main__':
   test_image = cv2.imread('./test.jpg')
   output_image = predict_for_given_image(test_image)
   cv2.imshow('output', output_image)
   cv2.waitKey(0)
