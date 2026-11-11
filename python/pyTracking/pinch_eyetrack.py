import cv2
import mediapipe as mp
import math
import time

# --- Setup ---
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
cap = cv2.VideoCapture(0)

# --- NEW: Load Haar Cascade Classifiers for Eye Tracking ---
# These XML files are included with the opencv-python library
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

# --- State and Configuration Variables ---
THUMB_TIP_INDEX = 4
INDEX_FINGER_TIP_INDEX = 8

# MODIFIED: State variable renamed for clarity
eye_tracking_enabled = False 
pinch_event_processed = False # A latch to ensure one toggle per pinch

# Variables for debounce logic
pinch_start_time = None
PINCH_DEBOUNCE_DURATION = 0.2 # in seconds
PINCH_THRESHOLD = 50 # in pixels

while cap.isOpened():
    success, image = cap.read()
    if not success:
        continue

    # Prepare the image
    image = cv2.flip(image, 1)
    image_height, image_width, _ = image.shape
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # Process hands for gesture control
    hand_results = hands.process(image_rgb)

    # --- Hand Landmark Processing (Gesture Control) ---
    if hand_results.multi_hand_landmarks:
        hand_landmarks = hand_results.multi_hand_landmarks[0]
        
        # Get coordinates for thumb and index finger tips
        thumb_tip = hand_landmarks.landmark[THUMB_TIP_INDEX]
        index_tip = hand_landmarks.landmark[INDEX_FINGER_TIP_INDEX]
        thumb_cx, thumb_cy = int(thumb_tip.x * image_width), int(thumb_tip.y * image_height)
        index_cx, index_cy = int(index_tip.x * image_width), int(index_tip.y * image_height)

        # Calculate distance for pinch detection
        distance = math.hypot(index_cx - thumb_cx, index_cy - thumb_cy)
        
        # Toggle Logic
        if distance < PINCH_THRESHOLD:
            if pinch_start_time is None:
                pinch_start_time = time.time()
            elif (time.time() - pinch_start_time) > PINCH_DEBOUNCE_DURATION:
                if not pinch_event_processed:
                    # Toggle the eye tracking state
                    eye_tracking_enabled = not eye_tracking_enabled
                    pinch_event_processed = True
        else:
            pinch_start_time = None
            pinch_event_processed = False
            
        # Visual Feedback for fingertips
        tip_color = (0, 255, 0) if eye_tracking_enabled else (0, 0, 255)
        cv2.circle(image, (thumb_cx, thumb_cy), 10, tip_color, cv2.FILLED)
        cv2.circle(image, (index_cx, index_cy), 10, tip_color, cv2.FILLED)

    # --- NEW: Eye Tracking Logic ---
    if eye_tracking_enabled:
        # Convert image to grayscale for the classifiers
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # Detect faces in the image
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            # Draw a rectangle around the detected face
            cv2.rectangle(image, (x, y), (x+w, y+h), (255, 0, 0), 2)
            
            # Create a Region of Interest (ROI) for both gray and color images
            # This makes eye detection more accurate and faster
            roi_gray = gray[y:y+h, x:x+w]
            roi_color = image[y:y+h, x:x+w]
            
            # Detect eyes within the face ROI
            eyes = eye_cascade.detectMultiScale(roi_gray)
            for (ex, ey, ew, eh) in eyes:
                # Draw a rectangle around each detected eye
                cv2.rectangle(roi_color, (ex, ey), (ex+ew, ey+eh), (0, 255, 0), 2)

    # Display the final image
    cv2.imshow('Gesture Controlled Eye Tracker', image)

    if cv2.waitKey(5) & 0xFF == 27:
        break

hands.close()
cap.release()
cv2.destroyAllWindows()