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



