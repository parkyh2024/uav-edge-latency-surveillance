# Example Runtime Configuration

This file is not executed by Python. It documents example runtime settings so that reviewers and readers can reproduce the configuration logic without exposing local file paths, private datasets, or trained model files.

## 1. Common paths

Replace these paths with your local files.

```text
Model path, PyTorch: models/best.pt
Model path, TensorRT: models/best.engine
Input video: data/input_video.mp4
Tracker configuration: bytetrack.yaml
Output log directory: logs/
```

The model weights, TensorRT engine files, dataset, and input videos are not included in this repository.

## 2. Environment variables

```bash
export UAV_MODEL_PATH=models/best.pt
export UAV_ENGINE_PATH=models/best.engine
export UAV_VIDEO_PATH=data/input_video.mp4
export UAV_TRACKER_CFG=bytetrack.yaml
export UAV_OUTPUT_DIR=logs
```

## 3. Runtime conditions

### Host PC / SSH X11-style runtime

```bash
export UAV_MODEL_PATH=models/best.pt
export UAV_VIDEO_PATH=data/input_video.mp4
export UAV_DEVICE=0
python detect_custom_radar.py
```

### Host PC with TensorRT engine

```bash
export UAV_ENGINE_PATH=models/best.engine
export UAV_VIDEO_PATH=data/input_video.mp4
export UAV_DEVICE=0
python detect_custom_radar.py
```

Select `2. TensorRT (.engine)` when prompted.

### Jetson AGX Orin-style runtime

```bash
export UAV_ENGINE_PATH=models/best.engine
export UAV_VIDEO_PATH=data/input_video.mp4
export UAV_DEVICE=cuda:0
python detect_custom_radar_Jetson.py
```

Select `2. TensorRT (.engine)` when prompted.

## 4. Threat-assessment parameters

The public scripts preserve the following implementation parameters:

```text
MAX_MISS_TOLERANCE = 15
APPROACH_THRESHOLD = 3
DANGER_RANGE = 0.8
```

The danger state is activated when:

```text
approach_streak >= 3
and normalized_anchor_distance < 0.8
```

## 5. Output CSV format

The scripts save per-frame latency logs with the following columns:

```text
Frame, Inference(ms), Process(ms), Display(ms), Total(ms), FPS
```

These logs can be used for mean/std analysis and tail-latency analysis such as P95 and P99.
