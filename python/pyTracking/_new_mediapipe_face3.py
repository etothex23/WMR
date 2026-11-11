import cv2
import mediapipe as mp
import os
import urllib.request
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# 1. MODELS - Auto-grab what's missing
FACE_MODEL = "face_landmarker.task"
HAND_MODEL = "hand_landmarker.task"
for model, url in [
    (FACE_MODEL, "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task"),
    (HAND_MODEL, "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task")
]:
    if not os.path.exists(model): urllib.request.urlretrieve(url, model)

# 2. SETUP (No more mp.solutions!)
base_face = python.BaseOptions(model_asset_path=FACE_MODEL)
face_opt = vision.FaceLandmarkerOptions(base_options=base_face, running_mode=vision.RunningMode.VIDEO)
base_hand = python.BaseOptions(model_asset_path=HAND_MODEL)
hand_opt = vision.HandLandmarkerOptions(base_options=base_hand, running_mode=vision.RunningMode.VIDEO)

def draw_dots(img, landmarks):
    for pt in landmarks:
        x, y = int(pt.x * img.shape[1]), int(pt.y * img.shape[0])
        cv2.circle(img, (x, y), 1, (0, 255, 0), -1)

# 3. RUN (USB = 0, Mac = 1)
cap = cv2.VideoCapture(0) 

with vision.FaceLandmarker.create_from_options(face_opt) as f_det, \
     vision.HandLandmarker.create_from_options(hand_opt) as h_det:
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret: break
        frame = cv2.flip(frame, 1)
        
        # New API needs mp.Image and a timestamp
        mp_img = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        ts = int(cv2.getTickCount() / cv2.getTickFrequency() * 1000)

        h_res = h_det.detect_for_video(mp_img, ts)
        f_res = f_det.detect_for_video(mp_img, ts)

        # TRIGGER: No hand = Show Mesh. Hand = Raw Camera.
        if not h_res.hand_landmarks:
            if f_res.face_landmarks:
                for face in f_res.face_landmarks: draw_dots(frame, face)

        cv2.imshow('Face Toggle', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'): break

cap.release()
cv2.destroyAllWindows()