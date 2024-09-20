import cv2
import easyocr
import numpy as np
import tkinter as tk
from PIL import Image, ImageTk
import threading
import warnings

# Suppress future warnings
warnings.filterwarnings("ignore", category=FutureWarning)

# Initialize EasyOCR reader
reader = easyocr.Reader(['en'])

# Global variables for storing product details
company_name = ""
product_name = ""
mrp = ""
quantity = ""
other_details = []

# Function to extract text details
def extract_text_details(frame):
    global company_name, product_name, mrp, quantity, other_details

    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    results = reader.readtext(gray_frame, allowlist='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789:;,."[]_-+=()*&^%$#@!|/?')

    # Sort detected text boxes by height to identify largest fonts
    results = sorted(results, key=lambda x: abs(x[0][0][1] - x[0][2][1]), reverse=True)

    # Detect company name and product name if not already detected
    if len(results) > 0 and not company_name:
        company_name = results[0][1]

    if len(results) > 1 and not product_name:
        product_name = results[1][1]

    # Extract MRP and other details
    for (bbox, text, prob) in results:
        if 'mrp' in text.lower() and not mrp:
            mrp = text
        elif 'quantity' in text.lower() and not quantity:
            quantity = text
        elif text not in [company_name, product_name, mrp, quantity]:
            other_details.append(text)

    # Update the GUI with extracted details
    update_product_details()

# Function to update product details in the GUI
def update_product_details():
    company_name_label.config(text=f"Company Name: {company_name}")
    product_name_label.config(text=f"Product Name: {product_name}")
    mrp_label.config(text=f"MRP: {mrp}")
    quantity_label.config(text=f"Quantity: {quantity}")

    # Update other details label
    other_details_text = '\n'.join(other_details)
    other_details_label.config(text=f"Other Details:\n{other_details_text}")

# Function to start video capture
def start_video():
    cap = cv2.VideoCapture(1)
    # cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    # cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    def process_video():
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            # Extract text details from frame
            extract_text_details(frame)

            # Draw bounding boxes around detected text
            for (bbox, text, prob) in reader.readtext(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)):
                top_left = tuple(map(int, bbox[0]))
                bottom_right = tuple(map(int, bbox[2]))
                cv2.rectangle(frame, top_left, bottom_right, (0, 255, 0), 2)
                cv2.putText(frame, text, (top_left[0], top_left[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # Resize frame for GUI display (640x480)
            display_frame = cv2.resize(frame, (640, 480))

            # Convert frame to Tkinter compatible format
            img = Image.fromarray(cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB))
            imgtk = ImageTk.PhotoImage(image=img)

            # Update the video label in the GUI
            video_label.imgtk = imgtk
            video_label.config(image=imgtk)

        cap.release()

    threading.Thread(target=process_video).start()

# Function to stop video capture
def stop_video():
    root.quit()

# Initialize Tkinter GUI
root = tk.Tk()
root.title("Camera Feed")
root.geometry("1280x720")  # Set the GUI window size to 720p

# Video frame on the left
video_label = tk.Label(root)
video_label.place(x=10, y=10)

# Product details section
product_details_frame = tk.Frame(root)
product_details_frame.place(x=660, y=10, width=600, height=500)  # Adjust position and size

product_details_label = tk.Label(product_details_frame, text="Product Details", font=("Arial", 14))
product_details_label.pack(anchor='w', padx=10, pady=5)

company_name_label = tk.Label(product_details_frame, text="Company Name: ", font=("Arial", 12))
company_name_label.pack(anchor='w', padx=10, pady=5)

product_name_label = tk.Label(product_details_frame, text="Product Name: ", font=("Arial", 12))
product_name_label.pack(anchor='w', padx=10, pady=5)

mrp_label = tk.Label(product_details_frame, text="MRP: ", font=("Arial", 12))
mrp_label.pack(anchor='w', padx=10, pady=5)

quantity_label = tk.Label(product_details_frame, text="Quantity: ", font=("Arial", 12))
quantity_label.pack(anchor='w', padx=10, pady=5)

other_details_label = tk.Label(product_details_frame, text="Other Details: ", font=("Arial", 12), justify="left")
other_details_label.pack(anchor='w', padx=10, pady=5)

# Start and Stop buttons
start_button = tk.Button(root, text="Start", command=start_video)
start_button.place(x=660, y=520)

stop_button = tk.Button(root, text="Stop", command=stop_video)
stop_button.place(x=740, y=520)

# Start Tkinter event loop
root.mainloop()
