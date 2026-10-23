# Linear ORAM basic implementation

Just as in project description: "The trivial ORAM construction is “Linear ORAM”: To read position ‘i‘, you
construct a secret unit vector with a one at position ‘i’ and take the inner
product with the array A. To write value ‘v‘, add ‘(v - A[i])’ times that unit
vector. It needs no client state, but every access costs O(n) work, so it only
makes sense for small arrays."

## Installating the libraries

Those unit vectors as well as secure data typec come from mpyc. To install:
```bash
pip install mpyc
```

and to run evetyrhing I would recommend
```bash
pip install -r requirements.txt
```

The initial table consists only of 100 entries of

- BSN: 9 digit Dutch citizen service number 
- blood_type:  as one of 8 types
- blood_code: integer encoding the blood type (secint can't hold strings)

## Running the simulation
To run linear.py, open three separate terminals from the project root & paste these three separate commands:

Terminal 1
```bash
python linear.py -M3 -I0
```

Terminal 2
```bash
python linear.py -M3 -I1
```

Terminal 3
``` bash
python linear.py -M3 -I2
```

## Benchmarking

`benchmark.py` measures every operation (setup, lookup/write by index, lookup/write by key)
on tables of growing size. Each table is the first n rows of `full_table.csv`, with
n = 1, 10, 100, ..., 10^max-exp.

Make sure the real CSV is there (it is stored with Git LFS):
```bash
git lfs pull
```

Run all three parties in one terminal (parties 1 and 2 are spawned automatically):
```bash
python benchmark.py -M3 --max-exp 3
```

Useful options:

| option | meaning | default |
|---|---|---|
| `--max-exp k` | sizes 10^0 .. 10^k | 3 |
| `--sizes 16 32 64` | explicit sizes, overrides `--max-exp` | |
| `--ops lookup_by_key ...` | only run these operations | all four |
| `--repeat r` | runs per operation, median time is reported | 3 |
| `--seed s` | seed for which rows are queried and what is written | 1 |
| `--no-memory` | skip memory tracking (it slows Python down, so times are more accurate) | |
| `--csv results.csv` | save the results as CSV, for scripts and `plot.py` | |
| `--md results.md` | save a readable Markdown report | |
| `--table file.csv` | another table with `bsn` and `blood_code` columns | `full_table.csv` |

Example, saving results for sizes up to 10 000:
```bash
python benchmark.py -M3 --max-exp 4 --no-memory --csv results.csv --md results.md
```

### Output

The terminal, the CSV and the Markdown report use the same columns and units:

| column (CSV name) | meaning |
|---|---|
| `n` | table size in rows |
| `op` | `setup` (secret-sharing the table) or one of the four ORAM operations |
| `time_ms` | wall-clock time of the slowest party, median over `--repeat` runs, in ms |
| `sent_kib` | data sent, summed over all parties, in KiB |
| `messages` | messages sent, summed over all parties |
| `rounds` | sequential communication rounds (each costs one network round-trip) |
| `peak_kib` | largest Python memory growth of any party, in KiB (0 with `--no-memory`) |

The Markdown report starts with the run settings (date, parties, sizes, repeat, seed),
then has the full table and a smaller "time per size" table with one column per operation.

Key operations do n secure comparisons, so they get slow fast: about 1 s at n = 1000 on one
machine (more with memory tracking on), roughly 10x more per step. Start small and raise
`--max-exp` step by step.

### Plots

`plot.py` turns one or more result CSVs into charts (log-log, cost against n):
```bash
python plot.py results.csv                      # writes plots/*.png
python plot.py local.csv wan.csv --out plots    # compare up to 4 runs
```

It writes one PNG per metric (`time_ms.png`, `sent_kib.png`, `rounds.png`, `peak_kib.png`)
and `overview.png` with all of them. Colour and marker show the operation, line style shows
the run (the CSV file name), so name the files after what differs, e.g. the network setting.
The memory chart is skipped when the run used `--no-memory`.

## TODOs 
- check bigger datasets (and write down size + time), 
- unit tests ?, 
- simulation of real network (termianls with different-I ids) check here [https://mpyc.readthedocs.io/en/latest/cli.html]