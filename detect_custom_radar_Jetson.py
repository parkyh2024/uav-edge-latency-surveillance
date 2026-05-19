"""
Public reproduction script for the edge-based UAV surveillance runtime experiments.

This public version preserves the detection-tracking-alert-visualization-latency
logging logic used in the manuscript while replacing local file paths with
environment-variable-based placeholders.

The repository does not include model weights, TensorRT engines, UAV datasets,
or input videos. Place those files locally and configure the paths below via
environment variables or by editing the default constants.
"""

import cv2
import numpy as np
import time
import os
import csv
from datetime import datetime
from ultralytics import YOLO
from typing import Optional, Tuple, Dict, List, Set

class KalmanBoxSmoother:
    def __init__(self):
        self.kf = cv2.KalmanFilter(8, 4)
        self.kf.measurementMatrix = np.eye(4, 8, dtype=np.float32)
        self.kf.transitionMatrix = np.eye(8, dtype=np.float32)
        
        for i in range(4):
            self.kf.transitionMatrix[i, i+4] = 1.0
            
        self.kf.processNoiseCov = np.eye(8, dtype=np.float32) * 1e-2
        self.kf.measurementNoiseCov = np.eye(4, dtype=np.float32) * 1e-1
        self.kf.errorCovPost = np.eye(8, dtype=np.float32)
        self.initialized = False

    def update(self, bbox: Tuple[int, int, int, int]) -> Tuple[int, int, int, int]:
        x1, y1, x2, y2 = bbox
        cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
        w, h = x2 - x1, y2 - y1
        measurement = np.array([[np.float32(cx)], [np.float32(cy)], [np.float32(w)], [np.float32(h)]])

        if not self.initialized:
            self.kf.statePost = np.array([
                [cx], [cy], [w], [h],
                [0], [0], [0], [0]
            ], dtype=np.float32)
            self.initialized = True
            return x1, y1, x2, y2

        self.kf.predict()
        prediction = self.kf.correct(measurement)
        return self._post_process(prediction)

    def predict_only(self) -> Tuple[int, int, int, int]:
        prediction = self.kf.predict()
        return self._post_process(prediction)

    def _post_process(self, prediction) -> Tuple[int, int, int, int]:
        pred_cx, pred_cy = prediction[0], prediction[1]
        pred_w, pred_h = prediction[2], prediction[3]
        
        nx1 = int(pred_cx - pred_w / 2)
        ny1 = int(pred_cy - pred_h / 2)
        nx2 = int(pred_cx + pred_w / 2)
        ny2 = int(pred_cy + pred_h / 2)
        return nx1, ny1, nx2, ny2

class DroneTrack:
    MAX_MISS_TOLERANCE = 15
    APPROACH_THRESHOLD = 3
    DANGER_RANGE = 0.8

    def __init__(self, track_id: int, initial_box: Tuple[int, int, int, int]):
        self.track_id = track_id
        self.smoother = KalmanBoxSmoother()
        self.current_box = self.smoother.update(initial_box)
        
        self.miss_count = 0
        self.approach_streak = 0
        self.prev_offset: Optional[float] = None
        self.is_danger = False
        self.last_seen_tick = 0

    def update(self, raw_box: Tuple[int, int, int, int], anchor_dist: float, tick: int):
        self.current_box = self.smoother.update(raw_box)
        self.miss_count = 0
        self.last_seen_tick = tick
        
        if self.prev_offset is not None and anchor_dist < self.prev_offset:
            self.approach_streak += 1
        else:
            self.approach_streak = 0
            
        self.is_danger = (self.approach_streak >= self.APPROACH_THRESHOLD) and (anchor_dist < self.DANGER_RANGE)
        self.prev_offset = anchor_dist

    def coast(self):
        self.current_box = self.smoother.predict_only()
        self.miss_count += 1

    def is_dead(self) -> bool:
        return self.miss_count > self.MAX_MISS_TOLERANCE

class DroneSurveillanceSystem:
    DEFAULT_MODEL = os.environ.get("UAV_MODEL_PATH", "models/best.pt")
    VIDEO_SOURCE = os.environ.get("UAV_VIDEO_PATH", "data/input_video.mp4")
    INFERENCE_SIZE = 1280
    
    PIP_W, PIP_H = 200, 150
    PIP_BG_COLOR = (0, 0, 0)
    PIP_BORDER_COLOR = (255, 255, 255)
    
    RADAR_SIZE = 120
    RADAR_SCALE = 0.11
    RADAR_BG_COLOR = (0, 20, 0)
    
    COLOR_BLUE = (255, 0, 0)
    COLOR_RED = (0, 0, 255)
    COLOR_GREEN = (0, 255, 0)
    
    ALPHA = 0.1

    def __init__(self):
        self.target_anchor: Optional[Tuple[int, int]] = None
        self.view_scale = 1.0
        self.viewer_width = 720
        self.model = None
        self.model_path = self.DEFAULT_MODEL
        
        self.tracks: Dict[int, DroneTrack] = {}
        self.frame_count = 0
        self.last_valid_pip: Optional[np.ndarray] = None
        
        self.metrics = {
            'infer': 0.0, 'proc': 0.0, 'disp': 0.0, 'total': 0.0
        }

        self.latency_log = []
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = os.environ.get("UAV_OUTPUT_DIR", "logs")
        os.makedirs(output_dir, exist_ok=True)
        self.csv_filename = os.path.join(output_dir, f"latency_log_{timestamp}.csv")

    def _mouse_callback(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            orig_x = int(x / self.view_scale)
            orig_y = int(y / self.view_scale)
            self.target_anchor = (orig_x, orig_y)
            print(f"Target Anchor Set: Original({orig_x}, {orig_y})")

    def setup_system(self):
        print("\n=== Resolution Selection ===")
        print("1. SD (720)\n2. HD (1280)\n3. FHD (1920)")
        res = input("Select Resolution (1-3): ").strip()
        self.viewer_width = { '2': 1280, '3': 1920 }.get(res, 720)

        print("\n=== Model Format Selection ===")
        print("1. PyTorch (.pt)\n2. TensorRT (.engine)")
        if input("Select Model (1-2): ").strip() == '2':
            self.model_path = os.environ.get("UAV_ENGINE_PATH", "models/best.engine")

        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Model file '{self.model_path}' not found.")

        self._select_anchor_gui()
        self.model = YOLO(self.model_path)

    def _select_anchor_gui(self):
        if not os.path.exists(self.VIDEO_SOURCE):
            return

        cap = cv2.VideoCapture(self.VIDEO_SOURCE)
        ret, frame = cap.read()
        cap.release()

        if not ret:
            return

        h, w = frame.shape[:2]
        self.view_scale = self.viewer_width / w
        disp_h = int(h * self.view_scale)
        
        win_name = "Set Target Anchor"
        cv2.namedWindow(win_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(win_name, self.viewer_width, disp_h)
        cv2.setMouseCallback(win_name, self._mouse_callback)

        display_base = cv2.resize(frame, (self.viewer_width, disp_h))

        while True:
            display = display_base.copy()
            cv2.putText(display, "Click Target & Press Space", (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, self.COLOR_GREEN, 2)
            
            if self.target_anchor:
                ax, ay = self.target_anchor
                dx, dy = int(ax * self.view_scale), int(ay * self.view_scale)
                cv2.drawMarker(display, (dx, dy), self.COLOR_RED, cv2.MARKER_CROSS, 20, 2)

            cv2.imshow(win_name, display)
            if cv2.waitKey(10) & 0xFF == 32:
                break
        
        cv2.destroyWindow(win_name)

    def _calc_offset(self, cx: int, cy: int, img_w: int, img_h: int) -> float:
        tx, ty = self.target_anchor if self.target_anchor else (img_w / 2, img_h / 2)
        norm_dx = (cx - tx) / img_w
        norm_dy = (cy - ty) / img_h
        return np.hypot(norm_dx, norm_dy)

    def _extract_pip(self, frame: np.ndarray, bbox: Optional[Tuple[int, int, int, int]]) -> Optional[np.ndarray]:
        if bbox is None:
            return None

        x1, y1, x2, y2 = bbox
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
        
        box_dim = max(x2 - x1, y2 - y1)
        src_w = max(box_dim * 1.5, 50)
        src_h = src_w * (self.PIP_H / self.PIP_W)
        
        h, w = frame.shape[:2]
        crop_x1 = max(0, int(cx - src_w / 2))
        crop_y1 = max(0, int(cy - src_h / 2))
        crop_x2 = min(w, int(crop_x1 + src_w))
        crop_y2 = min(h, int(crop_y1 + src_h))

        if crop_x2 <= crop_x1 or crop_y2 <= crop_y1:
            return None
            
        crop = frame[crop_y1:crop_y2, crop_x1:crop_x2]
        return cv2.resize(crop, (self.PIP_W, self.PIP_H))

    def _draw_radar(self, display: np.ndarray, primary_track: Optional[DroneTrack]):
        radar = np.full((self.RADAR_SIZE, self.RADAR_SIZE, 3), self.RADAR_BG_COLOR, dtype=np.uint8)
        center = self.RADAR_SIZE // 2
        
        cv2.circle(radar, (center, center), int(self.RADAR_SIZE * 0.3), (0, 50, 0), 1)
        cv2.circle(radar, (center, center), int(self.RADAR_SIZE * 0.6), (0, 50, 0), 1)
        cv2.line(radar, (center, 0), (center, self.RADAR_SIZE), (0, 50, 0), 1)
        cv2.line(radar, (0, center), (self.RADAR_SIZE, center), (0, 50, 0), 1)
        cv2.drawMarker(radar, (center, center), self.COLOR_GREEN, cv2.MARKER_CROSS, 8, 1)

        if primary_track and self.target_anchor:
            x1, y1, x2, y2 = primary_track.current_box
            cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
            ax, ay = self.target_anchor
            
            dx = (cx - ax) * self.RADAR_SCALE
            dy = (cy - ay) * self.RADAR_SCALE
            
            rx = int(center + dx)
            ry = int(center + dy)
            
            rx = np.clip(rx, 3, self.RADAR_SIZE - 3)
            ry = np.clip(ry, 3, self.RADAR_SIZE - 3)
            
            color = self.COLOR_RED if primary_track.is_danger else self.COLOR_BLUE
            cv2.circle(radar, (rx, ry), 4, color, -1)
            cv2.line(radar, (center, center), (rx, ry), (100, 100, 100), 1)

        h, w = display.shape[:2]
        pad = 20
        x_offset = w - self.RADAR_SIZE - pad
        y_offset = h - self.RADAR_SIZE - pad
        
        roi = display[y_offset:y_offset+self.RADAR_SIZE, x_offset:x_offset+self.RADAR_SIZE]
        combined = cv2.addWeighted(roi, 0.3, radar, 0.7, 0)
        display[y_offset:y_offset+self.RADAR_SIZE, x_offset:x_offset+self.RADAR_SIZE] = combined
        cv2.rectangle(display, (x_offset, y_offset), (x_offset+self.RADAR_SIZE, y_offset+self.RADAR_SIZE), (255, 255, 255), 1)

    def _update_metrics(self, infer_t, proc_t, disp_t, total_t):
        raw_fps = 1000.0 / total_t if total_t > 0 else 0.0
        
        self.latency_log.append([
            self.frame_count, 
            round(infer_t, 1), 
            round(proc_t, 1), 
            round(disp_t, 1), 
            round(total_t, 1), 
            round(raw_fps, 1)
        ])

        if self.frame_count == 0:
            self.metrics['infer'] = infer_t
            self.metrics['proc'] = proc_t
            self.metrics['disp'] = disp_t
            self.metrics['total'] = total_t
        else:
            self.metrics['infer'] = (1 - self.ALPHA) * self.metrics['infer'] + self.ALPHA * infer_t
            self.metrics['proc'] = (1 - self.ALPHA) * self.metrics['proc'] + self.ALPHA * proc_t
            self.metrics['disp'] = (1 - self.ALPHA) * self.metrics['disp'] + self.ALPHA * disp_t
            self.metrics['total'] = (1 - self.ALPHA) * self.metrics['total'] + self.ALPHA * total_t

        print(f"[Frame {self.frame_count:04d}] Inference: {self.metrics['infer']:.1f}ms | "
              f"Process: {self.metrics['proc']:.1f}ms | "
              f"Display: {self.metrics['disp']:.1f}ms | "
              f"Total: {self.metrics['total']:.1f}ms ({1000/self.metrics['total']:.1f} FPS)")

    def _save_logs(self):
        if not self.latency_log:
            print("\n[System] No data to save.")
            return

        try:
            with open(self.csv_filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Frame', 'Inference(ms)', 'Process(ms)', 'Display(ms)', 'Total(ms)', 'FPS'])
                writer.writerows(self.latency_log)
            print(f"\n[System] Latency log saved successfully: {self.csv_filename}")
        except Exception as e:
            print(f"\n[Error] Failed to save log: {e}")

    def run(self):
        self.setup_system()
        
        results_gen = self.model.track(
            source=self.VIDEO_SOURCE,
            imgsz=self.INFERENCE_SIZE,
            conf=0.10,
            persist=True,
            device=os.environ.get("UAV_DEVICE", "cuda:0"),
            half=True,
            stream=True,
            verbose=False,
            tracker=os.environ.get("UAV_TRACKER_CFG", "bytetrack.yaml")
        )

        win_name = "Drone Detection System"
        cv2.namedWindow(win_name, cv2.WINDOW_NORMAL)

        try:
            while True:
                t0 = time.perf_counter()
                
                try:
                    result = next(results_gen)
                except StopIteration:
                    break
                    
                t1 = time.perf_counter()

                annotated = result.orig_img.copy()
                fh, fw = annotated.shape[:2]
                
                if self.target_anchor:
                    cv2.drawMarker(annotated, self.target_anchor, self.COLOR_GREEN, cv2.MARKER_CROSS, 30, 2)

                detected_ids = set()
                primary_track = None
                min_dist = float('inf')

                if result.boxes and result.boxes.id is not None:
                    ids = result.boxes.id.cpu().numpy().astype(int)
                    boxes = result.boxes.xyxy.cpu().numpy().astype(int)
                    
                    for tid, box in zip(ids, boxes):
                        detected_ids.add(tid)
                        cx = (box[0] + box[2]) / 2
                        cy = (box[1] + box[3]) / 2
                        dist = self._calc_offset(cx, cy, fw, fh)

                        if tid not in self.tracks:
                            self.tracks[tid] = DroneTrack(tid, box)
                        
                        track = self.tracks[tid]
                        track.update(box, dist, self.frame_count)

                        if track.is_danger:
                            min_dist = -1.0 
                            primary_track = track
                        elif dist < min_dist:
                            min_dist = dist
                            primary_track = track

                dead_ids = []
                for tid, track in self.tracks.items():
                    if tid not in detected_ids:
                        track.coast()
                        if track.is_dead():
                            dead_ids.append(tid)
                    
                    sx1, sy1, sx2, sy2 = track.current_box
                    color = self.COLOR_RED if track.is_danger else self.COLOR_BLUE
                    
                    if track.miss_count > 0:
                        color = (128, 128, 128) 

                    cv2.rectangle(annotated, (sx1, sy1), (sx2, sy2), color, 2)

                for tid in dead_ids:
                    del self.tracks[tid]

                self.view_scale = self.viewer_width / fw
                disp_h = int(fh * self.view_scale)
                final_disp = cv2.resize(annotated, (self.viewer_width, disp_h))
                
                if self.frame_count == 0:
                    cv2.resizeWindow(win_name, self.viewer_width, disp_h)

                has_danger = any(t.is_danger for t in self.tracks.values())
                if has_danger and (self.frame_count % 10 < 5):
                    cv2.rectangle(final_disp, (0, 0), (self.viewer_width, disp_h), self.COLOR_RED, 10)

                pip_source_box = primary_track.current_box if primary_track else None
                pip_img = self._extract_pip(result.orig_img, pip_source_box)

                if pip_img is not None:
                    self.last_valid_pip = pip_img
                elif self.last_valid_pip is not None:
                    gray = cv2.cvtColor(self.last_valid_pip, cv2.COLOR_BGR2GRAY)
                    pip_img = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
                else:
                    pip_img = np.zeros((self.PIP_H, self.PIP_W, 3), dtype=np.uint8)

                x_off = self.viewer_width - self.PIP_W
                final_disp[0:self.PIP_H, x_off:self.viewer_width] = pip_img
                cv2.rectangle(final_disp, (x_off, 0), (self.viewer_width, self.PIP_H), self.PIP_BORDER_COLOR, 1)

                self._draw_radar(final_disp, primary_track)

                t2 = time.perf_counter()

                cv2.imshow(win_name, final_disp)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

                t3 = time.perf_counter()
                self._update_metrics(
                    (t1 - t0) * 1000, 
                    (t2 - t1) * 1000, 
                    (t3 - t2) * 1000, 
                    (t3 - t0) * 1000
                )
                self.frame_count += 1

        finally:
            self._save_logs()
            cv2.destroyAllWindows()

if __name__ == "__main__":
    system = DroneSurveillanceSystem()
    system.run()
