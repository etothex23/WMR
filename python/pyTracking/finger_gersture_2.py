import cv2
import mediapipe as mp
import math
import time

# --- Setup ---
mp_hands = mp.solutions.hands # Correctly access the lowercase 'hands' module
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
cap = cv2.VideoCapture(0)

# --- State and Configuration Variables ---
THUMB_TIP_INDEX = 4
INDEX_FINGER_TIP_INDEX = 8

# NEW: State for toggling the line
draw_connecting_line = False
pinch_event_processed = False # A latch to ensure one toggle per pinch

# Variables for debounce logic
pinch_start_time = None
PINCH_DEBOUNCE_DURATION = 0.2 # in seconds
PINCH_THRESHOLD = 55 # in pixels

while cap.isOpened():
    success, image = cap.read()
    if not success:
        continue

    # Prepare the image
    image = cv2.flip(image, 1)
    image_height, image_width, _ = image.shape
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = hands.process(image_rgb)

    # --- Hand Landmark Processing ---
    if results.multi_hand_landmarks:
        hand_landmarks = results.multi_hand_landmarks[0]
        
        # Get coordinates for thumb and index finger tips
        thumb_tip = hand_landmarks.landmark[THUMB_TIP_INDEX]
        index_tip = hand_landmarks.landmark[INDEX_FINGER_TIP_INDEX]
        thumb_cx, thumb_cy = int(thumb_tip.x * image_width), int(thumb_tip.y * image_height)
        index_cx, index_cy = int(index_tip.x * image_width), int(index_tip.y * image_height)

        # Calculate distance
        distance = math.hypot(index_cx - thumb_cx, index_cy - thumb_cy)
        
        # --- NEW Toggle Logic ---
        if distance < PINCH_THRESHOLD:
            # Start debounce timer on first detection
            if pinch_start_time is None:
                pinch_start_time = time.time()
            
            # If pinch is held long enough, and we haven't processed this pinch yet
            elif (time.time() - pinch_start_time) > PINCH_DEBOUNCE_DURATION:
                if not pinch_event_processed:
                    # Toggle the drawing state
                    draw_connecting_line = not draw_connecting_line
                    # Mark this pinch event as processed to prevent rapid toggling
                    pinch_event_processed = True
        else:
            # If fingers are apart, reset the debounce timer and the event latch
            pinch_start_time = None
            pinch_event_processed = False
            
        # --- Drawing and Visual Feedback ---
        # Draw the connecting line ONLY if the state is True
        if draw_connecting_line:
            cv2.line(image, (thumb_cx, thumb_cy), (index_cx, index_cy), (0, 255, 0), 3)

        # Always draw circles on the fingertips
        # The color now reflects the line's on/off state
        tip_color = (0, 255, 0) if draw_connecting_line else (0, 0, 255)
        cv2.circle(image, (thumb_cx, thumb_cy), 10, tip_color, cv2.FILLED)
        cv2.circle(image, (index_cx, index_cy), 10, tip_color, cv2.FILLED)

    # Display the final image
    cv2.imshow('Pinch Toggle Line', image)

    if cv2.waitKey(5) & 0xFF == 27:
        break

hands.close()
cap.release()
cv2.destroyAllWindows()