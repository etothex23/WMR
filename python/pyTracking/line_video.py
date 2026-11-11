import cv2
import numpy as np

def apply_sketch_effect(frame):
    """Applies a high-detail sketch effect to a single video frame."""
    # 1. Convert to grayscale (CORRECTED CONSTANT)
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # 2. Apply a WEAKER Gaussian blur to preserve detail
    blurred_frame = cv2.GaussianBlur(gray_frame, (3, 3), 0)
    
    # 3. Use LOWER thresholds for Canny to detect more edges
    canny_edges = cv2.Canny(blurred_frame, 20, 70)
    
    # 4. Invert the image to get a sketch effect
    ret, mask = cv2.threshold(canny_edges, 120, 255, cv2.THRESH_BINARY_INV)
    
    # 5. Convert back to a 3-channel image
    sketch_frame = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
    
    return sketch_frame

# --- Main execution for live camera (This part is unchanged) ---
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open camera.")
    exit()

print("Camera opened. Press 'q' to quit.")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Can't receive frame. Exiting ...")
        break

    sketch_frame = apply_sketch_effect(frame)
    combined_frame = np.hstack((frame, sketch_frame))
    cv2.imshow('Live Camera vs. High-Detail Sketch (Press Q to Quit)', combined_frame)
    
    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
print("Camera released and windows closed.")