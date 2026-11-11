import cv2
import mediapipe as mp
import numpy as np

# --- Helper Function to Define the Target Shape ---
def create_target_shape(points, width_scale=1.3, height_scale=1.1):
    """
    Creates destination points for morphing based on the bounding box of source points.
    It scales the bounding box and remaps the points to fit the new, larger box.
    """
    # Find the bounding box of the source points
    x_min, y_min = np.min(points, axis=0)
    x_max, y_max = np.max(points, axis=0)

    # Calculate the center of the bounding box
    center_x = (x_min + x_max) / 2
    center_y = (y_min + y_max) / 2

    # Original width and height
    width = x_max - x_min
    height = y_max - y_min

    # New scaled width and height
    new_width = width * width_scale
    new_height = height * height_scale

    # Create destination points by scaling each point from the center
    destination_points = []
    for x, y in points:
        # Normalize the point's position relative to the center
        norm_x = (x - center_x) / (width / 2)
        norm_y = (y - center_y) / (height / 2)

        # Scale to the new dimensions
        new_x = center_x + norm_x * (new_width / 2)
        new_y = center_y + norm_y * (new_height / 2)
        
        destination_points.append([new_x, new_y])

    return np.array(destination_points, dtype=np.float32)


# --- Main Application Setup ---
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1, min_detection_confidence=0.5)

cap = cv2.VideoCapture(0)

while cap.isOpened():
    success, image = cap.read()
    if not success:
        print("Ignoring empty camera frame.")
        continue

    # Flip the image horizontally for a later selfie-view display
    image = cv2.flip(image, 1)
    
    # To improve performance, optionally mark the image as not writeable
    image.flags.writeable = False
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(image_rgb)

    # Set it back to writeable so we can draw on it later
    image.flags.writeable = True

    output_image = image.copy()

    if results.multi_face_landmarks:
        for face_landmarks in results.multi_face_landmarks:
            h, w, _ = image.shape
            
            # --- 1. Select Source Landmarks (e.g., Jawline) ---
            # These indices trace the jaw, chin, and lower cheeks.
            jaw_indices = [61, 127, 234, 93, 132, 58, 172, 136, 150, 149, 176, 148, 152, 377, 400, 378, 379, 365, 397, 288, 361, 323, 454, 356, 291]
            
            source_points = []
            for idx in jaw_indices:
                lm = face_landmarks.landmark[idx]
                source_points.append([lm.x * w, lm.y * h])
            source_points = np.array(source_points, dtype=np.float32)

            # --- 2. Get Destination Points from our Helper Function ---
            destination_points = create_target_shape(source_points, width_scale=1.4, height_scale=1.1)

            # --- 3. Calculate Homography ---
            matrix, _ = cv2.findHomography(source_points, destination_points)

            # --- 4. Warp the Image ---
            warped_image = cv2.warpPerspective(image, matrix, (w, h))

            # --- 5. Create Mask and Blend Seamlessly ---
            # a. Create a mask for the source region
            mask = np.zeros_like(image, dtype=np.uint8)
            cv2.fillConvexPoly(mask, np.int32(source_points), (255, 255, 255))
            
            # b. Warp the mask to find the destination region
            warped_mask = cv2.warpPerspective(mask, matrix, (w, h))
            
            # c. Prepare the final output image
            # Create a hole in the original image where the warped face will go
            background = cv2.bitwise_and(image, cv2.bitwise_not(warped_mask))
            
            # Get only the warped face region
            foreground = cv2.bitwise_and(warped_image, warped_mask)
            
            # Combine the background and the warped foreground
            output_image = cv2.add(background, foreground)

    cv2.imshow('Live Face Morph', output_image)

    if cv2.waitKey(5) & 0xFF == 27:  # Press ESC to exit
        break

cap.release()
cv2.destroyAllWindows()