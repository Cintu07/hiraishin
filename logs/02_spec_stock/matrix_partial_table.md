## per run

| run | tok/s | n | accept % | cycles | acc/cycle | tok/pass | matches plain | first diff byte / plain len |
|---|---:|---:|---:|---:|---:|---:|---|---|
| plain_code_r1 | 39.59 | 255 | nan | - | nan | nan | yes | - |
| plain_code_r2 | 41.01 | 255 | nan | - | nan | nan | yes | - |
| plain_explain_r1 | 23.87 | 255 | nan | - | nan | nan | yes | - |
| plain_explain_r2 | 41.31 | 255 | nan | - | nan | nan | yes | - |
| plain_math_r1 | 19.33 | 255 | nan | - | nan | nan | yes | - |
| plain_rewrite_r1 | 41.14 | 209 | nan | - | nan | nan | yes | - |
| plain_rewrite_r2 | 40.47 | 209 | nan | - | nan | nan | yes | - |
| spec_k2_code_r1 | 53.83 | 258 | 72.4 | 106 | 1.43 | 2.43 | NO | 365 / 1072 |
| spec_k2_code_r2 | 65.05 | 258 | 72.4 | 106 | 1.43 | 2.43 | NO | 365 / 1072 |
| spec_k2_explain_r1 | 42.38 | 258 | 48.8 | 131 | 0.97 | 1.97 | NO | 656 / 997 |
| spec_k2_explain_r2 | 52.85 | 258 | 48.8 | 131 | 0.97 | 1.97 | NO | 656 / 997 |
| spec_k2_math_r1 | 67.94 | 257 | 78.0 | 101 | 1.54 | 2.54 | yes | - |
| spec_k2_rewrite_r1 | 76.80 | 210 | 97.2 | 72 | 1.92 | 2.92 | yes | - |
| spec_k2_rewrite_r2 | 75.95 | 210 | 97.2 | 72 | 1.92 | 2.92 | yes | - |
| spec_k4_code_r1 | 67.05 | 257 | 57.1 | 79 | 2.25 | 3.25 | NO | 169 / 1072 |
| spec_k4_code_r2 | 64.29 | 257 | 57.1 | 79 | 2.25 | 3.25 | NO | 169 / 1072 |
| spec_k4_explain_r1 | 51.16 | 261 | 44.1 | 95 | 1.75 | 2.75 | NO | 478 / 997 |
| spec_k4_explain_r2 | 56.41 | 261 | 44.1 | 95 | 1.75 | 2.75 | NO | 478 / 997 |
| spec_k4_rewrite_r1 | 94.17 | 211 | 94.3 | 45 | 3.69 | 4.69 | yes | - |
| spec_k4_rewrite_r2 | 83.31 | 211 | 94.3 | 45 | 3.69 | 4.69 | yes | - |
| spec_k8_code_r1 | 66.84 | 258 | 40.2 | 62 | 3.16 | 4.16 | yes | - |
| spec_k8_code_r2 | 63.75 | 258 | 40.2 | 62 | 3.16 | 4.16 | yes | - |
| spec_k8_explain_r1 | 49.54 | 260 | 27.0 | 83 | 2.13 | 3.13 | NO | 478 / 997 |
| spec_k8_explain_r2 | 50.19 | 260 | 27.0 | 83 | 2.13 | 3.13 | NO | 478 / 997 |
| spec_k8_rewrite_r1 | 122.57 | 210 | 92.0 | 26 | 7.08 | 8.08 | yes | - |
| spec_k8_rewrite_r2 | 90.45 | 210 | 92.0 | 26 | 7.08 | 8.08 | yes | - |

## per config (mean over prompts and reps; acceptance stats are deterministic per prompt)

| config | tok/s mean | tok/s min-max | accept % | acc/cycle | tok/pass | runs matching plain |
|---|---:|---:|---:|---:|---:|---|
| plain | 35.25 | 19.33-41.31 | - | - | 1.00 | 7/7 |
| spec k=2 | 62.12 | 42.38-76.80 | 69.5 | 1.38 | 2.38 | 3/7 |
| spec k=4 | 69.40 | 51.16-94.17 | 59.0 | 2.33 | 3.33 | 2/6 |
| spec k=8 | 73.89 | 49.54-122.57 | 41.4 | 3.26 | 4.26 | 4/6 |

## divergences (plain vs spec, 70 bytes around first difference)

- spec_k2_code_r1 @ byte 365
  - plain: b'che\n\n```python\nfrom typing import Dict, Optional, Any\nimport time\n\ncla'
  - spec : b'che\n\n```python\nfrom typing import Dict, Any, Optional\nimport time\n\ncla'
- spec_k2_code_r2 @ byte 365
  - plain: b'che\n\n```python\nfrom typing import Dict, Optional, Any\nimport time\n\ncla'
  - spec : b'che\n\n```python\nfrom typing import Dict, Any, Optional\nimport time\n\ncla'
- spec_k2_explain_r1 @ byte 656
  - plain: b'sed.\n\n### \xf0\x9f\x93\xa6 **Cache Levels and Latency**\n\nHere are typical **latenc'
  - spec : b'sed.\n\n### \xf0\x9f\x93\xa6 **Cache Levels and Latencies (in nanoseconds)**\n\n| Leve'
- spec_k2_explain_r2 @ byte 656
  - plain: b'sed.\n\n### \xf0\x9f\x93\xa6 **Cache Levels and Latency**\n\nHere are typical **latenc'
  - spec : b'sed.\n\n### \xf0\x9f\x93\xa6 **Cache Levels and Latencies (in nanoseconds)**\n\n| Leve'
- spec_k4_code_r1 @ byte 169
  - plain: b'ludes:\n\n- `get(key)` to retrieve a value by key.\n- `put(key, value)` t'
  - spec : b'ludes:\n\n- `get(key)` to retrieve a value\n- `put(key, value)` to insert'
- spec_k4_code_r2 @ byte 169
  - plain: b'ludes:\n\n- `get(key)` to retrieve a value by key.\n- `put(key, value)` t'
  - spec : b'ludes:\n\n- `get(key)` to retrieve a value\n- `put(key, value)` to insert'
- spec_k4_explain_r1 @ byte 478
  - plain: b'd **L3 being the slowest and largest**. Each level serves as a buffer '
  - spec : b"d **L3 being the slowest and largest**. Here's a breakdown:\n\n| Level |"
- spec_k4_explain_r2 @ byte 478
  - plain: b'd **L3 being the slowest and largest**. Each level serves as a buffer '
  - spec : b"d **L3 being the slowest and largest**. Here's a breakdown:\n\n| Level |"
- spec_k8_explain_r1 @ byte 478
  - plain: b'd **L3 being the slowest and largest**. Each level serves as a buffer '
  - spec : b"d **L3 being the slowest and largest**. Here's a breakdown:\n\n| Level |"
- spec_k8_explain_r2 @ byte 478
  - plain: b'd **L3 being the slowest and largest**. Each level serves as a buffer '
  - spec : b"d **L3 being the slowest and largest**. Here's a breakdown:\n\n| Level |"
