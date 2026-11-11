import cv2
import mediapipe as mp
import numpy as np

# --- INITIALIZATION ---
mp_drawing = mp.solutions.drawing_utils
mp_face_mesh = mp.solutions.face_mesh

draw_spec_lines = mp_drawing.DrawingSpec(color=(255, 255, 255), thickness=1)

face_mesh = mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5)

cap = cv2.VideoCapture(0)

# --- MAIN LOOP ---
while cap.isOpened():
    success, image = cap.read()
    if not success:
        continue

    image = cv2.flip(image, 1)
    h, w, _ = image.shape
    
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(image_rgb)

    # We start with the original image
    output_image = image.copy()

    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            # Create a copy of the image to draw the black polygon on
            overlay = image.copy()
            
            # Get the ordered list of points for the face oval
            ordered_face_oval_indices = [
                10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288,
                397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150, 136,
                172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109, 10
            ]
            face_oval_points = []
            for idx in ordered_face_oval_indices:
                lm = face_landmarks.landmark[idx]
                face_oval_points.append([int(lm.x * w), int(lm.y * h)])
            face_oval_points = np.array(face_oval_points, dtype=np.int32)
            
            # 1. Draw the solid black polygon ON THE OVERLAY
            cv2.fillConvexPoly(overlay, face_oval_points, (0, 0, 0))
            
            # 2. Blend the overlay (with the black shape) back onto the original image
            alpha = 0.7
            output_image = cv2.addWeighted(overlay, alpha, output_image, 1 - alpha, 0)

            # 3. Draw the white mesh lines on top of the blended result
            mp_drawing.draw_landmarks(
                image=output_image,
                landmark_list=face_landmarks,
                connections=mp_face_mesh.FACEMESH_TESSELATION,
                landmark_drawing_spec=None,
                connection_drawing_spec=draw_spec_lines)
            
            mp_drawing.draw_landmarks(
                image=output_image,
                landmark_list=face_landmarks,
                connections=mp_face_mesh.FACEMESH_CONTOURS,
                landmark_drawing_spec=None,
                connection_drawing_spec=draw_spec_lines)

    cv2.imshow('Robot Face Mesh Effect', output_image)

    if cv2.waitKey(5) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()