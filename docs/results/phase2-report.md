| entry | Index | ECE | coverage | median ms | p95 ms | run layout / orders | run calibration | shipped now | latency run |
|---|---|---|---|---|---|---|---|---|---|
| **qwen3.6-27b** † | 51.61 | 0.022 | 1.000 | 126.7 | 657.4 | decider_chat / identity | T=1.943 | header / identity / v6 | 2026-10-02T194323Z-latency ‡ |
| Decider chat · Qwen3.6-27B | 51.35 | 0.021 | board | 83.6 | n/a | | | | |
| **gemma-4-31b** † | 56.31 | 0.235 | 1.000 | 88.5 | 614.0 | decider_chat / identity | T=1 (none) | decider_chat / identity / v3 | 2026-10-02T035957Z-latency |
| Decider chat · Gemma-4-31B | 57.33 | 0.047 | board | 108.5 | n/a | | | | |
| **qwen3.8-27b** † | 51.44 | 0.061 | 1.000 | 90.2 | 623.9 | decider_chat / identity | T=1 (none) | decider_chat / identity / v3 | 2026-10-02T141446Z-latency |
| simple-jev · Qwen3.8-27B | 55.70 | 0.113 | board | 373.0 | n/a | | | | |
| reflex 27B | 52.20 | 0.024 | board | 108.0 | n/a | | | | |
| Jevfire (Qwen3.8-27B-FP8) | 49.40 | 0.052 | board | 89.6 | n/a | | | | |

- Calibration T is listed as choice/score/noul; b is the noul yes-offset.
- † the run's layout, orders or calibration differ from what ships now (or the calibration file is newer).
- ‡ the latency run's layout, orders or calibration differ from the Index run's.
