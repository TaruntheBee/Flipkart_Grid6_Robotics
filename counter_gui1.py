import cv2
import easyocr
import numpy as np
import tkinter as tk
from PIL import Image, ImageTk
import threading
import warnings
import serial  # For reading from Arduino
import json

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
ir_counter = 0  # To store the counter value from Arduino
ir_data = {}
ir_state = 0

# Variables to control video capture
running = False
cap = None
arduino = serial.Serial('COM3', 9600, timeout=1)  # Replace 'COM3' with your port

# Function to extract text details
def extract_text_details(results):
    global company_name, product_name, mrp, quantity, other_details

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

# Function to update IR counter from Arduino in the GUI
def update_ir_counter():
    global ir_counter, ir_data, ir_state
    try:
        arduino_data = arduino.readline().decode().strip()  # Read data from Arduino
        # print(arduino_data)
        ir_data = json.loads(arduino_data)
        print(ir_data)
        if arduino_data:
            ir_data = json.loads(arduino_data)  # Convert to integer
            # print(ir_data)
            ir_counter = ir_data["count"]
            ir_state = ir_data["state"]
            ir_counter_label.config(text=f"IR Counter: {ir_counter}")  # Update the label
    except:
        pass

    # Keep reading the counter every 500 ms
    ir_counter_label.after(50, update_ir_counter)

# Function to start the camera
def start_camera():
    global running, cap
    if not running:
        running = True
        cap = cv2.VideoCapture(1)
        process_frame()

# Function to stop the camera
def stop_camera():
    global running, cap
    running = False
    if cap is not None:
        cap.release()
    camera_label.config(image='')  # Clear the camera feed display

# Function to process frames in a separate thread
def process_frame():
    global running, cap

    if running and cap is not None:
        ret, frame = cap.read()
        if ret:
            # Resize frame to 640x480
            frame_resized = cv2.resize(frame, (640, 480))

            # Convert to grayscale
            gray_frame = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2GRAY)

            # Perform OCR using EasyOCR with allowlist
            results = reader.readtext(gray_frame, allowlist='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789:;,."[]_-+=()*&^%$#@!|/?')

            # Extract text details
            extract_text_details(results)

            # Draw bounding boxes around detected text
            for (bbox, text, prob) in results:
                top_left = tuple(map(int, bbox[0]))
                bottom_right = tuple(map(int, bbox[2]))
                cv2.rectangle(frame_resized, top_left, bottom_right, (0, 255, 0), 2)

            # Convert frame to an image for Tkinter
            frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame_rgb)
            imgtk = ImageTk.PhotoImage(image=img)

            # Display the camera frame
            camera_label.imgtk = imgtk
            camera_label.config(image=imgtk)

            # Schedule the next frame
            camera_label.after(10, process_frame)
        else:
            stop_camera()

# Initialize Tkinter GUI
root = tk.Tk()
root.title("Camera Feed and IR Counter")
root.geometry("1280x720")  # Set the GUI window size to 720p

# Video frame on the left
camera_label = tk.Label(root)
camera_label.place(x=10, y=10)

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

# IR Counter label
ir_counter_label = tk.Label(root, text="IR Counter: 0", font=("Arial", 16), fg="blue")
ir_counter_label.place(x=660, y=550)

# Start and Stop buttons
start_button = tk.Button(root, text="Start Camera", command=start_camera)
start_button.place(x=660, y=620)

stop_button = tk.Button(root, text="Stop Camera", command=stop_camera)
stop_button.place(x=780, y=620)

# Start Tkinter event loop and IR counter update
update_ir_counter()  # Start the Arduino counter update
print(ir_data)
root.mainloop()
