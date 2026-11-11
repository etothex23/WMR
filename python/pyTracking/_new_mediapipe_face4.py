import cv2
import mediapipe as mp
import os
import numpy as np
import urllib.request
import time
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

# 2. SETUP DETECTORS
base_face = python.BaseOptions(model_asset_path=FACE_MODEL)
face_opt = vision.FaceLandmarkerOptions(base_options=base_face, running_mode=vision.RunningMode.VIDEO)
base_hand = python.BaseOptions(model_asset_path=HAND_MODEL)
hand_opt = vision.HandLandmarkerOptions(base_options=base_hand, running_mode=vision.RunningMode.VIDEO)

def get_face_mask(img, landmarks):
    """Creates a binary mask (white shape of face) based on mesh points."""
    mask = np.zeros(img.shape[:2], dtype=np.uint8)
    points = np.array([[int(pt.x * img.shape[1]), int(pt.y * img.shape[0])] for pt in landmarks])
    # Use convexHull to get a clean outer boundary for the face
    hull = cv2.convexHull(points)
    cv2.fillConvexPoly(mask, hull, 255)
    return mask

# 3. INITIALIZE CAMERA
cap = cv2.VideoCapture(0)
background = None

# --- NEW SECTION: BACKGROUND CAPTURE ---
print("GET OUT OF THE FRAME! Capturing background in 2 seconds...")
time.sleep(2)
ret, background = cap.read()
if ret:
    background = cv2.flip(background, 1)
    print("Background captured! You can enter now.")
# ---------------------------------------

with vision.FaceLandmarker.create_from_options(face_opt) as f_det, \
     vision.HandLandmarker.create_from_options(hand_opt) as h_det:
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret: break
        frame = cv2.flip(frame, 1)
        
        mp_img = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        ts = int(cv2.getTickCount() / cv2.getTickFrequency() * 1000)

        h_res = h_det.detect_for_video(mp_img, ts)
        f_res = f_det.detect_for_video(mp_img, ts)

        # --- NEW SECTION: THE INVISIBILITY LOGIC ---
        if f_res.face_landmarks:
            for face in f_res.face_landmarks:
                # 1. Create a mask of the face
                mask = get_face_mask(frame, face)
                mask_inv = cv2.bitwise_not(mask)

                # 2. If NO hand is visible, replace the face area with the background
                if not h_res.hand_landmarks:
                    # Black out the face area in the current frame
                    frame_bg = cv2.bitwise_and(frame, frame, mask=mask_inv)
                    # Extract only the face-shaped area from the empty room photo
                    empty_room_face = cv2.bitwise_and(background, background, mask=mask)
                    # Combine them
                    frame = cv2.add(frame_bg, empty_room_face)
        # -------------------------------------------

        cv2.imshow('Invisibility Face Toggle', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'): break

cap.release()
cv2.destroyAllWindows()