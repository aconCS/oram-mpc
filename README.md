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

We use table full_table.csv with size of 2^24 of entries:

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
python plot.py results/results.csv                      # writes plots/*.png
python plot.py results/local.csv results/wan.csv --out plots    # compare up to 4 runs
```

It writes one PNG per metric (`time_ms.png`, `sent_kib.png`, `rounds.png`, `peak_kib.png`)
and `overview.png` with all of them. Colour and marker show the operation, line style shows
the run (the CSV file name), so name the files after what differs, e.g. the network setting.
The memory chart is skipped when the run used `--no-memory`.

## Network emulation

### First-time installation ()

**Windows:** Install Ubuntu WSL2 from an Administrator PowerShell session, if needed:

```powershell
wsl --install -d Ubuntu
```

Open Ubuntu and navigate to the repository (adjust the Windows username/path as necessary):

```bash
cd /mnt/c/Users/fthef/Documents/oram-mpc
sudo apt update
sudo apt install -y iproute2 python3 python3-venv
python3 -m venv .venv
.venv/bin/python -m pip install mpyc pandas openpyxl numpy gmpy2
```

Confirm dependencies:

```bash
.venv/bin/python -c "import mpyc, pandas; print('Dependencies OK')"
```

**Important:** `network/launcher.py` must invoke the project's virtual-environment interpreter (`os.path.abspath('.venv/bin/python')`), **not** `sys.executable`, because launching the network command with `sudo python3` otherwise selects system Python and may cause `ModuleNotFoundError`.


### run an experiment

 1. Create network
 ```
sudo .venv/bin/python -m network.cli setup
```

 2. Configure conditions (example: Party 1, 50ms latency)
 ```
sudo .venv/bin/python -m network.cli set --party 1 --latency 50
```

3. Check configuration
```
sudo .venv/bin/python -m network.cli status
```

 4. Run MPyC experiment
 ```
sudo .venv/bin/python -m network.launcher
```

 5. Reset network conditions (optional)
 ```
sudo .venv/bin/python -m network.cli reset
```

 6. Remove network when finished
 ```
sudo .venv/bin/python -m network.cli teardown
```

The network emulator creates three isolated network namespaces for the MPC
parties. Each party has its own virtual interface and IP address, and traffic
between them passes through a virtual bridge.

This makes it possible to test the MPC setup under network conditions such as
latency, jitter, packet loss and bandwidth limits.

### Network setup

| Party | Namespace | IP address |
|---|---|---|
| 0 | mpc0 | 10.10.0.10 |
| 1 | mpc1 | 10.10.0.11 |
| 2 | mpc2 | 10.10.0.12 |

The namespaces are connected through a Linux bridge. Traffic control (`tc`)
is used on each party's interface to apply network conditions.

### Commands

Network conditions can be set for an individual party:

```bash
sudo .venv/bin/python -m network.cli set --party 1 --latency 50
```

The current traffic control configuration can be checked with:

```bash
sudo .venv/bin/python -m network.cli status
```

## Testing

Connectivity was tested by pinging between parties:

```bash
sudo ip netns exec mpc0 ping -c 5 10.10.0.11
sudo ip netns exec mpc1 ping -c 5 10.10.0.10
```

Latency was tested by adding a 50 ms delay to Party 1. The round trip time
between Party 0 and Party 1 increased to roughly 50 ms in both directions.

When a 50 ms delay was applied to both Party 0 and Party 1, the round trip
time increased to roughly 100 ms. This confirmed that delays from both
parties are added together across the round trip.

Jitter, packet loss and bandwidth limits were also tested. The 10 Mbps
bandwidth limit was verified using `iperf3`, with one party acting as the
server and another as the client.

Combined conditions were tested by applying latency, jitter, packet loss and
bandwidth limits at the same time. Invalid values were also tested and were
rejected by the CLI.

## Reset and teardown

Traffic shaping can be removed with:

```bash
sudo .venv/bin/python -m network.cli reset
```

After resetting, all parties showed `noqueue`, confirming the traffic shaping
rules had been removed.

The network can be removed with:

```bash
sudo .venv/bin/python -m network.cli teardown
```

After teardown, no `mpc*` namespaces or interfaces remained.

