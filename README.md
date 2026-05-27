# UAV Edge Latency Surveillance

This repository provides the public implementation scripts and reproducibility materials used for the runtime-feasibility experiments reported in the manuscript:

**Stochastic Latency Decomposition and Constrained Runtime Feasibility Analysis for Edge-Based UAV Surveillance under Network-Denied Environments**

The repository is provided to improve implementation transparency and reproducibility for the video-based UAV surveillance pipeline. The implementation includes object detection, object tracking, threat assessment, visualization, and per-frame latency logging.

In addition to the runtime scripts and a representative sample input video, this repository provides anonymized per-frame latency logs and a reproduction script for verifying the latency statistics reported in Tables 9–11 and Figures 4–5 of the manuscript.

## Repository Structure

```text
uav-edge-latency-surveillance/
├── detect_custom_radar.py
├── detect_custom_radar_Jetson.py
├── requirements.txt
├── example_config.md
├── README.md
├── .gitignore
├── sample_data/
│   ├── README.md
│   └── sample_input_video.mp4
└── defense_round2/
    ├── README_latency_logs.txt
    ├── reproduce_latency_statistics.py
    ├── table9_10_component_latency_logs/
    │   ├── best_pt_ssh_x11_sd.csv
    │   ├── best_pt_ssh_x11_hd.csv
    │   ├── best_pt_ssh_x11_fhd.csv
    │   ├── best_pt_jetson_sd.csv
    │   ├── best_pt_jetson_hd.csv
    │   ├── best_pt_jetson_fhd.csv
    │   ├── best_engine_ssh_x11_sd.csv
    │   ├── best_engine_ssh_x11_hd.csv
    │   ├── best_engine_ssh_x11_fhd.csv
    │   ├── best_engine_jetson_sd.csv
    │   ├── best_engine_jetson_hd.csv
    │   └── best_engine_jetson_fhd.csv
    └── table11_tail_latency_logs/
        ├── best_pt_ssh_x11_sd.csv
        ├── best_pt_ssh_x11_hd.csv
        ├── best_pt_ssh_x11_fhd.csv
        ├── best_pt_jetson_sd.csv
        ├── best_pt_jetson_hd.csv
        ├── best_pt_jetson_fhd.csv
        ├── best_engine_ssh_x11_sd.csv
        ├── best_engine_ssh_x11_hd.csv
        ├── best_engine_ssh_x11_fhd.csv
        ├── best_engine_jetson_sd.csv
        ├── best_engine_jetson_hd.csv
        └── best_engine_jetson_fhd.csv
```

## Files

| File | Description |
|---|---|
| `detect_custom_radar.py` | Runtime script used for the Host PC / SSH X11 display-path proxy condition. |
| `detect_custom_radar_Jetson.py` | Runtime script used for the Jetson AGX Orin local edge-execution condition. |
| `requirements.txt` | Minimal Python package requirements. |
| `example_config.md` | Example runtime configuration and environment-variable usage. |
| `sample_data/sample_input_video.mp4` | Short representative sample input video clip for demonstrating the runtime input format. |
| `sample_data/README.md` | Description of the sample input video and its intended use. |
| `defense_round2/README_latency_logs.txt` | Description of the anonymized per-frame latency logs released for reproducibility. |
| `defense_round2/reproduce_latency_statistics.py` | Reproduction script for computing the mean, standard deviation, and P95/P99 latency statistics reported in Tables 9–11. |
| `defense_round2/table9_10_component_latency_logs/` | Anonymized per-frame latency logs used to compute the component-wise mean and standard deviation values reported in Tables 9 and 10 and visualized in Figures 4 and 5. |
| `defense_round2/table11_tail_latency_logs/` | Retained anonymized per-frame latency logs used to compute the P95/P99 tail-latency statistics reported in Table 11. |

## Important Notes

This repository does **not** include the full author-constructed UAV image dataset, trained model weights, TensorRT engine files, or full evaluation videos used for the quantitative results in the manuscript. However, it does include anonymized per-frame latency logs used to verify the latency summary statistics reported in Tables 9–11 and Figures 4–5.

The following materials are not publicly distributed due to institutional and data-use restrictions:

- full UAV image dataset;
- trained PyTorch model weights, such as `best.pt`;
- TensorRT engine files, such as `best.engine`;
- full evaluation videos used for the quantitative experiments.

These materials are available from the corresponding authors upon reasonable request, subject to institutional and data-use restrictions.

The anonymized per-frame latency logs in `defense_round2/` do **not** contain image data, model weights, TensorRT binaries, or full evaluation videos. They contain only frame-level latency measurements and FPS values required to verify the reported runtime statistics.

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

## Released Per-Frame Latency Logs

Anonymized per-frame latency logs used for the manuscript's runtime analysis are provided in:

```text
defense_round2/
```

The folder `table9_10_component_latency_logs/` contains the per-frame logs used to compute the component-wise mean and standard deviation values reported in Tables 9 and 10 and visualized in Figures 4 and 5.

The folder `table11_tail_latency_logs/` contains the retained per-frame logs used to compute the P95/P99 tail-latency statistics reported in Table 11.

Each CSV file includes the following columns:

```text
Frame, Inference(ms), Process(ms), Display(ms), Total(ms), FPS
```

The initial 60 frames are excluded when computing the reported summary statistics and tail-latency statistics.

To reproduce the reported latency statistics, run:

```bash
cd defense_round2
python reproduce_latency_statistics.py
```

The script reads the released CSV files and reports:

- mean and standard deviation of inference latency;
- mean and standard deviation of processing latency;
- mean and standard deviation of display/I/O latency;
- mean and standard deviation of total latency;
- mean and standard deviation of FPS;
- P95 and P99 total-latency statistics;
- P95 and P99 display-latency statistics.

## Reproducibility Scope

This repository is intended to support reproducibility of the implementation structure, runtime measurement procedure, and reported latency statistics.

The public repository supports:

- inspection of the runtime implementation logic;
- reproduction of the video-processing pipeline structure;
- verification of the latency-logging mechanism;
- demonstration using a short representative sample input video;
- independent verification of the component-wise latency statistics reported in Tables 9 and 10 using anonymized per-frame logs;
- independent verification of the P95/P99 tail-latency statistics reported in Table 11 using retained anonymized per-frame logs;
- verification of the latency data underlying Figures 4 and 5.

The public repository does not provide:

- the full training dataset;
- the full validation dataset;
- the trained detector weights;
- TensorRT engine binaries;
- full evaluation videos used for quantitative measurements.

Because the full evaluation videos, trained weights, and TensorRT engine binaries are not publicly distributed, the released latency logs are intended to support independent verification of the reported latency statistics rather than full re-execution of the complete quantitative experiments.

## Reproducibility Data

The anonymized per-frame latency logs and reproduction script are provided for review and reproducibility of the manuscript's latency-decomposition results. These files correspond to the runtime conditions reported in Tables 9–11 and Figures 4–5.

The logs were anonymized to remove private file paths and environment-specific identifiers. They retain the frame index and measured latency components required to reproduce the reported summary statistics.

## Citation

If this repository is used or referenced, please cite the associated manuscript:

```text
Park, Y.H.; Kang, J.; Lee, K.-B. Stochastic Latency Decomposition and Constrained Runtime Feasibility Analysis for Edge-Based UAV Surveillance under Network-Denied Environments. Mathematics, 2026.
```

## License and Use

This repository is provided for academic review and research transparency. Please contact the corresponding authors for questions regarding reuse, redistribution, or access to non-public experimental materials.
