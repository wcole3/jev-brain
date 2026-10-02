from scripts import host_info

SMI = "NVIDIA RTX PRO 6000 Blackwell Workstation Edition, 610.62, 540.00, 600.00, 600.00, 3090, 4, 16"


def test_parse_smi_reads_one_gpu_line():
    got = host_info.parse_smi(SMI + "\n")
    assert got["gpu_name"].startswith("NVIDIA RTX PRO 6000")
    assert got["driver"] == "610.62" and got["power_limit_w"] == 540.0 and got["power_max_w"] == 600.0
    assert got["sm_clock_max_mhz"] == 3090 and got["pcie_gen_max"] == 4 and got["pcie_width_max"] == 16


def test_parse_smi_handles_missing_output():
    assert set(host_info.parse_smi("").values()) == {None}


def test_collect_without_nvidia_smi(monkeypatch):
    def boom(*a, **k):
        raise FileNotFoundError

    monkeypatch.setattr(host_info.subprocess, "run", boom)
    monkeypatch.setenv("VAST_CONTAINERLABEL", "C.123")
    d = host_info.collect()
    assert d["gpu_name"] is None and d["vast_instance"] == "C.123" and d["hostname"]


def test_summary_line_is_short_and_tolerates_none():
    d = {**host_info.parse_smi(SMI), "cpu_model": "AMD Ryzen 7 3800X 8-Core Processor", "cpu_cores": 16,
         "ram_gb": 94, "wsl": True}
    line = host_info.summary_line(d)
    assert "RTX PRO 6000" in line and "540/600 W" in line and "drv 610.62" in line
    assert "PCIe 4x16" in line and "16 thr" in line and "94 GB" in line and line.endswith("WSL")
    assert host_info.summary_line(host_info.parse_smi(""))
