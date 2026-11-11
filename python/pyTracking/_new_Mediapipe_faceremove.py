import cv2
import mediapipe as mp
import os
import numpy as np
import urllib.request
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# 1. SETUP MODELS
FACE_MODEL = "face_landmarker.task"
HAND_MODEL = "hand_landmarker.task"

for model, url in [
    (FACE_MODEL, "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task"),
    (HAND_MODEL, "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task")
]:
    if not os.path.exists(model):
        print(f"Grabbing {model}...")
        urllib.request.urlretrieve(url, model)

# 2. INITIALIZE DETECTORS
base_face = python.BaseOptions(model_asset_path=FACE_MODEL)
face_options = vision.FaceLandmarkerOptions(base_options=base_face, running_mode=vision.RunningMode.VIDEO)

base_hand = python.BaseOptions(model_asset_path=HAND_MODEL)
hand_options = vision.HandLandmarkerOptions(base_options=base_hand, running_mode=vision.RunningMode.VIDEO, num_hands=2)

# 3. DRAWING LOGIC (dots only)
def draw_dots(canvas, landmarks, color=(0, 255, 0)):
    for landmark in landmarks:
        x = int(landmark.x * canvas.shape[1])
        y = int(landmark.y * canvas.shape[0])
        cv2.circle(canvas, (x, y), 1, color, -1)

# 4. MAIN LOOP
cap = cv2.VideoCapture(0) # 0 for USB

with vision.FaceLandmarker.create_from_options(face_options) as face_det, \
     vision.HandLandmarker.create_from_options(hand_options) as hand_det:
    
    while cap.isOpened():
        success, frame = cap.read()
        if not success: continue

        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        
        # Create the "Void" (Black Background)
        black_bg = np.zeros((h, w, 3), dtype=np.uint8)
        
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        ts = int(cv2.getTickCount() / cv2.getTickFrequency() * 1000)

        # Detect Face & Hand
        face_result = face_det.detect_for_video(mp_image, ts)
        hand_result = hand_det.detect_for_video(mp_image, ts)

        # Draw Face (Green)
        if face_result.face_landmarks:
            for landmarks in face_result.face_landmarks:
                draw_dots(black_bg, landmarks, (0, 255, 0))

        # Draw Hand (Blue/Cyan) - Our "Trigger" visual
        if hand_result.hand_landmarks:
            for landmarks in hand_result.hand_landmarks:
                draw_dots(black_bg, landmarks, (255, 255, 0))

        cv2.imshow('Constellation Mode', black_bg)
        if cv2.waitKey(1) & 0xFF == ord('q'): break

cap.release()
cv2.destroyAllWindows()