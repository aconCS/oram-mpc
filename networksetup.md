## First-time installation ()

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


## run an experiment

1. create the network
2. configure conditions
3. Inspect current settings
4. launch the existing MpYC program: The launcher starts three instances of `linear.py` in `mpc0`, `mpc1`, and `mpc2`, using `.venv/bin/python`. The script and `table.xlsx` must be available relative to the repository working directory.
5. Reset traffic shaping
6. Remove all virtual networking



## Tests that aren't covered 

- [ ] **Bandwidth:** Measure actual throughput with an appropriate tool (e.g., `iperf3`), across multiple configured bandwidth caps. Ping alone cannot validate throughput.
- [ ] **Jitter:** Collect many RTT samples and check variability under nonzero jitter settings.
- [ ] **Packet loss:** Send enough packets to estimate observed loss at several configured rates; test whether MPyC completes or fails gracefully.
- [ ] **Party independence:** Change Party 1's settings and verify the `tc` configurations of Parties 0 and 2 are unchanged. Note that communication *with* Party 1 will still be affected.
- [ ] **Directionality:** Confirm traffic shaping applies to **outgoing traffic** from each namespace. End-to-end RTT can reflect delay at both endpoints; one party's 50 ms egress delay produced ~50 ms additional ping RTT in the observed test.
- [ ] **Combined conditions:** Test latency + jitter + loss + bandwidth together, including realistic and extreme profiles.
- [ ] **MPyC integration:** Run the ORAM program under multiple network profiles; verify consistent outputs, completion, and sensible timing differences.
- [ ] **Lifecycle:** Verify `status`, `reset`, `teardown`, clean recreation, and behavior after a failed/partial `setup`.
- [ ] **Validation:** Check invalid party IDs, negative values, zero bandwidth, loss outside 0–100%, missing namespaces, and missing Linux tools.
- [ ] **Portability:** Confirm operation on the intended Linux/WSL2 environments, including virtual-environment dependency resolution and root permissions.


