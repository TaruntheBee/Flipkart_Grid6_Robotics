import easyocr
import cv2
import os
import numpy as np
import time
import warnings

warnings.filterwarnings("ignore", category=FutureWarning)
IMAGE_FOLDER = r'C:\Users\hacke\OneDrive\Documents\programming files\flipkart_detect\images'
reader = easyocr.Reader(['en'], gpu=True)

def process_image(image_path):
    img_o=cv2.imread(image_path)
    w, h = 960, 1280
    sh_kernel = np.array([[0, -1, 0],[-1, 5, -1],[0, -1, 0]])
    img = cv2.filter2D(img_o, -1, sh_kernel)
    gray=cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    blur=cv2.GaussianBlur(gray,(5,5),1)
    canny=cv2.Canny(blur,190,190)
    contours,_=cv2.findContours(canny,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    contour_draw=img.copy()
    contour_draw=cv2.drawContours(contour_draw,contours,-1,(255,0,255),4)
    CornerFrame = img.copy()
    result = reader.readtext(blur)
    return img, result

start_time = time.time()
for idx, image_file in enumerate(os.listdir(IMAGE_FOLDER)):
    image_path = os.path.join(IMAGE_FOLDER, image_file)
    
    if image_file.lower().endswith(('.png', '.jpg', '.jpeg')):
        img, result = process_image(image_path)
 
        if result:
            for detection in result:
                top_left = tuple(map(int, detection[0][0]))
                bottom_right = tuple(map(int, detection[0][2]))
                text = detection[1]
                font = cv2.FONT_HERSHEY_SIMPLEX
                img = cv2.rectangle(img, top_left, bottom_right, (0, 255, 0), 3)
                img = cv2.putText(img, text, (top_left[0], top_left[1] - 10), font, 1, (0, 255, 0), 2, cv2.LINE_AA)

            print(f"Image {idx + 1} ({image_file}) contains text:")
            for detection in result:
                print(f"{detection[1]}")
            scale_percent = 50 
            width = int(img.shape[1] * scale_percent / 100)
            height = int(img.shape[0] * scale_percent / 100)
            resized_img = cv2.resize(img, (width, height), interpolation=cv2.INTER_AREA)
            
            cv2.imshow(f"Image {idx + 1}", resized_img)
           
end_time = time.time()
print(f"Processed all images in {end_time - start_time:.2f} seconds.")
cv2.waitKey(0)
