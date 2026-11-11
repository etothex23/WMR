import cv2
import mediapipe as mp
import os
import urllib.request
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# 1. AUTO-DOWNLOAD MODELS
FACE_MODEL = "face_landmarker.task"
HAND_MODEL = "hand_landmarker.task"

for model, url in [
    (FACE_MODEL, "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task"),
    (HAND_MODEL, "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/face_landmarker.task")
]:
    if not os.path.exists(model):
        print(f"Downloading {model}...")
        urllib.request.urlretrieve(url, model)

# 2. SETUP THE DETECTORS
base_face = python.BaseOptions(model_asset_path=FACE_MODEL)
face_opt = vision.FaceLandmarkerOptions(base_options=base_face, running_mode=vision.RunningMode.VIDEO)

base_hand = python.BaseOptions(model_asset_path=HAND_MODEL)
hand_opt = vision.HandLandmarkerOptions(base_options=base_hand, running_mode=vision.RunningMode.VIDEO)

def draw_dots(image, landmarks, color=(0, 255, 0)):
    for landmark in landmarks:
        x = int(landmark.x * image.shape[1])
        y = int(landmark.y * image.shape[0])
        cv2.circle(image, (x, y), 1, color, -1)

# 3. MAIN LOOP
cap = cv2.VideoCapture(0) # 0 for USB on your setup

with vision.FaceLandmarker.create_from_options(face_opt) as face_det, \
     vision.HandLandmarker.create_from_options(hand_opt) as hand_det:
    
    while cap.isOpened():
        success, frame = cap.read()
        if not success: continue

        frame = cv2.flip(frame, 1)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        ts = int(cv2.getTickCount() / cv2.getTickFrequency() * 1000)

        # Run detections
        hand_result = hand_det.detect_for_video(mp_image, ts)
        face_result = face_det.detect_for_video(mp_image, ts)

        # TRIGGER LOGIC: If NO hand is visible, draw the face dots.
        # If a hand enters the frame, the 'if' fails and dots disappear.
        if not hand_result.hand_landmarks:
            if face_result.face_landmarks:
                for face_pts in face_result.face_landmarks:
                    draw_dots(frame, face_pts, (0, 255, 0))
        else:
            # Optional: Add a label so you know the trigger is active
            cv2.putText(frame, "HAND DETECTED: FACE OFF", (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        cv2.imshow('MediaPipe Hand Trigger', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'): break

cap.release()
cv2.destroyAllWindows()