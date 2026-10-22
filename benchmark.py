"""Benchmark Linear ORAM: time, bytes, rounds and memory per operation.

Run all three parties locally (parties 1 and 2 are spawned automatically):
    python benchmark.py -M3 --sizes 10 100 1000

or one terminal per party, as with linear.py:
    python benchmark.py -M3 -I0 --sizes 10 100
    python benchmark.py -M3 -I1 --sizes 10 100
    python benchmark.py -M3 -I2 --sizes 10 100

Under the network emulator (see networksetup.md):
    sudo .venv/bin/python -m network.launcher benchmark.py --sizes 10 100

Party 0 prints the results and optionally writes them to --csv.
"""
import argparse
import csv
import random
import statistics

from mpyc.runtime import mpc

import metrics
from linear import (BLOOD, secint, share_columns, lookup_by_index, write_by_index,
                    lookup_by_key, write_by_key)

OWNER = 0     # holds the table
CLIENT = 0    # makes the queries
FIELDS = ['n', 'op', 'time', 'bytes', 'messages', 'rounds', 'peak_mem']


def synthetic_table(n, rng):
    keys = rng.sample(range(100_000_000, 1_000_000_000), n)   # unique 9 digit BSNs
    vals = [rng.randrange(len(BLOOD)) for _ in range(n)]
    return keys, vals


def secret(value):
    # only CLIENT knows the real value, the rest contribute a placeholder
    return mpc.input(secint(value if mpc.pid == CLIENT else 0), senders=CLIENT)


# Each op is one ORAM access as seen by the client: input the query, run it.
OPS = {
    'lookup_by_index': lambda K, V, i, key, v: lookup_by_index(V, secret(i)),
    'write_by_index':  lambda K, V, i, key, v: write_by_index(V, secret(i), secret(v)),
    'lookup_by_key':   lambda K, V, i, key, v: lookup_by_key(K, V, secret(key)),
    'write_by_key':    lambda K, V, i, key, v: write_by_key(K, V, secret(key), secret(v)),
}


async def bench(args):
    rows = []
    rng = random.Random(args.seed)
    for n in args.sizes:
        keys, vals = synthetic_table(n, rng)   # same on every party (same seed), only OWNER's is used

        async with metrics.Measure(args.memory) as m:
            K, V = await share_columns(keys, vals, owner=OWNER)
            await mpc.gather(K, V)
        rows.append({'n': n, 'op': 'setup', **await metrics.combine(m.stats)})
        if mpc.pid == 0:
            print(fmt(rows[-1]), flush=True)

        for op in args.ops:
            runs = []
            for _ in range(args.repeat):
                i = rng.randrange(n)
                async with metrics.Measure(args.memory) as m:
                    await mpc.gather(OPS[op](K, V, i, keys[i], rng.randrange(len(BLOOD))))
                runs.append(await metrics.combine(m.stats))
            row = {'n': n, 'op': op, **runs[0]}
            row['time'] = statistics.median(r['time'] for r in runs)
            row['peak_mem'] = max(r['peak_mem'] for r in runs)
            rows.append(row)
            if mpc.pid == 0:
                print(fmt(row), flush=True)
    return rows


def fmt(row):
    return (f"{row['n']:>7} {row['op']:<16} {row['time']*1000:>10.1f} {row['bytes']:>12} "
            f"{row['messages']:>9} {row['rounds']:>7} {row['peak_mem']/1024:>11.1f}")


async def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--sizes', type=int, nargs='+', default=[10, 100, 1000],
                        help='table sizes n to benchmark')
    parser.add_argument('--ops', nargs='+', choices=list(OPS), default=list(OPS))
    parser.add_argument('--repeat', type=int, default=3, help='runs per op, median time reported')
    parser.add_argument('--seed', type=int, default=1)
    parser.add_argument('--no-memory', dest='memory', action='store_false',
                        help='skip tracemalloc (it slows Python down, so times are more accurate)')
    parser.add_argument('--csv', help='write results to this CSV file (party 0)')
    args = parser.parse_args()

    metrics.install()
    await mpc.start()
    if mpc.pid == 0:
        print(f'Linear ORAM benchmark, {len(mpc.parties)} parties, '
              f'time = median of {args.repeat}, totals over all parties')
        print(f"{'n':>7} {'op':<16} {'time (ms)':>10} {'bytes':>12} {'messages':>9} "
              f"{'rounds':>7} {'peak (KiB)':>11}")
    rows = await bench(args)
    await mpc.shutdown()

    if mpc.pid == 0 and args.csv:
        with open(args.csv, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=FIELDS)
            writer.writeheader()
            writer.writerows(rows)
        print(f'Wrote {args.csv}')


if __name__ == '__main__':
    mpc.run(main())
