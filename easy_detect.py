import easyocr
import cv2
from matplotlib import pyplot as plt
import numpy as np

IMAGE_PATH = r'C:\Users\hacke\OneDrive\Documents\programming files\flipkart_detect\images\IMG_20240913_142347.jpg'

img_o=cv2.imread(IMAGE_PATH)
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

reader = easyocr.Reader(['en'])
result = reader.readtext(CornerFrame)
result

top_left = tuple(result[0][0][0])
bottom_right = tuple(result[0][0][2])
text = result[0][1]
font = cv2.FONT_HERSHEY_SIMPLEX

img = cv2.imread(IMAGE_PATH)
spacer = 100
for detection in result: 
    top_left = tuple(map(int, detection[0][0]))
    bottom_right = tuple(map(int, detection[0][2]))

    # Ensure the coordinates are within image bounds
    top_left = (min(max(top_left[0], 0), img.shape[1] - 1), min(max(top_left[1], 0), img.shape[0] - 1))
    bottom_right = (min(max(bottom_right[0], 0), img.shape[1] - 1), min(max(bottom_right[1], 0), img.shape[0] - 1))
    
    text = detection[1]
    print(text)
    img = cv2.rectangle(img,top_left,bottom_right,(0,255,0),3)
    img = cv2.putText(img,text,(20,spacer), font, 2,(0,255,0),3,cv2.LINE_AA)
    spacer+=15

# Resize images for display
def resize_image(image, scale_percent):
    width = int(image.shape[1] * scale_percent / 100)
    height = int(image.shape[0] * scale_percent / 100)
    return cv2.resize(image, (width, height), interpolation=cv2.INTER_AREA)

scale_percent = 20  # Adjust scale percentage
img_resized = resize_image(img, scale_percent)
gray_resized = resize_image(gray, scale_percent)
blur_resized = resize_image(blur, scale_percent)
canny_resized = resize_image(canny, scale_percent)
contour_draw_resized = resize_image(contour_draw, scale_percent)
CornerFrame_resized = resize_image(CornerFrame, scale_percent)

# Display resized images
cv2.imshow("Original", img_resized)
cv2.imshow("Gray Image", gray_resized)
cv2.imshow("Gaussian Blur", blur_resized)
cv2.imshow("Canny Edge", canny_resized)
cv2.imshow("Contour", contour_draw_resized)
cv2.imshow("Corner", CornerFrame_resized)
cv2.imshow("Output Image", img_resized)


# cv2.imshow("original", img)
# cv2.imshow("gray image", gray)
# cv2.imshow("gaussian blur", blur)
# cv2.imshow("canny edge", canny)
# cv2.imshow("contour", contour_draw)
# cv2.imshow("corner", CornerFrame)
# cv2.imshow("outputImage", img)

# plt.imshow(img)
# plt.show()
cv2.waitKey(0)