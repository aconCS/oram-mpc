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
| `--no-memory` | skip memory tracking (more accurate times) | |
| `--csv results.csv` | save the results (written by party 0) | |
| `--table file.csv` | another table with `bsn` and `blood_code` columns | `full_table.csv` |

Example, saving results for sizes up to 10 000:
```bash
python benchmark.py -M3 --max-exp 4 --no-memory --csv results.csv
```

Output columns: `time` (slowest party, ms), `bytes` and `messages` (sum over all parties),
`rounds` (sequential communication rounds), `peak` (largest Python heap growth of any party).

Key operations do n secure comparisons, so they get slow fast: about 1 s at n = 1000 on one
machine, roughly 10x more per step. Start small and raise `--max-exp` step by step.

## TODOs 
- check bigger datasets (and write down size + time), 
- unit tests ?, 
- simulation of real network (termianls with different-I ids) check here [https://mpyc.readthedocs.io/en/latest/cli.html]