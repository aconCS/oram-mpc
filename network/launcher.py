
import os
import subprocess


def launch(script="linear.py", parties=3, base_port=11365):
    addresses = [
        f"10.10.0.{10 + i}:{base_port + i}"
        for i in range(parties)
    ]

    processes = []

    try:
        for party in range(parties):
            command = [
                "ip", "netns", "exec", f"mpc{party}",
                os.path.abspath(".venv/bin/python"),
                os.path.abspath(script),
                "-I", str(party),
            ]

            for address in addresses:
                command.extend(["-P", address])

            processes.append(subprocess.Popen(command))

        exit_codes = [process.wait() for process in processes]

        if any(code != 0 for code in exit_codes):
            raise RuntimeError(f"MPyC parties failed: {exit_codes}")

    finally:
        for process in processes:
            if process.poll() is None:
                process.terminate()

        for process in processes:
            if process.poll() is None:
                process.wait()


if __name__ == "__main__":
    launch()
