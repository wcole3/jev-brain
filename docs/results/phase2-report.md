| entry | Index | Full | ECE | coverage | median ms | p95 ms | run layout / orders | run calibration | shipped now | latency run |
|---|---|---|---|---|---|---|---|---|---|---|
| **qwen3.6-27b** | 56.82 | — | 0.048 | 1.000 | 131.5 | 976.8 | blurb_header / identity | T=1.63/2.06/1.26 | blurb_header / identity / v1 | 2026-10-20T201005Z-latency |
| Decider chat · Qwen3.6-27B | 51.57 | 51.25 | 0.021 | board | 83.6 | n/a | | | | |
| **gemma-4-31b** | 62.98 | — | 0.119 | 1.000 | 124.8 | 954.5 | blurb_header / top_p:0.9+reversed | T=3.98/5.21/6.74 | blurb_header / top_p:0.9+reversed / v1 | 2026-10-20T174655Z-latency |
| Decider chat · Gemma-4-31B | 57.79 | 57.62 | 0.047 | board | 108.5 | n/a | | | | |
| **qwen3.8-27b** | 57.64 | — | 0.024 | 1.000 | 155.8 | 814.9 | blurb_header / min_n:4+reversed | T=1.64/1/1.21 | blurb_header / min_n:4+reversed / v1 | 2026-10-20T165511Z-latency |
| simple-jev · Qwen3.8-27B | 56.05 | 51.79 | 0.113 | board | 373.0 | n/a | | | | |
| reflex Qwen3.8-27B-FP8 (wide choice) | 52.27 | 51.40 | 0.024 | board | 108.3 | n/a | | | | |
| Jevfire Qwen3.8-27B | 49.80 | 45.55 | 0.052 | board | 89.6 | n/a | | | | |
| **gemma-4-12b** | 53.58 | — | 0.060 | 1.000 | 83.1 | 465.6 | blurb_header / identity | T=4.035 | blurb_header / identity / v2 | 2026-10-21T115907Z-latency ‡ |
| AJev lora7 (Gemma 4 12B) | 55.17 | 49.11 | 0.082 | board | 69.1 | n/a | | | | |
| decisio 0.4.0 (Gemma 4 12B) | 49.72 | 47.93 | 0.103 | board | 37.8 | n/a | | | | |
| Winnow-12B | 50.66 | 47.07 | 0.168 | board | 72.5 | n/a | | | | |
| **qwen3.6-27b-fp8** | 56.78 | — | 0.049 | 1.000 | 67.8 | 485.6 | blurb_header / identity | T=1.61/2.04/1.26 | blurb_header / identity / v1 | 2026-10-20T200156Z-latency |
| Decider chat · Qwen3.6-27B | 51.57 | 51.25 | 0.021 | board | 83.6 | n/a | | | | |
| **qwen3.8-27b-fp8** | 57.58 | — | 0.024 | 1.000 | 114.5 | 601.3 | blurb_header / min_n:4+reversed | T=1.59/1/1.11, b=0.14 | blurb_header / min_n:4+reversed / v1 | 2026-10-20T165750Z-latency |
| simple-jev · Qwen3.8-27B | 56.05 | 51.79 | 0.113 | board | 373.0 | n/a | | | | |
| reflex Qwen3.8-27B-FP8 (wide choice) | 52.27 | 51.40 | 0.024 | board | 108.3 | n/a | | | | |
| Jevfire Qwen3.8-27B | 49.80 | 45.55 | 0.052 | board | 89.6 | n/a | | | | |
| **qwen3.8-27b-nvfp4** | 56.63 | — | 0.025 | 1.000 | 88.3 | 450.9 | blurb_header / min_n:4+reversed | T=1.68/1.97/1.14 | blurb_header / min_n:4+reversed / v1 | 2026-10-20T165445Z-latency |
| simple-jev · Qwen3.8-27B | 56.05 | 51.79 | 0.113 | board | 373.0 | n/a | | | | |
| reflex Qwen3.8-27B-FP8 (wide choice) | 52.27 | 51.40 | 0.024 | board | 108.3 | n/a | | | | |
| Jevfire Qwen3.8-27B | 49.80 | 45.55 | 0.052 | board | 89.6 | n/a | | | | |
| **gemma-4-31b-fp8** | 62.82 | — | 0.116 | 1.000 | 100.9 | 696.4 | blurb_header / top_p:0.9+reversed | T=4.06/5.31/6.66 | blurb_header / top_p:0.9+reversed / v1 | 2026-10-20T165623Z-latency |
| Decider chat · Gemma-4-31B | 57.79 | 57.62 | 0.047 | board | 108.5 | n/a | | | | |
| **gemma-4-12b-qat** | 51.26 | — | 0.047 | 1.000 | 82.2 | 450.3 | blurb_header / identity | T=3.01/12.9/2.24 | blurb_header / identity / v2 | 2026-10-21T115055Z-latency ‡ |
| AJev lora7 (Gemma 4 12B) | 55.17 | 49.11 | 0.082 | board | 69.1 | n/a | | | | |
| decisio 0.4.0 (Gemma 4 12B) | 49.72 | 47.93 | 0.103 | board | 37.8 | n/a | | | | |
| Winnow-12B | 50.66 | 47.07 | 0.168 | board | 72.5 | n/a | | | | |

- Calibration T is listed as choice/score/noul; b is the noul yes-offset.
- ‡ the latency run's layout, orders or calibration differ from the Index run's.
