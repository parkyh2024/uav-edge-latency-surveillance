# Edge-Based UAV Surveillance Runtime Scripts

This repository provides the public implementation scripts used for the runtime-feasibility experiments in the manuscript:

**Stochastic Latency Decomposition and Constrained Runtime Feasibility Analysis for Edge-Based UAV Surveillance under Network-Denied Environments**

The scripts implement the integrated UAV surveillance pipeline used in the paper:

1. YOLO-based UAV detection
2. Kalman-filter-based object state smoothing
3. Track persistence under temporary missed detections
4. Anchor-distance-based threat assessment
5. Hysteresis-based danger-state transition
6. PIP magnified view, radar overlay, and flashing alert visualization
7. Per-frame latency logging for inference, processing, display/I/O, total latency, and FPS

## Repository contents

```text
.
├── detect_custom_radar.py          # Host PC / SSH X11-oriented runtime script
├── detect_custom_radar_Jetson.py   # Jetson AGX Orin-oriented runtime script
├── requirements.txt                # Minimal Python package requirements
├── example_config.md               # Example runtime settings and path placeholders
└── .gitignore                      # Excludes datasets, weights, videos, logs, and local environments
```

## Data and model availability

This repository does **not** include the author-constructed UAV image dataset, trained model weights, TensorRT engine files, or input videos.

These files are excluded because of data-use, storage, and institutional restrictions. They are available from the corresponding authors upon reasonable request, subject to applicable restrictions.

Expected local file examples:

```text
models/best.pt
models/best.engine
data/input_video.mp4
```

## Installation

Create a Python environment and install the required packages:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

For Jetson AGX Orin, PyTorch, CUDA, TensorRT, and OpenCV should be installed according to the JetPack/L4T environment. The `requirements.txt` file is provided as a minimal reference and may need to be adapted for Jetson-specific installations.

## Runtime configuration

The public scripts use environment variables to avoid exposing private local paths.

```bash
export UAV_MODEL_PATH=models/best.pt
export UAV_ENGINE_PATH=models/best.engine
export UAV_VIDEO_PATH=data/input_video.mp4
export UAV_TRACKER_CFG=bytetrack.yaml
export UAV_OUTPUT_DIR=logs
```

Optional device variable:

```bash
# Host PC
export UAV_DEVICE=0

# Jetson AGX Orin
export UAV_DEVICE=cuda:0
```

## Usage

### Host PC / SSH X11-oriented runtime

```bash
export UAV_MODEL_PATH=models/best.pt
export UAV_VIDEO_PATH=data/input_video.mp4
export UAV_DEVICE=0
python detect_custom_radar.py
```

### TensorRT engine on Host PC

```bash
export UAV_ENGINE_PATH=models/best.engine
export UAV_VIDEO_PATH=data/input_video.mp4
export UAV_DEVICE=0
python detect_custom_radar.py
```

Then select `2. TensorRT (.engine)` when prompted.

### Jetson AGX Orin-oriented runtime

```bash
export UAV_ENGINE_PATH=models/best.engine
export UAV_VIDEO_PATH=data/input_video.mp4
export UAV_DEVICE=cuda:0
python detect_custom_radar_Jetson.py
```

Then select `2. TensorRT (.engine)` when prompted.

## Anchor selection

By default, the first frame is displayed and the user selects the target anchor by clicking on the image and pressing the space bar.

## Runtime logs

Each run saves a CSV file in the `logs/` directory:

```text
logs/latency_log_YYYYMMDD_HHMMSS.csv
```

The CSV columns are:

```text
Frame, Inference(ms), Process(ms), Display(ms), Total(ms), FPS
```

These logs can be used to calculate mean latency, standard deviation, P95, P99, and other runtime stability metrics.

## Key parameters preserved from the manuscript implementation

```text
Inference input size: 1280
Tracking missing-frame tolerance: 15 frames
Approach threshold: 3 consecutive approach frames
Danger range: 0.8 normalized anchor distance
EMA smoothing coefficient for displayed latency values: 0.1
```

## Notes

This repository is intended to support reproducibility of the runtime pipeline structure and latency-logging procedure. It is not intended to redistribute the UAV dataset, trained weights, TensorRT engines, or experimental videos.
