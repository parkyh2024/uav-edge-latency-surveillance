# UAV Edge Latency Surveillance

This repository provides the public implementation scripts used for the runtime-feasibility experiments reported in the manuscript:

**Stochastic Latency Decomposition and Constrained Runtime Feasibility Analysis for Edge-Based UAV Surveillance under Network-Denied Environments**

The repository is provided to improve implementation transparency and reproducibility for the video-based UAV surveillance pipeline. The implementation includes object detection, object tracking, threat assessment, visualization, and per-frame latency logging.

## Repository Structure

```text
uav-edge-latency-surveillance/
├── detect_custom_radar.py
├── detect_custom_radar_Jetson.py
├── requirements.txt
├── example_config.md
├── README.md
├── .gitignore
└── sample_data/
    ├── README.md
    └── sample_input_video.mp4
```

## Files

| File | Description |
|---|---|
| `detect_custom_radar.py` | Runtime script used for the Host PC / SSH X11 display-path proxy condition. |
| `detect_custom_radar_Jetson.py` | Runtime script used for the Jetson AGX Orin local edge-execution condition. |
| `requirements.txt` | Minimal Python package requirements. |
| `example_config.md` | Example runtime configuration and environment-variable usage. |
| `Sample_Video.mp4` | Short representative sample input video clip for demonstrating the runtime input format. |
| `README.md` | Description of the sample input video and its intended use. |

## Important Notes

This repository does **not** include the full author-constructed UAV image dataset, trained model weights, TensorRT engine files, or full evaluation videos used for the quantitative results in the manuscript.

The following materials are not publicly distributed due to institutional and data-use restrictions:

- full UAV image dataset;
- trained PyTorch model weights, such as `best.pt`;
- TensorRT engine files, such as `best.engine`;
- full evaluation videos used for the quantitative experiments.

These materials are available from the corresponding authors upon reasonable request, subject to institutional and data-use restrictions.

The sample video included in `sample_data/` is a short representative clip provided only to illustrate the video input format of the runtime pipeline. It does **not** replace the full evaluation videos used for the quantitative results reported in the manuscript.

## Runtime Pipeline Overview

The scripts implement the following video-based UAV surveillance pipeline:

1. video frame acquisition;
2. YOLO-based UAV detection;
3. object tracking using tracking IDs and bounding-box smoothing;
4. anchor-point-based distance calculation;
5. approach-history-based threat assessment;
6. PIP magnified view and radar overlay visualization;
7. flashing alert display;
8. per-frame latency and FPS logging.

The logged latency components include:

- inference latency;
- processing latency;
- display/I/O latency;
- total latency;
- instantaneous FPS.

## Installation

Create a Python environment and install the required packages:

```bash
pip install -r requirements.txt
```

The scripts require a working installation of the Ultralytics YOLO package, OpenCV, NumPy, and a CUDA-capable environment when GPU inference is used.

## Expected Model and Video Inputs

The public scripts are configured to use environment variables so that private file paths do not need to be hard-coded.

### PyTorch model

```bash
export UAV_MODEL_PATH="models/best.pt"
```

### TensorRT engine

```bash
export UAV_ENGINE_PATH="models/best.engine"
```

### Input video

```bash
export UAV_VIDEO_PATH="sample_data/sample_input_video.mp4"
```

### Output log directory

```bash
export UAV_OUTPUT_DIR="logs"
```

If these variables are not set, the scripts use placeholder default paths. Users should replace them with their own model and video paths.

## Running the Host PC / SSH X11 Proxy Script

```bash
python detect_custom_radar.py
```

This script corresponds to the Host PC-based runtime condition used to analyze a network-coupled display/output path through an SSH X11 display-path proxy.

During execution, the user can select:

- display resolution: SD, HD, or FHD;
- model format: PyTorch `.pt` or TensorRT `.engine`;
- target anchor point using the GUI.

## Running the Jetson AGX Orin Script

```bash
python detect_custom_radar_Jetson.py
```

This script corresponds to the Jetson AGX Orin local edge-execution condition. It is intended for the local execution path where detection, tracking, threat assessment, visualization, and output are performed on the edge device.

## Sample Input Video

A short representative sample input video is provided at:

```text
sample_data/sample_input_video.mp4
```

This clip is included only for demonstrating the runtime input format of the video-based surveillance pipeline.

It is not the full evaluation video used for the quantitative runtime results reported in the manuscript. Therefore, the sample clip should be used only for code-execution demonstration and pipeline-format verification.

## Latency Log Output

Each script generates a CSV latency log with columns similar to:

```text
Frame, Inference(ms), Process(ms), Display(ms), Total(ms), FPS
```

The log file is saved under the configured output directory, for example:

```text
logs/latency_log_YYYYMMDD_HHMMSS.csv
```

These logs can be used to calculate mean latency, latency standard deviation, P95/P99 tail latency, and FPS statistics.

## Reproducibility Scope

This repository is intended to support reproducibility of the implementation structure and runtime measurement procedure. Exact reproduction of the quantitative results reported in the manuscript requires the original trained weights, TensorRT engine, evaluation videos, hardware configuration, and display environment.

The public repository supports:

- inspection of the runtime implementation logic;
- reproduction of the video-processing pipeline structure;
- verification of the latency-logging mechanism;
- demonstration using a short representative sample input video.

The public repository does not provide:

- the full training dataset;
- the full validation dataset;
- the trained detector weights;
- TensorRT engine binaries;
- full evaluation videos used for quantitative measurements.

## Citation

If this repository is used or referenced, please cite the associated manuscript:

```text
Park, Y.H.; Kang, J.; Lee, K.-B. Stochastic Latency Decomposition and Constrained Runtime Feasibility Analysis for Edge-Based UAV Surveillance under Network-Denied Environments. Mathematics, 2026.
```

## License and Use

This repository is provided for academic review and research transparency. Please contact the corresponding authors for questions regarding reuse, redistribution, or access to non-public experimental materials.
