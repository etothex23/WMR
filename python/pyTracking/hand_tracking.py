import cv2
import mediapipe as mp

# Initialize MediaPipe modules
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

# --- Main execution for live camera ---
# Initialize video capture from the default camera
cap = cv2.VideoCapture(0)

# Set up the MediaPipe Hands model
# min_detection_confidence: How sure the model needs to be to detect a hand (e.g., 0.7 = 70%)
# min_tracking_confidence: How sure the model needs to be to track the hand to the next frame
with mp_hands.Hands(
    model_complexity=0,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7) as hands:
    
    if not cap.isOpened():
        print("Error: Could not open camera.")
        exit()

    print("Camera opened. Show your hand to the camera. Press 'q' to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Can't receive frame. Exiting ...")
            break

        # IMPORTANT: Flip the frame horizontally for a later selfie-view display.
        # This makes it intuitive, like looking in a mirror.
        frame = cv2.flip(frame, 1)

        # To improve performance, optionally mark the image as not writeable to
        # pass by reference.
        frame.flags.writeable = False
        
        # MediaPipe expects RGB images, but OpenCV reads in BGR. We need to convert.
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process the image and find hands
        results = hands.process(image_rgb)
        
        # Once processed, we can make the image writeable again to draw on it.
        frame.flags.writeable = True

        # Check if any hands were detected
        if results.multi_hand_landmarks:
            # Loop through all the hands that were found
            for hand_landmarks in results.multi_hand_landmarks:
                # Use the drawing utility to draw the landmarks and connections
                mp_drawing.draw_landmarks(
                    frame,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing_styles.get_default_hand_landmarks_style(),
                    mp_drawing_styles.get_default_hand_connections_style())

        # Display the resulting frame
        cv2.imshow('Hand Tracking (Press Q to Quit)', frame)
        
        # Wait for the 'q' key to be pressed to exit
        if cv2.waitKey(5) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
print("Camera released and windows closed.")
