import cv2
import threading
import easyocr
import torch
import tkinter as tk
from tkinter import Text, Label
from PIL import Image, ImageTk
import warnings

# Suppress future warnings
warnings.filterwarnings("ignore", category=FutureWarning)

# Initialize EasyOCR reader with GPU support
reader = easyocr.Reader(['en'], gpu=True)

# Initialize global variables
running = False
cap = None

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

            # Display the text in the text box
            text_box.delete('1.0', tk.END)  # Clear previous text
            extracted_texts = [text for _, text, _ in results]
            text_box.insert(tk.END, '\n'.join(extracted_texts))

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

# Create the GUI application
root = tk.Tk()
root.title("Camera")
root.geometry('1280x720')  # Set window size to 720p (1280x720)

# Left frame for the camera feed
camera_frame = tk.Frame(root, width=640, height=480)
camera_frame.pack(side=tk.LEFT, padx=10, pady=10)

# Label to display the camera feed
camera_label = tk.Label(camera_frame)
camera_label.pack()

# Right frame for text extraction
text_frame = tk.Frame(root, width=640, height=480)
text_frame.pack(side=tk.RIGHT, padx=10, pady=10)

# Add title above the text box
title_label = Label(text_frame, text="Product Details", font=('Arial', 16))
title_label.pack(pady=5)

# Text box to display the extracted text
text_box = Text(text_frame, width=60, height=20)
text_box.pack()

# Start and Stop buttons
button_frame = tk.Frame(root)
button_frame.pack(side=tk.BOTTOM, pady=10)

start_button = tk.Button(button_frame, text="Start", command=start_camera)
start_button.pack(side=tk.LEFT, padx=5)

stop_button = tk.Button(button_frame, text="Stop", command=stop_camera)
stop_button.pack(side=tk.RIGHT, padx=5)

# Run the GUI application
root.mainloop()
