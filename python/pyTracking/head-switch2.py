import cv2
import mediapipe as mp
import numpy as np
import math
import time

# --- Constants and State Variables ---
HAND_PRESENCE_DURATION = 0.5  # Seconds a hand must be present to register

# State variables to manage which image is displayed
display_mode = "RIGHT_HAND_CYCLE"  # Can be "RIGHT_HAND_CYCLE" or "LEFT_HAND_OVERRIDE"
right_hand_image_index = 0

# Timers and triggers to debounce hand gestures
right_hand_start_time = None
right_hand_triggered = False
left_hand_start_time = None
left_hand_triggered = False

# --- Recording State Variables ---
is_recording = False
video_writer = None
output_filename = "image-switch.mp4"


# --- Initialization ---
# MediaPipe Face Detection
mp_face_detection = mp.solutions.face_detection
face_detection = mp_face_detection.FaceDetection(
    model_selection=0, min_detection_confidence=0.5)

# MediaPipe Hand Tracking (now configured for two hands)
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    max_num_hands=2, 
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7)

# OpenCV Video Capture
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open video stream.")
    exit()

# --- Helper Function for Placeholders ---
def create_placeholder(face_type='smile'):
    """Creates a placeholder image (smile, wink, or surprised)."""
    # Note: Placeholders are saved as PNG to support transparency, even if JPG is requested.
    ph = np.zeros((200, 200, 4), dtype=np.uint8)
    cv2.circle(ph, (100, 100), 90, (0, 255, 255, 255), -1) # Face
    cv2.circle(ph, (70, 70), 15, (0, 0, 0, 255), -1)      # Left Eye
    if face_type == 'surprised':
        cv2.ellipse(ph, (100, 130), (30, 40), 0, 0, 360, (0, 0, 0, 255), -1) # Mouth
    else:
        cv2.ellipse(ph, (100, 120), (50, 35), 0, 0, 180, (0, 0, 0, 255), 10) # Mouth
    
    if face_type == 'wink':
        cv2.ellipse(ph, (130, 75), (18, 10), 0, 180, 360, (0, 0, 0, 255), 5) # Wink
    else:
        cv2.circle(ph, (130, 70), 15, (0, 0, 0, 255), -1) # Right Eye
    return ph

# --- Load All Three Replacement Images ---
replacement_images = []
try:
    # Use cv2.IMREAD_COLOR for JPG files
    img1 = cv2.imread('image1.jpg', cv2.IMREAD_COLOR)
    if img1 is None: raise FileNotFoundError
    replacement_images.append(img1)
except FileNotFoundError:
    print("Creating placeholder for 'image1.jpg'.")
    placeholder = create_placeholder('smile')
    replacement_images.append(placeholder)
    cv2.imwrite('image1.png', placeholder) # Save placeholder as png

try:
    img2 = cv2.imread('image2.jpg', cv2.IMREAD_COLOR)
    if img2 is None: raise FileNotFoundError
    replacement_images.append(img2)
except FileNotFoundError:
    print("Creating placeholder for 'image2.jpg'.")
    placeholder = create_placeholder('wink')
    replacement_images.append(placeholder)
    cv2.imwrite('image2.png', placeholder)

try:
    img3 = cv2.imread('image3.jpg', cv2.IMREAD_COLOR)
    if img3 is None: raise FileNotFoundError
    replacement_images.append(img3)
except FileNotFoundError:
    print("Creating placeholder for 'image3.jpg'.")
    placeholder = create_placeholder('surprised')
    replacement_images.append(placeholder)
    cv2.imwrite('image3.png', placeholder)

# --- Main Application Loop ---
while cap.isOpened():
    success, frame = cap.read()
    if not success: continue

    frame = cv2.flip(frame, 1)
    frame_height, frame_width, _ = frame.shape
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # --- Process Hands for Gestures ---
    hand_results = hands.process(rgb_frame)
    
    left_hand_is_present_this_frame = False
    right_hand_is_present_this_frame = False

    if hand_results.multi_hand_landmarks and hand_results.multi_handedness:
        for handedness in hand_results.multi_handedness:
            # Determine if the hand is Left or Right
            hand_label = handedness.classification[0].label
            if hand_label == "Left":
                left_hand_is_present_this_frame = True
            elif hand_label == "Right":
                right_hand_is_present_this_frame = True

    # --- State Change Logic with Timers (Debouncing) ---

    # Right Hand Presence Logic
    if right_hand_is_present_this_frame:
        if right_hand_start_time is None:
            right_hand_start_time = time.time()
        elif not right_hand_triggered and (time.time() - right_hand_start_time) >= HAND_PRESENCE_DURATION:
            if display_mode == "LEFT_HAND_OVERRIDE":
                # Right hand takes over from left, resetting the cycle to image 1
                display_mode = "RIGHT_HAND_CYCLE"
                right_hand_image_index = 0
                print("Right hand detected! Overriding left, switching to image 1")
            else:
                # Right hand is already in control, so it toggles its own cycle
                right_hand_image_index = 1 - right_hand_image_index
                print(f"Right hand detected! Toggling to image {right_hand_image_index + 1}")
            
            right_hand_triggered = True
    else:
        right_hand_start_time = None
        right_hand_triggered = False

    # Left Hand Presence Logic (only triggers if right hand is not present)
    if left_hand_is_present_this_frame and not right_hand_is_present_this_frame:
        if left_hand_start_time is None:
            left_hand_start_time = time.time()
        elif not left_hand_triggered and (time.time() - left_hand_start_time) >= HAND_PRESENCE_DURATION:
            display_mode = "LEFT_HAND_OVERRIDE"
            print("Left hand detected! Switching to override image 3")
            left_hand_triggered = True
    else:
        # Reset the trigger if the left hand is not the active hand
        left_hand_start_time = None
        left_hand_triggered = False


    # --- Select the Final Image to Display based on the current mode ---
    if display_mode == "LEFT_HAND_OVERRIDE":
        display_image = replacement_images[2]  # Show image 3
    else:  # display_mode == "RIGHT_HAND_CYCLE"
        display_image = replacement_images[right_hand_image_index]


    # --- Process Face and Overlay Image ---
    face_results = face_detection.process(rgb_frame)
    if face_results.detections:
        # Find the detection with the largest bounding box (likely the user's head).
        largest_detection = None
        max_area = 0
        for detection in face_results.detections:
            bbox = detection.location_data.relative_bounding_box
            area = bbox.width * bbox.height
            if area > max_area:
                max_area = area
                largest_detection = detection
        
        # If a face was found, apply the overlay to ONLY the largest one.
        if largest_detection:
            detection = largest_detection
            bboxC = detection.location_data.relative_bounding_box
            x, y, w, h = int(bboxC.xmin * frame_width), int(bboxC.ymin * frame_height), \
                         int(bboxC.width * frame_width), int(bboxC.height * frame_height)

            y_adj, h_adj = y - int(h * 0.5), int(h * 1.8)
            x_adj, w_adj = x - int(w * 0.3), int(w * 1.6)
            y1, y2 = max(0, y_adj), min(frame_height, y_adj + h_adj)
            x1, x2 = max(0, x_adj), min(frame_width, x_adj + w_adj)
            
            if x2 > x1 and y2 > y1:
                roi = frame[y1:y2, x1:x2]
                roi_h, roi_w, _ = roi.shape

                # Check for None before getting shape
                if display_image is not None:
                    r_h, r_w, r_channels = display_image.shape
                    resized_img = cv2.resize(display_image, (roi_w, roi_h))

                    if r_channels == 4: # Image has transparency (PNG placeholder)
                        img_bgr = resized_img[:, :, :3]
                        alpha_mask = cv2.cvtColor(resized_img[:, :, 3], cv2.COLOR_GRAY2BGR) / 255.0
                        bg_part = (roi * (1 - alpha_mask)).astype(np.uint8)
                        fg_part = (img_bgr * alpha_mask).astype(np.uint8)
                        frame[y1:y2, x1:x2] = cv2.add(bg_part, fg_part)
                    else: # Image is opaque (JPG)
                        frame[y1:y2, x1:x2] = resized_img

    # --- Recording Visual Indicator ---
    if is_recording:
        cv2.circle(frame, (30, 30), 10, (0, 0, 255), -1)
        cv2.putText(frame, "REC", (50, 38), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
    
    # --- Write Frame to Video File if Recording ---
    if is_recording and video_writer is not None:
        video_writer.write(frame)

    cv2.imshow('Hand Gesture Head Replacer - Press "q" to quit, "r" to record', frame)
    
    key = cv2.waitKey(5) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('r'):
        if is_recording:
            # Stop recording
            print(f"Stopping recording. Video saved as {output_filename}")
            is_recording = False
            video_writer.release()
            video_writer = None
        else:
            # Start recording
            print("Starting to record...")
            is_recording = True
            # Define the codec and create VideoWriter object
            fourcc = cv2.VideoWriter_fourcc(*'mp4v') # Codec for .mp4
            fps = 20.0 # Standard FPS
            video_writer = cv2.VideoWriter(output_filename, fourcc, fps, (frame_width, frame_height))


# --- Cleanup ---
if is_recording:
    video_writer.release() # Ensure video is saved if app is quit while recording
cap.release()
cv2.destroyAllWindows()