"""Fingerprint the machine a result came from: GPU, power limits, CPU, RAM, WSL or vast."""

import os
import platform
import socket
import subprocess

NO_VALUE = {"", "N/A", "[N/A]", "[Not Supported]", "Not Supported"}
SMI_FIELDS = {
    "gpu_name": ("name", str),
    "driver": ("driver_version", str),
    "power_limit_w": ("power.limit", float),
    "power_default_w": ("power.default_limit", float),
    "power_max_w": ("power.max_limit", float),
    "sm_clock_max_mhz": ("clocks.max.sm", int),
    "pcie_gen_max": ("pcie.link.gen.max", int),
    "pcie_width_max": ("pcie.link.width.max", int),
}


def parse_smi(text: str) -> dict:
    """First CSV line of nvidia-smi output into SMI_FIELDS; anything unparsable is None."""
    parts = [p.strip() for p in (text.splitlines() or [""])[0].split(",")]
    out = {}
    for i, (key, (_, cast)) in enumerate(SMI_FIELDS.items()):
        try:
            out[key] = None if parts[i] in NO_VALUE else cast(parts[i])
        except (IndexError, ValueError):
            out[key] = None
    return out


def query_gpu() -> dict:
    query = ",".join(name for name, _ in SMI_FIELDS.values())
    try:
        done = subprocess.run(["nvidia-smi", f"--query-gpu={query}", "--format=csv,noheader,nounits"],
                              capture_output=True, text=True, timeout=20, check=True)
    except (OSError, subprocess.SubprocessError):
        return parse_smi("")
    return parse_smi(done.stdout)


def read(path: str) -> str:
    try:
        with open(path) as f:
            return f.read()
    except OSError:
        return ""


def cpu_model() -> str | None:
    for line in read("/proc/cpuinfo").splitlines():
        if line.startswith("model name"):
            return line.partition(":")[2].strip()
    return None


def ram_gb() -> int | None:
    for line in read("/proc/meminfo").splitlines():
        if line.startswith("MemTotal"):
            return round(int(line.split()[1]) / 1024 / 1024)
    return None


def collect() -> dict:
    return {
        "hostname": socket.gethostname(),
        **query_gpu(),
        "cpu_model": cpu_model(),
        "cpu_cores": os.cpu_count(),
        "ram_gb": ram_gb(),
        "kernel": platform.release(),
        "wsl": "microsoft" in read("/proc/version").lower(),
        "vast_instance": os.environ.get("CONTAINER_ID") or os.environ.get("VAST_CONTAINERLABEL"),
    }


def summary_line(d: dict) -> str:
    """One line for provenance; every field is optional."""
    parts = [(d.get("gpu_name") or "no GPU").replace("NVIDIA ", "").replace(" Workstation Edition", "")]
    watts = [f"{d[k]:.0f}" for k in ("power_limit_w", "power_max_w") if d.get(k) is not None]
    if watts:
        parts.append("/".join(watts) + " W")
    if d.get("driver"):
        parts.append(f"drv {d['driver']}")
    if d.get("pcie_gen_max") and d.get("pcie_width_max"):
        parts.append(f"PCIe {d['pcie_gen_max']}x{d['pcie_width_max']}")
    if d.get("cpu_model"):
        threads = f" ({d['cpu_cores']} thr)" if d.get("cpu_cores") else ""
        parts.append(d["cpu_model"] + threads)
    if d.get("ram_gb"):
        parts.append(f"{d['ram_gb']} GB")
    if d.get("wsl"):
        parts.append("WSL")
    if d.get("vast_instance"):
        parts.append(f"vast {d['vast_instance']}")
    return ", ".join(parts)


def summary() -> str:
    return summary_line(collect())
