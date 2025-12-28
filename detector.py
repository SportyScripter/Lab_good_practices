import cv2
import numpy as np
import requests

def count_people_on_image(url):
    try:
        response = requests.get(url)
        if response.status_code != 200:
            print("Failed to retrieve image from URL.")
            return 0
        
        image_array = np.asarray(bytearray(response.content), dtype=np.uint8)
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
        
        hog = cv2.HOGDescriptor()
        hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
        
        boxes, weights = hog.detectMultiScale(image, winStride=(8,8))
        return len(boxes)
    except Exception as e:
        print(f"An error occurred: {e}")
        return 0