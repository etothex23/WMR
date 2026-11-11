import cv2
import mediapipe as mp
import math
import time

# --- Setup ---
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
cap = cv2.VideoCapture(0)

# --- Load Haar Cascade Classifiers for Eye Tracking ---
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')

# --- State and Configuration Variables ---
THUMB_TIP_INDEX = 4
INDEX_FINGER_TIP_INDEX = 8

eye_tracking_enabled = False 
pinch_event_processed = False 

pinch_start_time = None
PINCH_DEBOUNCE_DURATION = 0.2 
PINCH_THRESHOLD = 55 

while cap.isOpened():
    success, image = cap.read()
    if not success:
        continue

    image = cv2.flip(image, 1)
    image_height, image_width, _ = image.shape
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    hand_results = hands.process(image_rgb)

    # --- Hand Landmark Processing (Gesture Control) ---
    if hand_results.multi_hand_landmarks:
        hand_landmarks = hand_results.multi_hand_landmarks[0]
        
        thumb_tip = hand_landmarks.landmark[THUMB_TIP_INDEX]
        index_tip = hand_landmarks.landmark[INDEX_FINGER_TIP_INDEX]
        thumb_cx, thumb_cy = int(thumb_tip.x * image_width), int(thumb_tip.y * image_height)
        index_cx, index_cy = int(index_tip.x * image_width), int(index_tip.y * image_height)

        distance = math.hypot(index_cx - thumb_cx, index_cy - thumb_cy)
        
        if distance < PINCH_THRESHOLD:
            if pinch_start_time is None:
                pinch_start_time = time.time()
            elif (time.time() - pinch_start_time) > PINCH_DEBOUNCE_DURATION:
                if not pinch_event_processed:
                    eye_tracking_enabled = not eye_tracking_enabled
                    pinch_event_processed = True
        else:
            pinch_start_time = None
            pinch_event_processed = False
            
        tip_color = (0, 255, 0) if eye_tracking_enabled else (0, 0, 255)
        cv2.circle(image, (thumb_cx, thumb_cy), 10, tip_color, cv2.FILLED)
        cv2.circle(image, (index_cx, index_cy), 10, tip_color, cv2.FILLED)

    # --- REFINED Eye Tracking Logic ---
    if eye_tracking_enabled:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            cv2.rectangle(image, (x, y), (x+w, y+h), (255, 0, 0), 2)
            
            # --- KEY CHANGE: Create a Region of Interest for the upper part of the face ---
            # We define the upper region of the face where eyes are expected to be.
            eye_roi_y_end = y + int(h * 0.6) # Search in the top 60% of the face
            
            # Create the ROI slices from the original images
            roi_gray = gray[y:eye_roi_y_end, x:x+w]
            roi_color = image[y:eye_roi_y_end, x:x+w]
            
            # --- KEY CHANGE: Run eye detection on the smaller ROI with stricter parameters ---
            # The minNeighbors parameter is increased to 7 to reduce false positives.
            eyes = eye_cascade.detectMultiScale(roi_gray, scaleFactor=1.1, minNeighbors=7)
            
            for (ex, ey, ew, eh) in eyes:
                # Draw the rectangle on the color ROI
                cv2.rectangle(roi_color, (ex, ey), (ex+ew, ey+eh), (0, 255, 0), 2)

    cv2.imshow('Gesture Controlled Eye Tracker', image)

    if cv2.waitKey(5) & 0xFF == 27:
        break

hands.close()
cap.release()
cv2.destroyAllWindows()