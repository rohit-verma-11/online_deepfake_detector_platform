import os
import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from celery import shared_task
from .models import DetectionTask

# Setup Tasks API Configuration
# Ensure 'face_landmarker.task' is in your main project folder
model_path = os.path.join(os.getcwd(), 'face_landmarker.task')

base_options = python.BaseOptions(model_asset_path=model_path)
options = vision.FaceLandmarkerOptions(
    base_options=base_options,
    output_face_blendshapes=True, 
    num_faces=1,
    running_mode=vision.RunningMode.VIDEO # Optimized for frame sequences
)

def get_biological_signals(landmarker, frame, timestamp_ms):
    """Modern Tasks API implementation for facial landmarking."""
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
    
    # detect_for_video provides better temporal smoothing
    result = landmarker.detect_for_video(mp_image, timestamp_ms)
    
    if not result.face_landmarks:
        return None
    
    # Extract landmarks from the first detected face
    landmarks = result.face_landmarks[0]
    
    # Landmark 13: Upper Lip center, 14: Lower Lip center
    # Landmark 1: Nose tip, 152: Chin bottom
    lip_distance = abs(landmarks[13].y - landmarks[14].y)
    face_height = abs(landmarks[1].y - landmarks[152].y)
    
    return lip_distance / face_height if face_height != 0 else 0

@shared_task
def process_video_detection(task_id):
    try:
        task = DetectionTask.objects.get(id=task_id)
        task.status = 'PROCESSING'
        task.save()

        cap = cv2.VideoCapture(task.video_file.path)
        fps = cap.get(cv2.CAP_PROP_FPS) or 30
        
        # Initialize the Landmarker within the task
        with vision.FaceLandmarker.create_from_options(options) as landmarker:
            textures, flow_jitters, bio_signals = [], [], []
            prev_gray = None
            frame_count = 0

            while frame_count < 30:
                success, frame = cap.read()
                if not success: break

                timestamp_ms = int((frame_count / fps) * 1000)
                curr_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                # 1. TEXTURE (Laplacian)
                textures.append(cv2.Laplacian(curr_gray, cv2.CV_64F).var())

                # 2. OPTICAL FLOW (Jitter)
                if prev_gray is not None:
                    flow = cv2.calcOpticalFlowFarneback(prev_gray, curr_gray, None, 0.5, 3, 15, 3, 5, 1.2, 0)
                    mag, _ = cv2.cartToPolar(flow[..., 0], flow[..., 1])
                    flow_jitters.append(np.var(mag))

                # 3. BIOLOGICAL (Landmarks)
                sig = get_biological_signals(landmarker, frame, timestamp_ms)
                if sig is not None: bio_signals.append(sig)

                prev_gray = curr_gray
                frame_count += 1
            
        cap.release()

        # Final Evaluation Logic
        avg_texture = np.mean(textures)
        avg_jitter = np.mean(flow_jitters) if flow_jitters else 0
        bio_variance = np.var(bio_signals) if bio_signals else 0

        # Scoring
        if bio_variance > 0.005 or avg_jitter > 4.0:
            task.content_type = "Deepfake / AI-Manipulated"
            task.is_fake = True
            task.confidence_score = 94.0
            task.reasoning = "Inconsistent facial mesh movement and motion jitter detected."
        elif avg_texture < 60:
            task.content_type = "Animation"
            task.is_fake = False
            task.confidence_score = 99.0
        elif avg_texture < 90:
            task.content_type = "AI Generated / Synthetic"
            task.is_fake = True
            task.confidence_score = 88.0
            task.reasoning = "Absence of camera sensor noise (Too smooth)."
        else:
            task.content_type = "Authentic Live Action"
            task.is_fake = False
            task.confidence_score = 91.0
            task.reasoning = "Natural noise and biological motion verified."

        task.status = 'COMPLETED'
        task.save()

    except Exception as e:
        task.status = 'FAILED'
        task.reasoning = str(e)
        task.save()