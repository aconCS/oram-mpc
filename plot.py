"""Plot benchmark results: one chart per metric, cost against table size n.

    python plot.py results.csv
    python plot.py local.csv lan.csv wan.csv --out plots

Each CSV is one run of benchmark.py --csv. Colour and marker show the
operation, line style shows the run (file name), so several runs (e.g.
different network settings) can be compared in one chart.
Writes one PNG per metric plus overview.png with all of them.
"""
import argparse
import os

import matplotlib
matplotlib.use('Agg')   # no window, only files
import matplotlib.pyplot as plt
import pandas as pd

# (column, title, log y axis)
METRICS = [
    ('time_ms',  'Time (ms)',             True),
    ('sent_kib', 'Data sent (KiB)',       True),
    ('rounds',   'Communication rounds',  False),
    ('peak_kib', 'Peak memory (KiB)',     False),
]

# fixed colour + marker per op, so an op looks the same in every chart
OP_STYLE = {
    'lookup_by_index': ('#2a78d6', 'o'),
    'write_by_index':  ('#eb6834', 's'),
    'lookup_by_key':   ('#1baf7a', '^'),
    'write_by_key':    ('#eda100', 'D'),
    'setup':           ('#e87ba4', 'v'),
}
RUN_STYLES = ['-', '--', ':', '-.']

SURFACE = '#fcfcfb'
TEXT = '#0b0b0b'
TEXT_2 = '#52514e'
GRID = '#e4e3df'


def load(paths):
    frames = []
    for path in paths:
        df = pd.read_csv(path)
        df['run'] = os.path.splitext(os.path.basename(path))[0]
        frames.append(df)
    return pd.concat(frames, ignore_index=True)


def style_axes(ax, title, log_y):
    ax.set_facecolor(SURFACE)
    ax.set_title(title, color=TEXT, loc='left', fontsize=11)
    ax.set_xscale('log')
    if log_y:
        ax.set_yscale('log')
    else:
        ax.set_yscale('linear')
        ax.set_ylim(0, None)
        ax.yaxis.get_major_locator().set_params(integer=True)
    ax.set_xlabel('table size n (rows)', color=TEXT_2)
    ax.grid(True, which='major', color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    for side in ('top', 'right'):
        ax.spines[side].set_visible(False)
    for side in ('left', 'bottom'):
        ax.spines[side].set_color(GRID)
    ax.tick_params(colors=TEXT_2, which='both')


def draw(ax, df, column, title, log_y):
    style_axes(ax, title, log_y)
    runs = list(dict.fromkeys(df['run']))
    for op, (colour, marker) in OP_STYLE.items():
        for run, ls in zip(runs, RUN_STYLES):
            part = df[(df['op'] == op) & (df['run'] == run)].sort_values('n')
            if part.empty:
                continue
            label = op if len(runs) == 1 else f'{op} ({run})'
            ax.plot(part['n'], part[column], ls, color=colour, marker=marker,
                    markersize=6, linewidth=1.5, label=label,
                    markeredgecolor=SURFACE, markeredgewidth=1)
            if column == 'rounds':
                ax.set_ylim(0, 60)


def legend(fig, ax):
    handles, labels = ax.get_legend_handles_labels()
    fig.legend(handles, labels, loc='outside lower center', ncol=min(len(labels), 3),
               frameon=False, labelcolor=TEXT_2, fontsize=9)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('csv', nargs='+', help='result files from benchmark.py --csv')
    parser.add_argument('--out', default='results/plots', help='folder for the PNGs')
    args = parser.parse_args()

    df = load(args.csv)
    runs = list(dict.fromkeys(df['run']))
    if len(runs) > len(RUN_STYLES):
        parser.error(f'at most {len(RUN_STYLES)} CSVs per plot (one line style each)')

    # memory is all zeros when the benchmark ran with --no-memory
    metrics = [m for m in METRICS if df[m[0]].gt(0).any()]
    os.makedirs(args.out, exist_ok=True)

    for column, title, log_y in metrics:
        fig, ax = plt.subplots(figsize=(7, 4.8), layout='constrained', facecolor=SURFACE)
        draw(ax, df, column, title, log_y)
        legend(fig, ax)
        path = os.path.join(args.out, f'{column}.png')
        fig.savefig(path, dpi=150)
        plt.close(fig)
        print(f'Wrote {path}')

    cols = 2
    rows = (len(metrics) + 1) // cols
    fig, axes = plt.subplots(rows, cols, figsize=(12, 4.2 * rows), layout='constrained',
                             facecolor=SURFACE, squeeze=False)
    for ax, (column, title, log_y) in zip(axes.flat, metrics):
        draw(ax, df, column, title, log_y)
    for ax in list(axes.flat)[len(metrics):]:
        ax.set_visible(False)
    fig.suptitle('Linear ORAM cost vs table size', color=TEXT, x=0.01, ha='left')
    legend(fig, axes.flat[0])
    path = os.path.join(args.out, 'overview.png')
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f'Wrote {path}')


if __name__ == '__main__':
    main()
