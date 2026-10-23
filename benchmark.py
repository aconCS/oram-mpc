"""Benchmark Linear ORAM: time, bytes, rounds and memory per operation.

Table sizes are 10^0, 10^1, ..., 10^max-exp, taken as the first n rows of
full_table.csv (or give them explicitly with --sizes).

Run all three parties locally (parties 1 and 2 are spawned automatically):
    python benchmark.py -M3 --max-exp 3

or one terminal per party, as with linear.py:
    python benchmark.py -M3 -I0 --sizes 10 100
    python benchmark.py -M3 -I1 --sizes 10 100
    python benchmark.py -M3 -I2 --sizes 10 100

Under the network emulator (see networksetup.md):
    sudo .venv/bin/python -m network.launcher benchmark.py --sizes 10 100

Party 0 prints the results and can save them with --csv (for scripts, see
plot.py) and --md (a readable report). Units are the same everywhere:
time in ms, data sent and peak memory in KiB.
"""
import argparse
import csv
import datetime
import random
import statistics

from mpyc.runtime import mpc

import metrics
from linear import (BLOOD, secint, read_columns, share_columns, lookup_by_index,
                    write_by_index, lookup_by_key, write_by_key)

OWNER = 0     # holds the table
CLIENT = 0    # makes the queries
TABLE = 'full_table.csv'

# output columns: (name, header in terminal/markdown, format)
COLUMNS = [
    ('n',          'n',           '{}'),
    ('op',         'op',          '{}'),
    ('time_ms',    'time (ms)',   '{:.1f}'),
    ('sent_kib',   'sent (KiB)',  '{:.2f}'),
    ('messages',   'messages',    '{}'),
    ('rounds',     'rounds',      '{}'),
    ('peak_kib',   'peak (KiB)',  '{:.1f}'),
]


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
    if mpc.pid == OWNER:   # only the owner reads the table, once, up to the largest size
        all_keys, all_vals = read_columns(args.table, 'bsn', 'blood_code', nrows=max(args.sizes))
    for n in args.sizes:
        if mpc.pid == OWNER:
            keys, vals = all_keys[:n], all_vals[:n]
        else:
            keys = vals = [0] * n   # placeholders, ignored by share_columns and secret()

        async with metrics.Measure(args.memory) as m:
            K, V = await share_columns(keys, vals, owner=OWNER)
            await mpc.gather(K, V)
        rows.append(in_units(n, 'setup', await metrics.combine(m.stats)))
        if mpc.pid == 0:
            print(fmt(rows[-1]), flush=True)

        for op in args.ops:
            runs = []
            for _ in range(args.repeat):
                i = rng.randrange(n)
                async with metrics.Measure(args.memory) as m:
                    await mpc.gather(OPS[op](K, V, i, keys[i], rng.randrange(len(BLOOD))))
                runs.append(await metrics.combine(m.stats))
            stats = dict(runs[0])   # bytes, messages, rounds are the same every run
            stats['time'] = statistics.median(r['time'] for r in runs)
            stats['peak_mem'] = max(r['peak_mem'] for r in runs)
            row = in_units(n, op, stats)
            rows.append(row)
            if mpc.pid == 0:
                print(fmt(row), flush=True)
    return rows


def in_units(n, op, stats):
    # metrics gives seconds and bytes, convert to the output units
    return {
        'n': n,
        'op': op,
        'time_ms': round(stats['time'] * 1000, 3),
        'sent_kib': round(stats['bytes'] / 1024, 3),
        'messages': stats['messages'],
        'rounds': stats['rounds'],
        'peak_kib': round(stats['peak_mem'] / 1024, 3),
    }


WIDTHS = [7, 16, 10, 12, 9, 7, 11]


def fmt(row):
    cells = [f.format(row[name]) for name, _, f in COLUMNS]
    return ' '.join(c.ljust(w) if name == 'op' else c.rjust(w)
                    for c, w, (name, _, _) in zip(cells, WIDTHS, COLUMNS))


def header():
    return ' '.join(h.ljust(w) if name == 'op' else h.rjust(w)
                    for w, (name, h, _) in zip(WIDTHS, COLUMNS))


def write_csv(path, rows):
    with open(path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=[name for name, _, _ in COLUMNS])
        writer.writeheader()
        writer.writerows(rows)


def write_md(path, rows, args):
    md = lambda cells: '| ' + ' | '.join(cells) + ' |'
    lines = [
        '# Linear ORAM benchmark',
        '',
        f"- date: {datetime.datetime.now():%Y-%m-%d %H:%M}",
        f'- parties: {len(mpc.parties)}',
        f"- table: `{args.table}`, sizes: {', '.join(map(str, args.sizes))}",
        f'- repeat: {args.repeat} (time is the median), seed: {args.seed}',
        f"- memory tracking: {'on' if args.memory else 'off'}",
        '- time and peak memory: slowest party; sent and messages: sum over all parties',
        '',
        '## All results',
        '',
        md([h for _, h, _ in COLUMNS]),
        md(['---:' if name != 'op' else '---' for name, _, _ in COLUMNS]),
    ]
    lines += [md([f.format(r[name]) for name, _, f in COLUMNS]) for r in rows]

    # time per size, one column per op, to compare growth at a glance
    ops = list(dict.fromkeys(r['op'] for r in rows))
    times = {(r['n'], r['op']): r['time_ms'] for r in rows}
    lines += ['', '## Time (ms) per size', '', md(['n'] + ops), md(['---:'] * (len(ops) + 1))]
    lines += [md([str(n)] + [f'{times[n, op]:.1f}' for op in ops]) for n in args.sizes]

    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')


async def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--max-exp', type=int, default=3,
                        help='benchmark sizes 10^0 .. 10^max-exp')
    parser.add_argument('--sizes', type=int, nargs='+',
                        help='explicit table sizes n, overrides --max-exp')
    parser.add_argument('--table', default=TABLE, help='CSV with bsn and blood_code columns')
    parser.add_argument('--ops', nargs='+', choices=list(OPS), default=list(OPS))
    parser.add_argument('--repeat', type=int, default=3, help='runs per op, median time reported')
    parser.add_argument('--seed', type=int, default=1)
    parser.add_argument('--no-memory', dest='memory', action='store_false',
                        help='skip tracemalloc (it slows Python down, so times are more accurate)')
    parser.add_argument('--csv', help='write results to this CSV file (party 0)')
    parser.add_argument('--md', help='write a Markdown report to this file (party 0)')
    args = parser.parse_args()
    if args.sizes is None:
        args.sizes = [10**k for k in range(args.max_exp + 1)]

    metrics.install()
    await mpc.start()
    if mpc.pid == 0:
        print(f'Linear ORAM benchmark, {len(mpc.parties)} parties, '
              f'time = median of {args.repeat}, totals over all parties')
        print(header())
    rows = await bench(args)
    await mpc.shutdown()

    if mpc.pid == 0:
        if args.csv:
            write_csv(args.csv, rows)
            print(f'Wrote {args.csv}')
        if args.md:
            write_md(args.md, rows, args)
            print(f'Wrote {args.md}')


if __name__ == '__main__':
    mpc.run(main())
