import cv2
import easyocr
import numpy as np
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import warnings
import serial  # For reading from Arduino
import json
import threading
from difflib import SequenceMatcher

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

# Product catalog (with added expiry field and count)
catalog = [
    {"comp_name": "kinley", "prod_name": "water bottle", "mrp": 20, "expiry": "2025-12", "count": 0},
    {"comp_name": "nestle", "prod_name": "kitkat", "mrp": 20, "expiry": "2024-06", "count": 0},
    {"comp_name": "Best Web Cam Company", "prod_name": "web cam", "mrp": 900, "expiry": "2026-03", "count": 0}
]

# Function to reset the product details
def reset_product_details():
    global company_name, product_name, mrp, quantity, other_details
    company_name = ""
    product_name = ""
    mrp = ""
    quantity = ""
    other_details = []

# Function to match product based on detected text
def match_product(text):
    global catalog
    matched_item = None
    highest_ratio = 0

    # Loop through catalog and match with partial names
    for item in catalog:
        # Use SequenceMatcher to match product names or company names
        prod_ratio = SequenceMatcher(None, text.lower(), item["prod_name"].lower()).ratio()
        comp_ratio = SequenceMatcher(None, text.lower(), item["comp_name"].lower()).ratio()
        max_ratio = max(prod_ratio, comp_ratio)

        # Debug print to check matching
        # print(f"Matching '{text}' with '{item['prod_name']}' and '{item['comp_name']}' - Ratio: {max_ratio}")

        # If there's a good match, select that product
        if max_ratio > highest_ratio and max_ratio > 0.5:  # Set a threshold for matching
            highest_ratio = max_ratio
            matched_item = item

    return matched_item

# Function to extract text details
def extract_text_details(results):
    global company_name, product_name, mrp, quantity, other_details, catalog

    # Sort detected text boxes by height to identify largest fonts
    results = sorted(results, key=lambda x: abs(x[0][0][1] - x[0][2][1]), reverse=True)

    # Reset the product details for each new detection
    reset_product_details()

    # Detect company name and product name if not already detected
    if len(results) > 0 and not company_name:
        company_name = results[0][1].lower()

    if len(results) > 1 and not product_name:
        product_name = results[1][1].lower()

    # print(f"Detected Company Name: {company_name}, Product Name: {product_name}")

    matched_item = match_product(company_name) or match_product(product_name)
    if matched_item:
        # print(f"Matched Product: {matched_item}")
        company_name = matched_item['comp_name']
        product_name = matched_item['prod_name']
        mrp = matched_item['mrp']
        matched_item['count'] += 1  # Increment count of the matched item

        # Update the GUI with extracted details
        update_product_details(matched_item)

# Function to update product details in the GUI
def update_product_details(item=None):
    if item:
        # print(f"Updating GUI with: {item}")
        company_name_label.config(text=f"Company Name: {item['comp_name']}")
        product_name_label.config(text=f"Product Name: {item['prod_name']}")
        mrp_label.config(text=f"MRP: {item['mrp']}")
        count_label.config(text=f"Count: {item['count']}")
    else:
        company_name_label.config(text="Company Name: ")
        product_name_label.config(text="Product Name: ")
        mrp_label.config(text="MRP: ")
        count_label.config(text="Count: ")

# Function to update IR counter from Arduino in the GUI
def update_ir_counter():
    global ir_counter, ir_data, ir_state
    try:
        arduino_data = arduino.readline().decode().strip()  # Read data from Arduino
        ir_data = json.loads(arduino_data)
        if arduino_data:
            ir_data = json.loads(arduino_data)  # Convert to integer
            ir_counter = ir_data["count"]
            ir_state = ir_data["state"]
            ir_counter_label.config(text=f"IR Counter: {ir_counter}")  # Update the label
    except:
        pass

    # Keep reading the counter every 500 ms
    ir_counter_label.after(10, update_ir_counter)

# Function to start the camera
def start_camera():
    global running, cap
    if not running:
        running = True
        cap = cv2.VideoCapture(1)
        # Start the camera processing in a separate thread
        threading.Thread(target=process_frame, daemon=False).start()  # Asynchronous call
        # Start updating the IR counter
        update_ir_counter()
        # process_frame()

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

    while running and cap is not None:
        ret, frame = cap.read()
        if ret:
            # Resize frame to 640x480
            frame_resized = cv2.resize(frame, (640, 480))

            # Convert to grayscale
            gray_frame = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2GRAY)

            # Perform OCR using EasyOCR with allowlist
            results = reader.readtext(gray_frame, allowlist='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789:;,."[]_-+=()*&^%$#@!|/?')

            # Debugging: Print OCR results
            # print(f"OCR Results: {results}")

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
            # camera_label.after(10, process_frame)
        else:
            stop_camera()

# Function to display catalog in a new window (only for detected items)
def show_catalog():
    catalog_window = tk.Toplevel(root)
    catalog_window.title("Product Catalog")

    tree = ttk.Treeview(catalog_window, columns=("Company", "Product", "MRP", "Expiry", "Count"), show="headings")
    tree.heading("Company", text="Company")
    tree.heading("Product", text="Product")
    tree.heading("MRP", text="MRP")
    tree.heading("Expiry", text="Expiry")
    tree.heading("Count", text="Count")

    # Only show items that have been detected (count > 0)
    for item in catalog:
        if item['count'] > 0:
            tree.insert('', tk.END, values=(item["comp_name"], item["prod_name"], item["mrp"], item["expiry"], item["count"]))

    tree.pack(fill=tk.BOTH, expand=True)

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

count_label = tk.Label(product_details_frame, text="Count: ", font=("Arial", 12))
count_label.pack(anchor='w', padx=10, pady=5)

# IR Counter label
ir_counter_label = tk.Label(root, text="IR Counter: 0", font=("Arial", 16), fg="blue")
ir_counter_label.place(x=660, y=550)

# Start and Stop buttons
start_button = tk.Button(root, text="Start Camera", command=start_camera)
start_button.place(x=660, y=600)

stop_button = tk.Button(root, text="Stop Camera", command=stop_camera)
stop_button.place(x=760, y=600)

# Catalog button
catalog_button = tk.Button(root, text="Show Catalog", command=show_catalog)
catalog_button.place(x=660, y=650)

# #Start the IR counter update loop
# update_ir_counter()

# Start the Tkinter main loop
root.mainloop()