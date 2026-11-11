import cv2
import mediapipe as mp
import math
import time
import random # Needed for the flickering effect

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

# --- Function to draw electrified eyes ---
def draw_electrified_eyes(image, center_x, center_y, radius, frame_count):
    base_color_bgr = (255, 255, 0) # Cyan/Electric Blue
    overlay = image.copy()
    
    num_glow_layers = 3
    
    for i in range(num_glow_layers, 0, -1):
        current_radius = int(radius * (1 + (i * 0.4)))
        alpha = 0.1 / i
        
        flicker_offset_x = random.randint(-radius // 8, radius // 8)
        flicker_offset_y = random.randint(-radius // 8, radius // 8)
        flicker_color_boost = random.randint(0, 50)

        layer_color = (
            min(255, base_color_bgr[0] + flicker_color_boost),
            min(255, base_color_bgr[1] + flicker_color_boost),
            min(255, base_color_bgr[2] + flicker_color_boost)
        )
        
        cv2.ellipse(overlay, 
                    (center_x + flicker_offset_x, center_y + flicker_offset_y), 
                    (current_radius, int(current_radius * 0.7)), 
                    0, 0, 360, layer_color, -1)

        image = cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0)
        overlay = image.copy()
        
    spark_radius = int(radius * 0.4)
    spark_color = (255, 255, 255)
    cv2.circle(image, (center_x, center_y), spark_radius, spark_color, -1)

    cv2.ellipse(image, (center_x, center_y), (radius, int(radius * 0.7)), 0, 0, 360, base_color_bgr, 2)
    
    # --- FIX #1: Return the modified image from the function ---
    return image


frame_count = 0
while cap.isOpened():
    success, image = cap.read()
    if not success:
        continue

    frame_count += 1
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

    # --- Eye Tracking Logic with Electrified Effect ---
    if eye_tracking_enabled:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            eye_roi_y_end = y + int(h * 0.6) 
            roi_gray = gray[y:eye_roi_y_end, x:x+w]
            
            eyes = eye_cascade.detectMultiScale(roi_gray, scaleFactor=1.1, minNeighbors=7, minSize=(20,20))
            
            for (ex, ey, ew, eh) in eyes:
                eye_center_x = x + ex + ew // 2
                eye_center_y = y + ey + eh // 2
                eye_radius = int(max(ew, eh) // 2)

                # --- FIX #2: Update the main image with the function's result ---
                image = draw_electrified_eyes(image, eye_center_x, eye_center_y, eye_radius, frame_count)
                
    cv2.imshow('Gesture Controlled Electrified Eye Tracker', image)

    if cv2.waitKey(5) & 0xFF == 27:
        break

hands.close()
cap.release()
cv2.destroyAllWindows()