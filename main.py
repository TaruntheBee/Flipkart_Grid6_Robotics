import cv2
import easyocr


class Detector:
    def __init__(self, img_path):
        try:
            self.img_path = img_path
            self.img = cv2.imread(img_path)
            print(self.img)
        except Exception as e:
            print("Error: "+e)

    def showImg(self):
        cv2.imshow("image", self.img)

    def getText(self):
        reader = easyocr.Reader(['en'])
        result = reader.readtext(self.img_path, paragraph=False, weights_only=True)
        print(result)

if __name__ == "__main__":
    d = Detector(r"C:\Users\hacke\OneDrive\Documents\programming files\flipkart_detect\images\photo_2024-09-16_17-03-01.jpg")
    # d.showImg()
    d.getText()
 