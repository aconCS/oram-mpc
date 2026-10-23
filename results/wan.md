# Linear ORAM benchmark

- date: 2026-10-23 20:59
- parties: 3
- table: `full_table.csv`, sizes: 10, 100, 1000, 10000
- repeat: 3 (time is the median), seed: 1
- memory tracking: on
- time and peak memory: slowest party; sent and messages: sum over all parties

## All results

| n | op | time (ms) | sent (KiB) | messages | rounds | peak (KiB) |
| ---: | --- | ---: | ---: | ---: | ---: | ---: |
| 10 | setup | 62.5 | 0.39 | 6 | 1 | 274.0 |
| 10 | lookup_by_index | 406.5 | 1.53 | 59 | 8 | 367.1 |
| 10 | write_by_index | 459.8 | 2.74 | 121 | 9 | 385.7 |
| 10 | lookup_by_key | 420.4 | 34.49 | 398 | 8 | 461.6 |
| 10 | write_by_key | 474.3 | 35.70 | 460 | 9 | 492.6 |
| 100 | setup | 53.3 | 3.21 | 6 | 1 | 335.4 |
| 100 | lookup_by_index | 617.2 | 6.94 | 113 | 12 | 566.2 |
| 100 | write_by_index | 721.4 | 18.70 | 715 | 13 | 1005.2 |
| 100 | lookup_by_key | 622.0 | 343.52 | 3908 | 9 | 2287.1 |
| 100 | write_by_key | 685.0 | 355.27 | 4510 | 10 | 2696.1 |
| 1000 | setup | 78.6 | 31.35 | 6 | 1 | 1219.8 |
| 1000 | lookup_by_index | 865.9 | 50.25 | 161 | 16 | 2095.0 |
| 1000 | write_by_index | 1188.6 | 167.48 | 6163 | 17 | 7622.1 |
| 1000 | lookup_by_key | 3773.3 | 3433.75 | 39008 | 21 | 21390.3 |
| 1000 | write_by_key | 4278.3 | 3550.98 | 45010 | 22 | 25686.0 |
| 10000 | setup | 382.7 | 312.60 | 6 | 1 | 12393.0 |
| 10000 | lookup_by_index | 1658.7 | 473.91 | 233 | 20 | 17208.1 |
| 10000 | write_by_index | 4846.9 | 1645.82 | 60235 | 21 | 76684.8 |
| 10000 | lookup_by_key | 38683.4 | 34336.09 | 390008 | 35 | 212037.9 |
| 10000 | write_by_key | 40901.4 | 35508.01 | 450010 | 35 | 256163.6 |

## Time (ms) per size

| n | setup | lookup_by_index | write_by_index | lookup_by_key | write_by_key |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 10 | 62.5 | 406.5 | 459.8 | 420.4 | 474.3 |
| 100 | 53.3 | 617.2 | 721.4 | 622.0 | 685.0 |
| 1000 | 78.6 | 865.9 | 1188.6 | 3773.3 | 4278.3 |
| 10000 | 382.7 | 1658.7 | 4846.9 | 38683.4 | 40901.4 |
