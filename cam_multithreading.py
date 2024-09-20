import cv2
import threading
import easyocr
import torch
import warnings

warnings.filterwarnings("ignore", category=FutureWarning)


# Initialize EasyOCR Reader with GPU enabled
reader = easyocr.Reader(['en'], gpu=True)

# Flag to control threading
processing = False

# Store the latest processed frame to display
output_frame = None

# Function to process frames in a separate thread
def process_frame(frame):
    global processing, output_frame

    # Resize frame to reduce memory usage
    frame_resized = cv2.resize(frame, (640, 480))

    # Convert to grayscale, apply Gaussian blur, and detect edges
    gray = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 1)
    edges = cv2.Canny(blur, 100, 200)

    # Perform OCR using GPU
    results = reader.readtext(frame_resized)
    
    # Debug: Print detected text to console
    if results:
        print("Detected text:", [text for _, text, _ in results])
    else:
        print("No text detected")

    # Draw bounding boxes and text on the frame
    for (bbox, text, prob) in results:
        top_left = tuple(map(int, bbox[0]))
        bottom_right = tuple(map(int, bbox[2]))
        cv2.rectangle(frame_resized, top_left, bottom_right, (0, 255, 0), 2)
        cv2.putText(frame_resized, text, (top_left[0], top_left[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # Store the processed frame for display
    output_frame = frame_resized

    # Show the Canny edge detection result
    #cv2.imshow('Canny Edges', edges)

    # Clear GPU memory
    torch.cuda.empty_cache()

    # Allow new frames to be processed
    processing = False

# Capture video from webcam
cap = cv2.VideoCapture(1)

# Main loop to capture frames
while True:
    ret, frame = cap.read()
    if not ret:
        break

    # If not currently processing, start a new thread to process the frame
    if not processing:
        processing = True
        threading.Thread(target=process_frame, args=(frame.copy(),)).start()

    # Display the original webcam feed or the processed frame if available
    if output_frame is not None:
        cv2.imshow('Webcam', output_frame)
    else:
        cv2.imshow('Webcam', frame)

    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture and close windows
cap.release()
cv2.destroyAllWindows()
