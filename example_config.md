# Example Runtime Configuration

This file is not executed by Python. It documents example runtime settings so that reviewers and readers can understand the runtime configuration without exposing local file paths, private datasets, trained model files, or full evaluation videos.

## 1. Common Paths

Replace these paths with your local files when reproducing the full experimental setup.

```text
Model path, PyTorch: models/best.pt
Model path, TensorRT: models/best.engine
Input video, sample demonstration: sample_data/sample_input_video.mp4
Tracker configuration: bytetrack.yaml
Output log directory: logs/
```

The trained model weights, TensorRT engine files, full UAV dataset, and full evaluation videos are not included in this repository due to institutional and data-use restrictions.

## 2. Environment Variables

The scripts use environment variables so that private paths do not need to be hard-coded.

```bash
export UAV_MODEL_PATH="models/best.pt"
export UAV_ENGINE_PATH="models/best.engine"
export UAV_VIDEO_PATH="sample_data/sample_input_video.mp4"
export UAV_TRACKER_CFG="bytetrack.yaml"
export UAV_OUTPUT_DIR="logs"
```

If these variables are not set, the scripts use placeholder default paths.

## 3. Runtime Conditions

### Host PC / SSH X11 Display-Path Proxy Runtime

```bash
export UAV_MODEL_PATH="models/best.pt"
export UAV_VIDEO_PATH="sample_data/sample_input_video.mp4"
export UAV_DEVICE="0"
python detect_custom_radar.py
```

During execution, select the display resolution and model format when prompted.

### Host PC with TensorRT Engine

```bash
export UAV_ENGINE_PATH="models/best.engine"
export UAV_VIDEO_PATH="sample_data/sample_input_video.mp4"
export UAV_DEVICE="0"
python detect_custom_radar.py
```

Select `2. TensorRT (.engine)` when prompted.

### Jetson AGX Orin Local Edge Runtime

```bash
export UAV_ENGINE_PATH="models/best.engine"
export UAV_VIDEO_PATH="sample_data/sample_input_video.mp4"
export UAV_DEVICE="cuda:0"
python detect_custom_radar_Jetson.py
```

Select `2. TensorRT (.engine)` when prompted.

## 4. Sample Input Video

A short representative sample input video clip is provided at:

```text
sample_data/sample_input_video.mp4
```

This sample clip is provided only for code-execution demonstration and pipeline-format verification. It does not replace the full evaluation videos used for the quantitative runtime results reported in the manuscript.

## 5. Threat-Assessment Parameters

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

## 6. Output CSV Format

The scripts save per-frame latency logs with the following columns:

```text
Frame, Inference(ms), Process(ms), Display(ms), Total(ms), FPS
```

These logs can be used for mean/std analysis and tail-latency analysis such as P95 and P99.
