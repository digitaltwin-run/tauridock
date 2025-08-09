# benchmarks/benchmark_builds.py
import time
import subprocess
from statistics import mean, stdev


def benchmark_build(platform, runs=5):
    times = []
    for i in range(runs):
        start = time.time()
        subprocess.run([
            "python", "tauridock.py",
            "--mode", "build",
            "--platforms", platform
        ])
        times.append(time.time() - start)

    print(f"{platform}: {mean(times):.2f}s ± {stdev(times):.2f}s")


if __name__ == "__main__":
    for platform in ["windows", "linux", "macos"]:
        benchmark_build(platform)