# Import required packages
import cv2
import pytesseract
import numpy as np

# Mention the installed location of Tesseract-OCR in your system
pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract'  # In case using colab after installing above modules

# Read image from which text needs to be extracted
img = cv2.imread(r"C:\Users\hacke\OneDrive\Documents\programming files\flipkart_detect\images\photo_2024-09-16_17-03-01.jpg")

# Preprocessing the image starts

# Convert the image to gray scale
# gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

print(img)

sh_kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
sharpened = cv2.filter2D(img, -1, sh_kernel)

blur = cv2.GaussianBlur(sharpened, (3, 3), 0)

kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))

opening = cv2.morphologyEx(blur, cv2.MORPH_OPEN, kernel, iterations=1)
invert = 255 - opening

data = pytesseract.image_to_string(invert, lang="eng", config="--psm 6 --dpi 300")
print(data)

canny=cv2.Canny(blur,200,200)

cv2.imshow("original", img)
cv2.imshow("sharpned", sharpened)
cv2.imshow("gaussian blur", blur)
cv2.imshow("canny edge", canny)
cv2.waitKey(0)


