import cv2
import mediapipe as mp
import math
import time

# --- Setup ---
# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_drawing = mp.solutions.drawing_utils

# Start video capture
cap = cv2.VideoCapture(0)

# --- State and Configuration Variables ---
# Landmark indices for thumb and index finger tips
THUMB_TIP_INDEX = 4
INDEX_FINGER_TIP_INDEX = 8

# A list to store the start and end points of lines to be drawn
lines_to_draw = []

# Pinch gesture state variables
is_pinching = False
pinch_start_time = None
pinch_point_start = None
pinch_point_end = None
PINCH_DEBOUNCE_DURATION = 0.2 # in seconds
PINCH_THRESHOLD = 30 # in pixels

while cap.isOpened():
    success, image = cap.read()
    if not success:
        print("Ignoring empty camera frame.")
        continue

    # Flip the image horizontally for a mirror effect
    image = cv2.flip(image, 1)
    image_height, image_width, _ = image.shape
    
    # Convert the BGR image to RGB for MediaPipe
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = hands.process(image_rgb)

    # --- Hand Landmark Processing ---
    if results.multi_hand_landmarks:
        # We'll just use the first hand detected
        hand_landmarks = results.multi_hand_landmarks[0]
        
        # Get pixel coordinates for thumb and index finger tips
        thumb_tip = hand_landmarks.landmark[THUMB_TIP_INDEX]
        index_tip = hand_landmarks.landmark[INDEX_FINGER_TIP_INDEX]
        
        thumb_cx, thumb_cy = int(thumb_tip.x * image_width), int(thumb_tip.y * image_height)
        index_cx, index_cy = int(index_tip.x * image_width), int(index_tip.y * image_height)

        # Calculate the distance between the thumb and index finger
        distance = math.hypot(index_cx - thumb_cx, index_cy - thumb_cy)
        
        # --- Pinch Detection Logic ---
        # 1. Check if fingers are close enough to be a potential pinch
        if distance < PINCH_THRESHOLD:
            if not is_pinching: # If we are not already in a confirmed pinch
                if pinch_start_time is None:
                    # Start the timer for debouncing
                    pinch_start_time = time.time()
                elif (time.time() - pinch_start_time) > PINCH_DEBOUNCE_DURATION:
                    # If enough time has passed, confirm the pinch
                    is_pinching = True
                    pinch_point_start = (thumb_cx, thumb_cy)
                    pinch_point_end = (index_cx, index_cy)
        else:
            # 2. If fingers are separated
            if is_pinching:
                # If we were just pinching, this is the "release" action
                lines_to_draw.append((pinch_point_start, pinch_point_end))
            
            # 3. Reset the state
            is_pinching = False
            pinch_start_time = None
            
        # --- Drawing and Visual Feedback ---
        # Draw a line between the tips for live feedback
        cv2.line(image, (thumb_cx, thumb_cy), (index_cx, index_cy), (255, 0, 0), 2)
        
        # Change the color of tip circles if a pinch is confirmed
        tip_color = (0, 255, 0) if is_pinching else (0, 0, 255)
        cv2.circle(image, (thumb_cx, thumb_cy), 10, tip_color, cv2.FILLED)
        cv2.circle(image, (index_cx, index_cy), 10, tip_color, cv2.FILLED)

    # Draw all the permanent lines that have been created
    for start_point, end_point in lines_to_draw:
        if start_point and end_point:
            cv2.line(image, start_point, end_point, (0, 255, 255), 3)

    # Display the final image
    cv2.imshow('Pinch to Draw', image)

    if cv2.waitKey(5) & 0xFF == 27:
        break

hands.close()
cap.release()
cv2.destroyAllWindows()