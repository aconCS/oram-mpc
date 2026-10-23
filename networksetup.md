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

 1. Create network
sudo .venv/bin/python -m network.cli setup

 2. Configure conditions (example: Party 1, 50ms latency)
sudo .venv/bin/python -m network.cli set --party 1 --latency 50

3. Check configuration
sudo .venv/bin/python -m network.cli status

 4. Run MPyC experiment
sudo .venv/bin/python -m network.launcher

 5. Reset network conditions (optional)
sudo .venv/bin/python -m network.cli reset

 6. Remove network when finished
sudo .venv/bin/python -m network.cli teardown





