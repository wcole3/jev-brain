from scripts import gpu_telemetry

CSV = """utc,util,sm_clock,mem_clock,power_draw,power_limit,temp,throttle
2026-10-02T10:00:00,90,2500,405,500.0,600,60,0x0000000000000000
2026-10-02T10:00:05,95,2400,405,590.0,600,62,0x0000000000000004
2026-10-02T10:00:10,99,2300,405,600.0,600,64,0x0000000000000024
2026-10-02T10:00:15,10,1000,405,100.0,600,40,0x0000000000000001
"""


def test_summarize_medians_and_throttle_share(tmp_path):
    f = tmp_path / "t.csv"
    f.write_text(CSV)
    s = gpu_telemetry.summarize(f)
    assert s["samples"] == 4 and s["median_sm_clock"] == 2350 and s["median_util"] == 92.5
    assert s["median_power"] == 545.0 and s["median_temp"] == 61
    assert s["throttled_share"] == 0.5  # 0x4 and 0x24 count; 0x1 (idle) does not


def test_summarize_window(tmp_path):
    f = tmp_path / "t.csv"
    f.write_text(CSV)
    s = gpu_telemetry.summarize(f, since="2026-10-02T10:00:05", until="2026-10-02T10:00:10")
    assert s["samples"] == 2 and s["throttled_share"] == 1.0


def test_parse_row_from_smi_text():
    row = gpu_telemetry.parse_sample("2, 480, 405, 33.86, 540.00, 36, 0x0000000000000000\n")
    assert row == ["2", "480", "405", "33.86", "540.00", "36", "0x0000000000000000"]


def test_summarize_empty(tmp_path):
    f = tmp_path / "t.csv"
    f.write_text("utc,util,sm_clock,mem_clock,power_draw,power_limit,temp,throttle\n")
    assert gpu_telemetry.summarize(f)["samples"] == 0
