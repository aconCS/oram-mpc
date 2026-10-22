
import argparse
from .emulator import NetworkEmulator


def main():
    parser = argparse.ArgumentParser(description="MPC Network Emulator")
    commands = parser.add_subparsers(dest="command", required=True)

    commands.add_parser("setup")
    commands.add_parser("status")
    commands.add_parser("reset")
    commands.add_parser("teardown")

    configure = commands.add_parser("set")
    configure.add_argument("--party", type=int, required=True)
    configure.add_argument("--latency", type=float, default=0)
    configure.add_argument("--bandwidth", type=float, default=1000)
    configure.add_argument("--jitter", type=float, default=0)
    configure.add_argument("--loss", type=float, default=0)

    args = parser.parse_args()
    emulator = NetworkEmulator()

    if args.command == "setup":
        emulator.setup()
    elif args.command == "set":
        emulator.configure(
            party=args.party,
            latency=args.latency,
            bandwidth=args.bandwidth,
            jitter=args.jitter,
            loss=args.loss
        )
    elif args.command == "status":
        emulator.status()
    elif args.command == "reset":
        emulator.reset()
    elif args.command == "teardown":
        emulator.teardown()


if __name__ == "__main__":
    main()
