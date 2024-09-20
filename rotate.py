import cv2 

img=cv2.imread(r"C:\Users\hacke\OneDrive\Documents\programming files\flipkart_detect\photo_2024-09-12_14-38-49.jpg")
rotated_img=cv2.rotate(img,cv2.ROTATE_180)
cv2.imshow("image",rotated_img)
cv2.waitKey(0)