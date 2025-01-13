import cv2 as cv
import numpy as np
import os
import math
import time
from tqdm import tqdm

# Define paths
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(CURRENT_DIR, 'models')
WEIGHTS_PATH = os.path.join(MODEL_DIR, 'yolov4.weights')
CFG_PATH = os.path.join(MODEL_DIR, 'yolov4.cfg')

# Verify files exist
if not os.path.exists(WEIGHTS_PATH) or not os.path.exists(CFG_PATH):
    raise FileNotFoundError(f"YOLO files missing. Please ensure files exist at:\n{WEIGHTS_PATH}\n{CFG_PATH}")

# Load YOLO
try:
    net = cv.dnn.readNet(WEIGHTS_PATH, CFG_PATH)
    layer_names = net.getLayerNames()
    output_layers = [layer_names[i - 1] for i in net.getUnconnectedOutLayers()]
except Exception as e:
    print(f"Error loading YOLO model: {e}")
    raise

def detect_vehicles(frame):
    height, width = frame.shape[:2]
    blob = cv.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
    net.setInput(blob)
    outs = net.forward(output_layers)

    boxes = []
    confidences = []
    class_ids = []

    for out in outs:
        for detection in out:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > 0.5 and class_id == 2:  # class_id 2 for cars
                center_x = int(detection[0] * width)
                center_y = int(detection[1] * height)
                w = int(detection[2] * width)
                h = int(detection[3] * height)
                x = int(center_x - w / 2)
                y = int(center_y - h / 2)
                boxes.append([x, y, w, h])
                confidences.append(float(confidence))
                class_ids.append(class_id)

    indexes = cv.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
    return [boxes[i] for i in indexes]

def calculate_speed(prev_pos, curr_pos, fps):
    pixels_per_meter = 30  # This value needs calibration for your specific scenario
    
    dx = (curr_pos[0] - prev_pos[0]) / pixels_per_meter
    dy = (curr_pos[1] - prev_pos[1]) / pixels_per_meter
    
    distance = math.sqrt(dx*dx + dy*dy)
    time = 1/fps
    speed = distance/time * 3.6  # Convert to km/h
    
    return speed

def process_video(video_path):
    # Create output directory if it doesn't exist
    output_dir = 'output'
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate output path
    output_path = os.path.join(output_dir, 'processed_' + os.path.basename(video_path))
    
    # Open video
    cap = cv.VideoCapture(video_path)
    total_frames = int(cap.get(cv.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv.CAP_PROP_FPS)
    width = int(cap.get(cv.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))
    
    # Create video writer
    fourcc = cv.VideoWriter_fourcc(*'mp4v')
    out = cv.VideoWriter(output_path, fourcc, fps, (width, height))
    
    # Tracking dictionaries
    prev_positions = {}
    vehicle_speeds = {}
    next_vehicle_id = 0

    print(f"\nProcessing video: {video_path}")
    print(f"Output will be saved to: {output_path}")
    
    # Process frames with progress bar
    for frame_idx in tqdm(range(total_frames), desc="Processing"):
        ret, frame = cap.read()
        if not ret:
            break

        # Detect and process vehicles
        boxes = detect_vehicles(frame)
        frame_copy = frame.copy()
        
        for box in boxes:
            x, y, w, h = box
            center = (x + w//2, y + h//2)
            
            # Find closest vehicle from previous frame
            min_dist = float('inf')
            matching_id = None
            
            for vid, prev_pos in prev_positions.items():
                dist = math.sqrt((center[0] - prev_pos[0])**2 + (center[1] - prev_pos[1])**2)
                if dist < min_dist and dist < 100:  # threshold for matching
                    min_dist = dist
                    matching_id = vid
            
            if matching_id is None:
                matching_id = next_vehicle_id
                next_vehicle_id += 1
                vehicle_speeds[matching_id] = 0
            else:
                speed = calculate_speed(prev_positions[matching_id], center, fps)
                vehicle_speeds[matching_id] = speed
            
            prev_positions[matching_id] = center
            
            # Draw annotations
            cv.rectangle(frame_copy, (x, y), (x + w, y + h), (0, 255, 0), 2)
            speed_text = f"{vehicle_speeds[matching_id]:.1f} km/h"
            cv.putText(frame_copy, speed_text, (x, y-10), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        # Write frame
        out.write(frame_copy)

    # Release resources
    cap.release()
    out.release()
    
    print(f"\nProcessing complete!")
    print(f"Processed video saved to: {output_path}")

if __name__ == '__main__':
    video_path = 'video.mp4'
    
    if not os.path.exists(video_path):
        print(f"Error: Video file not found at {video_path}")
    else:
        try:
            process_video(video_path)
        except Exception as e:
            print(f"Error processing video: {e}")