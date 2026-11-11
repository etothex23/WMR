import cv2
import mediapipe as mp
import numpy as np

# --- Initialization ---

# Initialize MediaPipe Face Detection
mp_face_detection = mp.solutions.face_detection
face_detection = mp_face_detection.FaceDetection(
    model_selection=0, min_detection_confidence=0.5
)

# Initialize OpenCV Video Capture
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open video stream.")
    exit()

# --- Load Replacement Image ---

# Load the image to replace the head with.
# IMPORTANT: Create a file named 'replace_head.png' in the same directory.
# For best results, use a PNG image with a transparent background.
try:
    replacement_img = cv2.imread('pill.png', cv2.IMREAD_UNCHANGED)
    if replacement_img is None:
        raise FileNotFoundError("Image 'replace_head.png' not found.")
except (FileNotFoundError, Exception) as e:
    print(f"{e} Creating a default placeholder image.")
    # Create a simple placeholder image (a yellow smiley face) if the file doesn't exist.
    placeholder = np.zeros((200, 200, 4), dtype=np.uint8)
    # Yellow circle for face
    cv2.circle(placeholder, (100, 100), 90, (0, 255, 255, 255), -1)
    # Black circles for eyes
    cv2.circle(placeholder, (70, 70), 15, (0, 0, 0, 255), -1)
    cv2.circle(placeholder, (130, 70), 15, (0, 0, 0, 255), -1)
    # Black arc for smile
    cv2.ellipse(placeholder, (100, 120), (50, 35), 0, 0, 180, (0, 0, 0, 255), 10)
    
    cv2.imwrite('replace_head.png', placeholder)
    replacement_img = placeholder
    print("Created 'replace_head.png'. You can replace this file with your own image.")

# Get the number of channels in the replacement image
r_h, r_w, r_channels = replacement_img.shape


# --- Main Application Loop ---

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        print("Ignoring empty camera frame.")
        continue

    # Flip the frame horizontally for a selfie-view display
    frame = cv2.flip(frame, 1)
    frame_height, frame_width, _ = frame.shape

    # Convert the BGR frame to RGB for MediaPipe
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Process the frame to find faces
    results = face_detection.process(rgb_frame)

    if results.detections:
        for detection in results.detections:
            # Get the bounding box of the detected face
            bboxC = detection.location_data.relative_bounding_box
            x, y, w, h = int(bboxC.xmin * frame_width), int(bboxC.ymin * frame_height), \
                         int(bboxC.width * frame_width), int(bboxC.height * frame_height)

            # --- Adjust Bounding Box to Cover Entire Head ---
            # Increase size and shift position to better cover the head
            y_adj = y - int(h * 0.5)
            h_adj = int(h * 1.8)
            x_adj = x - int(w * 0.3)
            w_adj = int(w * 1.6)

            # --- Overlay Logic ---
            # Ensure the adjusted box is within the frame's boundaries
            y1, y2 = max(0, y_adj), min(frame_height, y_adj + h_adj)
            x1, x2 = max(0, x_adj), min(frame_width, x_adj + w_adj)
            
            # Continue only if the adjusted box has a valid area
            if x2 > x1 and y2 > y1:
                # Get the region of interest (ROI) from the frame
                roi = frame[y1:y2, x1:x2]
                roi_h, roi_w, _ = roi.shape

                # Resize the replacement image to fit the adjusted bounding box
                resized_img = cv2.resize(replacement_img, (roi_w, roi_h))

                # Handle images with transparency (PNG)
                if r_channels == 4:
                    # Split the replacement image into color and alpha (transparency) channels
                    img_bgr = resized_img[:, :, :3]
                    alpha_channel = resized_img[:, :, 3]

                    # Create a 3-channel alpha mask for blending
                    alpha_mask = cv2.cvtColor(alpha_channel, cv2.COLOR_GRAY2BGR) / 255.0

                    # Blend the ROI and the replacement image
                    # Background part (from ROI, where image is transparent)
                    bg_part = (roi * (1 - alpha_mask)).astype(np.uint8)
                    # Foreground part (from replacement image, where it's opaque)
                    fg_part = (img_bgr * alpha_mask).astype(np.uint8)
                    
                    # Combine the parts and place back into the frame
                    frame[y1:y2, x1:x2] = cv2.add(bg_part, fg_part)
                
                # Handle images without transparency (JPG)
                else:
                    # Simply replace the ROI with the resized image
                    frame[y1:y2, x1:x2] = resized_img


    # Display the resulting frame
    cv2.imshow('Head Replacer - Press "q" to quit', frame)

    # Exit loop if 'q' is pressed
    if cv2.waitKey(5) & 0xFF == ord('q'):
        break

# --- Cleanup ---
cap.release()
cv2.destroyAllWindows()