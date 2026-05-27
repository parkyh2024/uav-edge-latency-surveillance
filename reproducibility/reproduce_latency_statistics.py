from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parent
WARMUP_FRAMES = 60

def summarize_csv(csv_path: Path):
    df = pd.read_csv(csv_path)
    df = df[df["Frame"] >= WARMUP_FRAMES].copy()

    cols = ["Inference(ms)", "Process(ms)", "Display(ms)", "Total(ms)", "FPS"]

    print(f"\n[{csv_path.name}]")
    for col in cols:
        mean = df[col].mean()
        std = df[col].std()
        print(f"{col}: {mean:.2f} ± {std:.2f}")

    total_p95 = df["Total(ms)"].quantile(0.95)
    total_p99 = df["Total(ms)"].quantile(0.99)
    display_p95 = df["Display(ms)"].quantile(0.95)
    display_p99 = df["Display(ms)"].quantile(0.99)

    print(f"Total P95: {total_p95:.2f}")
    print(f"Total P99: {total_p99:.2f}")
    print(f"Display P95: {display_p95:.2f}")
    print(f"Display P99: {display_p99:.2f}")

def main():
    csv_files = sorted(ROOT.rglob("*.csv"))
    if not csv_files:
        raise FileNotFoundError("No CSV files found.")

    for csv_path in csv_files:
        summarize_csv(csv_path)

if __name__ == "__main__":
    main()
