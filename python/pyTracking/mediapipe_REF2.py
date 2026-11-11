import cv2
import mediapipe as mp
import os
import urllib.request
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# 1. THE AUTO-DOWNLOAD (Grabs the model if you don't have it)
MODEL_PATH = "face_landmarker.task"
if not os.path.exists(MODEL_PATH):
    print("Downloading model... sit tight.")
    url = "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task"
    urllib.request.urlretrieve(url, MODEL_PATH)

# 2. SETUP THE NEW API
base_options = python.BaseOptions(model_asset_path=MODEL_PATH)
options = vision.FaceLandmarkerOptions(
    base_options=base_options,
    running_mode=vision.RunningMode.VIDEO,
    num_faces=1)

# 3. MANUAL DRAWING FUNCTION (Because Google deleted mp.solutions.drawing_utils)
def draw_landmarks_manual(image, detection_result):
    if not detection_result.face_landmarks:
        return image
    for face_landmarks in detection_result.face_landmarks:
        for landmark in face_landmarks:
            x = int(landmark.x * image.shape[1])
            y = int(landmark.y * image.shape[0])
            cv2.circle(image, (x, y), 1, (0, 255, 0), -1)
    return image

# 4. START THE CAM
# You said (0) is USB and (1) is Mac—adjust here if it flips
cap = cv2.VideoCapture(0) 

with vision.FaceLandmarker.create_from_options(options) as landmarker:
    while cap.isOpened():
        success, frame = cap.read()
        if not success: continue

        # Convert for MediaPipe
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        
        # New API requires a timestamp in milliseconds
        timestamp_ms = int(cv2.getTickCount() / cv2.getTickFrequency() * 1000)
        
        # Run detection
        result = landmarker.detect_for_video(mp_image, timestamp_ms)

        # Draw and Show
        frame = draw_landmarks_manual(frame, result)
        cv2.imshow('MediaPipe Face Tracker', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()