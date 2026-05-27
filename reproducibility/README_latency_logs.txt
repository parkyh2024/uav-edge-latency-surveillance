This archive contains anonymized per-frame latency logs used for the runtime latency analysis reported in Tables 9–11 and Figures 4–5.

The folder table9_10_component_latency_logs contains the per-frame logs used to compute the component-wise mean and standard deviation values reported in Tables 9 and 10.

The folder table11_tail_latency_logs contains the retained per-frame logs used to compute the P95 and P99 tail-latency statistics reported in Table 11.

Each CSV file contains:
- Frame: frame index
- Inference(ms): detector inference latency
- Process(ms): processing latency including tracking, threat assessment, overlay generation, and synchronization
- Display(ms): display and I/O latency
- Total(ms): total per-frame latency
- FPS: per-frame throughput

The initial 60 frames were excluded when calculating the reported summary statistics and tail-latency statistics.