import easyocr
import cv2
import numpy as np
import warnings

warnings.filterwarnings("ignore", category=FutureWarning)

reader = easyocr.Reader(['en'], gpu=True)
def resize_image(image, width=None, height=None):
    if width is None and height is None:
        return image
    h, w = image.shape[:2]
    if width is None:
        ratio = height / float(h)
        dim = (int(w * ratio), height)
    else:
        ratio = width / float(w)
        dim = (width, int(h * ratio))
        return cv2.resize(image, dim, interpolation=cv2.INTER_AREA)

cap = cv2.VideoCapture(1)

if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

window_width = 800
window_height = 600

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Could not read frame.")
        break
    frame_resized = resize_image(frame, width=window_width, height=window_height)
    gray_frame = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2GRAY)
    # blur_frame = cv2.GaussianBlur(gray_frame, (5, 5), 0)
    # edges_frame = cv2.Canny(blur_frame, 190, 190)
    results = reader.readtext(gray_frame, allowlist='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789:;,."[]_-+=()*&^%$#@!|/?')

    for detection in results:
        top_left = tuple(map(int, detection[0][0]))
        bottom_right = tuple(map(int, detection[0][2]))
        text = detection[1]
        cv2.rectangle(frame_resized, top_left, bottom_right, (0, 255, 0), 2)
        cv2.putText(frame_resized, text, (top_left[0], top_left[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2, cv2.LINE_8)

    cv2.imshow('Webcam Text Detection', frame_resized)
    # cv2.imshow('Gray Image', gray_frame)
    # cv2.imshow('Gaussian Blur', blur_frame)
    # cv2.imshow('Canny Edge', edges_frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()
