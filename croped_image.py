import cv2 
import pytesseract # type: ignore
import numpy as np

# Mention the installed location of Tesseract-OCR in your system
pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract'

def drawRec(biggestNew, mainFrame):
        cv2.line(mainFrame, (biggestNew[0][0][0], biggestNew[0][0][1]), (biggestNew[1][0][0], biggestNew[1][0][1]), (0, 255, 0), 20)
        cv2.line(mainFrame, (biggestNew[0][0][0], biggestNew[0][0][1]), (biggestNew[2][0][0], biggestNew[2][0][1]), (0, 255, 0), 20)
        cv2.line(mainFrame, (biggestNew[3][0][0], biggestNew[3][0][1]), (biggestNew[2][0][0], biggestNew[2][0][1]), (0, 255, 0), 20)
        cv2.line(mainFrame, (biggestNew[3][0][0], biggestNew[3][0][1]), (biggestNew[1][0][0], biggestNew[1][0][1]), (0, 255, 0), 20)

img_o=cv2.imread(r"C:\Users\hacke\OneDrive\Documents\programming files\flipkart_detect\images\photo_2024-09-12_14-38-49.jpg")
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

maxArea = 0
biggest = []
for i in contours :
    area = cv2.contourArea(i)
    if area > 500 :
        peri = cv2.arcLength(i, True)
        edges = cv2.approxPolyDP(i, 0.02*peri, True)
        if area > maxArea and len(edges) == 4 :
            biggest = edges
            maxArea = area
if len(biggest) != 0 :
    biggest = biggest.reshape((4, 2))
    biggestNew = np.zeros((4, 1, 2), dtype= np.int32)
    add = biggest.sum(1)
    biggestNew[0] = biggest[np.argmin(add)]
    biggestNew[3] = biggest[np.argmax(add)]
    dif = np.diff(biggest, axis = 1)
    biggestNew[1] = biggest[np.argmin(dif)]
    biggestNew[2] = biggest[np.argmax(dif)]
    drawRec(biggestNew, CornerFrame)
    CornerFrame = cv2.drawContours(CornerFrame, biggestNew, -1, (255, 0, 255), 25)
    pts1 = np.float32(biggestNew)
    pts2 = np.float32([[0, 0], [w, 0], [0, h], [w, h]])
    matrix = cv2.getPerspectiveTransform(pts1, pts2)
    imgWarp = cv2.warpPerspective(img, matrix, (w, h))

cv2.imshow("original", img)
cv2.imshow("gray image", gray)
cv2.imshow("gaussian blur", blur)
cv2.imshow("canny edge", canny)
cv2.imshow("contour", contour_draw)
cv2.imshow("corner", CornerFrame)
cv2.imshow("outputImage", imgWarp)

invert = 255 - imgWarp

data = pytesseract.image_to_string(invert, lang="eng", config="--psm 6 --dpi 300")
print(data)

# Anti-sharpening kernel to counteract the previous sharpening
# inverse_sh_kernel = np.array([[0, 1, 0],[1, -5, 1],[0, 1, 0]])
# # inverse = 255 - imgWarp

# # Apply the inverse filter
# unsharpened_img = cv2.filter2D(imgWarp, -1, inverse_sh_kernel)
# cv2.imshow("output unsharped Image", unsharpened_img)

cv2.waitKey(0)