import cv2
import mediapipe as mp

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)

# --- KEY CHANGE 1 ---
# Define the landmark indices for the tips of the fingers and thumb
fingertip_indices = [4, 8, 12, 16, 20] # Thumb, Index, Middle, Ring, Pinky

# Start video capture from the default camera
cap = cv2.VideoCapture(0)

while cap.isOpened():
    success, image = cap.read()
    if not success:
        print("Ignoring empty camera frame.")
        continue

    # Flip the image horizontally for a mirror effect
    image = cv2.flip(image, 1)
    
    # Convert the BGR image to RGB for MediaPipe processing
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # Process the image to find hand landmarks
    results = hands.process(image_rgb)

    # Get image dimensions
    image_height, image_width, _ = image.shape

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            
            # --- KEY CHANGE 2 ---
            # REMOVED: The old line that draws the full skeleton:
            # mp.solutions.drawing_utils.draw_landmarks(
            #     image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # ADDED: A new loop to draw circles only on the fingertips.
            for index in fingertip_indices:
                # Get the specific landmark for the current fingertip
                landmark = hand_landmarks.landmark[index]
                
                # Convert the landmark's normalized coordinates (0.0 to 1.0) 
                # to pixel coordinates (e.g., 0 to 640 or 0 to 480)
                cx, cy = int(landmark.x * image_width), int(landmark.y * image_height)
                
                # Draw a green, filled-in circle at the fingertip's location
                cv2.circle(image, (cx, cy), 10, (0, 255, 0), cv2.FILLED)

    # Display the final image
    cv2.imshow('Fingertip Tracking', image)

    # Exit the loop if the 'ESC' key is pressed
    if cv2.waitKey(5) & 0xFF == 27:
        break

# Release resources
hands.close()
cap.release()
cv2.destroyAllWindows()