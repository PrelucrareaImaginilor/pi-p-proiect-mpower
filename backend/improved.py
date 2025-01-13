import cv2 as cv
import numpy as np
import os
import math
import time
from tqdm import tqdm
from dataclasses import dataclass
from typing import List, Dict
from collections import deque

@dataclass
class VehicleStats:
    vehicle_id: int
    speeds: List[float] = None
    max_speed: float = 0
    min_speed: float = float('inf')
    avg_speed: float = 0
    current_speed: float = 0
    
    def __init__(self, vehicle_id):
        self.vehicle_id = vehicle_id
        self.speeds = []
    
    def update_speed(self, speed):
        self.current_speed = speed
        self.speeds.append(speed)
        self.max_speed = max(self.max_speed, speed)
        self.min_speed = min(self.min_speed, speed) if speed > 0 else self.min_speed
        self.avg_speed = sum(self.speeds) / len(self.speeds)

class SpeedTracker:
    def __init__(self, fps, reference_distance_meters=20.0, reference_pixels=100):
        self.fps = fps
        self.pixels_per_meter = reference_pixels / reference_distance_meters
        self.speed_history = {}
        self.position_history = {}
        self.vehicle_stats: Dict[int, VehicleStats] = {}
        self.SPEED_WINDOW = 5
        self.STOPPED_THRESHOLD = 3.0

    def get_vehicle_stats(self, vehicle_id):
        if vehicle_id not in self.vehicle_stats:
            self.vehicle_stats[vehicle_id] = VehicleStats(vehicle_id)
        return self.vehicle_stats[vehicle_id]

    def initialize_vehicle(self, vehicle_id):
        self.speed_history[vehicle_id] = deque(maxlen=self.SPEED_WINDOW)
        self.position_history[vehicle_id] = deque(maxlen=3)
        self.get_vehicle_stats(vehicle_id)

    def calculate_speed(self, vehicle_id, current_pos):
        if vehicle_id not in self.speed_history:
            self.initialize_vehicle(vehicle_id)

        self.position_history[vehicle_id].append(current_pos)

        if len(self.position_history[vehicle_id]) < 2:
            return 0.0

        prev_pos = self.position_history[vehicle_id][-2]
        dx = (current_pos[0] - prev_pos[0]) / self.pixels_per_meter
        dy = (current_pos[1] - prev_pos[1]) / self.pixels_per_meter
        distance = math.sqrt(dx*dx + dy*dy)

        speed = (distance / (1.0/self.fps)) * 3.6  # km/h

        self.speed_history[vehicle_id].append(speed)
        smoothed_speed = np.mean(self.speed_history[vehicle_id])
        
        if smoothed_speed < self.STOPPED_THRESHOLD:
            smoothed_speed = 0.0

        # Update vehicle statistics
        stats = self.get_vehicle_stats(vehicle_id)
        stats.update_speed(smoothed_speed)

        return round(smoothed_speed, 1)

    def generate_report(self):
        return [
            {
                'car_id': stats.vehicle_id,
                'max_speed': round(stats.max_speed, 1),
                'min_speed': round(stats.min_speed, 1),
                'avg_speed': round(stats.avg_speed, 1)
            }
            for stats in self.vehicle_stats.values()
        ]

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


def process_video(video_path):
    output_dir = 'output'
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'processed_' + os.path.basename(video_path))
    
    cap = cv.VideoCapture(video_path)
    total_frames = int(cap.get(cv.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv.CAP_PROP_FPS)
    width = int(cap.get(cv.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))
    
    fourcc = cv.VideoWriter_fourcc(*'mp4v')
    out = cv.VideoWriter(output_path, fourcc, fps, (width, height))
    
    speed_tracker = SpeedTracker(fps=fps)
    next_vehicle_id = 0
    prev_positions = {}

    print(f"\nProcessing video: {video_path}")
    print(f"Output will be saved to: {output_path}")
    
    for frame_idx in tqdm(range(total_frames), desc="Processing"):
        ret, frame = cap.read()
        if not ret:
            break

        boxes = detect_vehicles(frame)
        frame_copy = frame.copy()
        
        for box in boxes:
            x, y, w, h = box
            center = (x + w//2, y + h//2)
            
            min_dist = float('inf')
            matching_id = None
            
            for vid, prev_pos in prev_positions.items():
                dist = math.sqrt((center[0] - prev_pos[0])**2 + (center[1] - prev_pos[1])**2)
                if dist < min_dist and dist < 100:
                    min_dist = dist
                    matching_id = vid
            
            if matching_id is None:
                matching_id = next_vehicle_id
                next_vehicle_id += 1
            
            speed = speed_tracker.calculate_speed(matching_id, center)
            prev_positions[matching_id] = center
            
            # Draw annotations with ID
            cv.rectangle(frame_copy, (x, y), (x + w, y + h), (0, 255, 0), 2)
            text = f"ID:{matching_id} - {speed:.1f} km/h"
            cv.putText(frame_copy, text, (x, y-10), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        out.write(frame_copy)

    cap.release()
    out.release()

    # Generate and save report
    report = speed_tracker.generate_report()
    report_path = os.path.join(output_dir, 'vehicle_stats.txt')
    
    with open(report_path, 'w') as f:
        f.write("Vehicle Statistics Report\n")
        f.write("======================\n\n")
        for vehicle in report:
            f.write(f"Vehicle ID: {vehicle['car_id']}\n")
            f.write(f"Maximum Speed: {vehicle['max_speed']} km/h\n")
            f.write(f"Minimum Speed: {vehicle['min_speed']} km/h\n")
            f.write(f"Average Speed: {vehicle['avg_speed']} km/h\n")
            f.write("----------------------\n")
    
    print(f"\nProcessing complete!")
    print(f"Processed video saved to: {output_path}")
    print(f"Statistics report saved to: {report_path}")

if __name__ == '__main__':
    video_path = 'recording.mp4'
    
    if not os.path.exists(video_path):
        print(f"Error: Video file not found at {video_path}")
    else:
        try:
            process_video(video_path)
        except Exception as e:
            print(f"Error processing video: {e}")