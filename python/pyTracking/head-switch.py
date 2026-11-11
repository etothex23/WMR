import cv2
import mediapipe as mp
import numpy as np
import math

# --- Constants and State Variables ---
PINCH_THRESHOLD = 30  # Pixel distance to trigger a pinch
current_image_index = 0
pinch_was_detected_in_last_frame = False

# --- Initialization ---
# MediaPipe Face Detection
mp_face_detection = mp.solutions.face_detection
face_detection = mp_face_detection.FaceDetection(
    model_selection=0, min_detection_confidence=0.5)

# MediaPipe Hand Tracking
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=1, min_detection_confidence=0.7)

# OpenCV Video Capture
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open video stream.")
    exit()

# --- Helper Function for Placeholders ---
def create_placeholder(face_type='smile'):
    """Creates a placeholder smiley or winky face image."""
    ph = np.zeros((200, 200, 4), dtype=np.uint8)
    cv2.circle(ph, (100, 100), 90, (0, 255, 255, 255), -1) # Face
    cv2.circle(ph, (70, 70), 15, (0, 0, 0, 255), -1)      # Left Eye
    cv2.ellipse(ph, (100, 120), (50, 35), 0, 0, 180, (0, 0, 0, 255), 10) # Mouth
    if face_type == 'wink':
        cv2.ellipse(ph, (130, 75), (18, 10), 0, 180, 360, (0, 0, 0, 255), 5) # Wink
    else:
        cv2.circle(ph, (130, 70), 15, (0, 0, 0, 255), -1) # Right Eye
    return ph

# --- Load Replacement Images ---
replacement_images = []
try:
    img1 = cv2.imread('trump-duh.jpg', cv2.IMREAD_UNCHANGED)
    if img1 is None: raise FileNotFoundError
    replacement_images.append(img1)
except (FileNotFoundError, Exception):
    print("Could not find 'replace_head_1.png'. Creating a placeholder.")
    img1 = create_placeholder('smile')
    cv2.imwrite('trump-duh.jpg', img1)
    replacement_images.append(img1)

try:
    img2 = cv2.imread('trump-kiss.jpg', cv2.IMREAD_UNCHANGED)
    if img2 is None: raise FileNotFoundError
    replacement_images.append(img2)
except (FileNotFoundError, Exception):
    print("Could not find 'replace_head_2.png'. Creating a placeholder.")
    img2 = create_placeholder('wink')
    cv2.imwrite('trump-kiss.jpg', img2)
    replacement_images.append(img2)

# --- Main Application Loop ---
while cap.isOpened():
    success, frame = cap.read()
    if not success:
        print("Ignoring empty camera frame.")
        continue

    frame = cv2.flip(frame, 1)
    frame_height, frame_width, _ = frame.shape
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # --- Process Hands for Pinch Gesture ---
    hand_results = hands.process(rgb_frame)
    is_pinched_now = False
    if hand_results.multi_hand_landmarks:
        landmarks = hand_results.multi_hand_landmarks[0].landmark
        
        # Get coordinates for thumb tip (4) and index finger tip (8)
        thumb_tip = landmarks[mp_hands.HandLandmark.THUMB_TIP]
        index_tip = landmarks[mp_hands.HandLandmark.INDEX_FINGER_TIP]
        
        thumb_px = (int(thumb_tip.x * frame_width), int(thumb_tip.y * frame_height))
        index_px = (int(index_tip.x * frame_width), int(index_tip.y * frame_height))

        # Calculate distance between fingertips
        distance = math.sqrt((thumb_px[0] - index_px[0])**2 + (thumb_px[1] - index_px[1])**2)
        
        if distance < PINCH_THRESHOLD:
            is_pinched_now = True
            # Draw a circle to indicate pinch detection
            cv2.circle(frame, index_px, 10, (0, 255, 0), 2)

    # Check for the start of a new pinch gesture to trigger the toggle
    if is_pinched_now and not pinch_was_detected_in_last_frame:
        current_image_index = 1 - current_image_index # Toggle between 0 and 1
        print(f"Pinch detected! Switching to image {current_image_index + 1}")
    
    pinch_was_detected_in_last_frame = is_pinched_now

    # --- Process Faces for Head Replacement ---
    face_results = face_detection.process(rgb_frame)
    if face_results.detections:
        for detection in face_results.detections:
            bboxC = detection.location_data.relative_bounding_box
            x, y, w, h = int(bboxC.xmin * frame_width), int(bboxC.ymin * frame_height), \
                         int(bboxC.width * frame_width), int(bboxC.height * frame_height)

            # Adjust bounding box to better cover the head
            y_adj, h_adj = y - int(h * 0.5), int(h * 1.8)
            x_adj, w_adj = x - int(w * 0.3), int(w * 1.6)

            # Ensure the box is within frame boundaries
            y1, y2 = max(0, y_adj), min(frame_height, y_adj + h_adj)
            x1, x2 = max(0, x_adj), min(frame_width, x_adj + w_adj)
            
            if x2 > x1 and y2 > y1:
                roi = frame[y1:y2, x1:x2]
                roi_h, roi_w, _ = roi.shape

                # Select the current image to display
                current_img = replacement_images[current_image_index]
                r_h, r_w, r_channels = current_img.shape
                
                resized_img = cv2.resize(current_img, (roi_w, roi_h))

                # Blend image based on whether it has transparency
                if r_channels == 4: # PNG with Alpha
                    img_bgr = resized_img[:, :, :3]
                    alpha_mask = cv2.cvtColor(resized_img[:, :, 3], cv2.COLOR_GRAY2BGR) / 255.0
                    bg_part = (roi * (1 - alpha_mask)).astype(np.uint8)
                    fg_part = (img_bgr * alpha_mask).astype(np.uint8)
                    frame[y1:y2, x1:x2] = cv2.add(bg_part, fg_part)
                else: # JPG without Alpha
                    frame[y1:y2, x1:x2] = resized_img

    cv2.imshow('Gesture Head Replacer - Press "q" to quit', frame)
    if cv2.waitKey(5) & 0xFF == ord('q'):
        break

# --- Cleanup ---
cap.release()
cv2.destroyAllWindows()