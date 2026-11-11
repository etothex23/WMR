import cv2
import mediapipe as mp
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3' # Hides TensorFlow logging

# --- INITIALIZATION ---
# Initialize MediaPipe solutions
mp_drawing = mp.solutions.drawing_utils
mp_face_mesh = mp.solutions.face_mesh

# Define drawing specifications for the mesh and contours
# Make points small (radius 1) and lines thin (thickness 1)
draw_spec_points = mp_drawing.DrawingSpec(color=(200, 200, 200), thickness=1, circle_radius=1)
draw_spec_lines = mp_drawing.DrawingSpec(color=(255, 255, 255), thickness=1)

# Initialize the Face Mesh model
face_mesh = mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True, # Use this to get landmarks for iris, pupils, and lips
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5)

# Start video capture from the default webcam
# cap = cv2.VideoCapture(0)
# cv2.CAP_AVFOUNDATION is the native macOS camera driver
cap = cv2.VideoCapture(0, cv2.CAP_AVFOUNDATION)
# --- MAIN LOOP ---
while cap.isOpened():
    success, image = cap.read()
    if not success:
        print("Ignoring empty camera frame.")
        continue

    # Flip the image horizontally for a selfie-view display.
    image = cv2.flip(image, 1)
    
    # Convert the BGR image to RGB before processing.
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # Process the image and find face landmarks.
    results = face_mesh.process(image_rgb)

    # --- DRAWING THE LANDMARKS ---
    # Check if any face landmarks were detected
    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            
            # Draw the main face mesh tessellation
            mp_drawing.draw_landmarks(
                image=image,
                landmark_list=face_landmarks,
                connections=mp_face_mesh.FACEMESH_TESSELATION,
                landmark_drawing_spec=draw_spec_points,
                connection_drawing_spec=draw_spec_lines)
            
            # Draw the key facial contours (eyes, eyebrows, lips)
            # This makes the main features stand out more clearly
            mp_drawing.draw_landmarks(
                image=image,
                landmark_list=face_landmarks,
                connections=mp_face_mesh.FACEMESH_CONTOURS,
                landmark_drawing_spec=None, # We don't need to draw the points again
                connection_drawing_spec=mp_drawing.DrawingSpec(color=(80,255,80), thickness=1)) # Green lines for contours


    # Display the final image
    cv2.imshow('MediaPipe Face Mesh Reference', image)

    # Exit the loop if the 'ESC' key is pressed
    if cv2.waitKey(5) & 0xFF == 27:
        break

# --- CLEANUP ---
cap.release()
cv2.destroyAllWindows()