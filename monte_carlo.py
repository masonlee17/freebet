#!/usr/bin/env python3
"""
monte_carlo.py - Monte Carlo P&L with confidence bands for Free Bet Blackjack.
Run with: python3 monte_carlo.py
Outputs:  charts/05_monte_carlo_pnl.png
"""

import random
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import os
import time

from freebet import FreeBetGame

os.makedirs('charts', exist_ok=True)

N_PATHS = 100
N_HANDS = 50_000
SAMPLE  = 500        # record cumulative P&L every N hands
BASE_SEED = 42

BLUE   = '#2E86AB'
GREEN  = '#3BB273'
ORANGE = '#E84855'

scenarios = [
    ('flat5',       5.0, 'Main=5u flat,  POG=1u',    BLUE),
    ('flat1',       1.0, 'Main=1u flat,  POG=1u',    GREEN),
    ('progressive', 1.0, 'Main progressive, POG=1u', ORANGE),
]

checkpoints = list(range(0, N_HANDS + 1, SAMPLE))
n_checks    = len(checkpoints)

# Theoretical EV slope (units lost per hand, combined main + POG)
# main edge ~0.75%, POG edge ~2.5%
EV_SLOPES = {
    'flat5':       -(5 * 0.0075 + 1 * 0.025),   # -0.0625/hand
    'flat1':       -(1 * 0.0075 + 1 * 0.025),   # -0.0325/hand
    'progressive': -(1 * 0.0075 + 1 * 0.025),   # same long-run as flat1
}

fig, axes = plt.subplots(1, 3, figsize=(18, 7))

for ax, (sc, start_mb, label, color) in zip(axes, scenarios):
    print(f"\n[{label}]  {N_PATHS} paths x {N_HANDS:,} hands each...")
    t0 = time.time()

    all_paths = np.zeros((N_PATHS, n_checks))  # column 0 = 0 (start)

    for p in range(N_PATHS):
        random.seed(BASE_SEED + p * 997)
        g       = FreeBetGame()
        mb      = start_mb
        running = 0.0
        ci      = 1  # checkpoint index; index 0 is the starting 0

        for i in range(N_HANDS):
            mn, pn   = g.play_hand(mb, 1.0)
            running += mn + pn

            if (i + 1) % SAMPLE == 0:
                all_paths[p, ci] = running
                ci += 1

            if sc == 'progressive':
                mb = (mb + 1) if mn > 0 else 1.0

        if (p + 1) % 25 == 0:
            elapsed = time.time() - t0
            print(f"  {p+1}/{N_PATHS} paths  ({elapsed:.0f}s)")

    x    = checkpoints
    p10  = np.percentile(all_paths, 10, axis=0)
    p25  = np.percentile(all_paths, 25, axis=0)
    p50  = np.percentile(all_paths, 50, axis=0)
    p75  = np.percentile(all_paths, 75, axis=0)
    p90  = np.percentile(all_paths, 90, axis=0)
    ev   = [EV_SLOPES[sc] * h for h in checkpoints]

    # Individual paths (very faint)
    for path in all_paths:
        ax.plot(x, path, color=color, alpha=0.04, linewidth=0.6)

    # Confidence bands
    ax.fill_between(x, p10, p90, alpha=0.18, color=color, label='10th–90th pct')
    ax.fill_between(x, p25, p75, alpha=0.35, color=color, label='25th–75th pct')

    # Median and EV
    ax.plot(x, p50, color=color, linewidth=2.2, label='Median')
    ax.plot(x, ev,  color='black', linewidth=1.4, linestyle='--', alpha=0.65, label='Theoretical EV')

    ax.axhline(0, color='#888888', linewidth=0.8)

    # Annotate final median and EV
    ax.annotate(f'{p50[-1]:+.0f}u', xy=(x[-1], p50[-1]),
                xytext=(x[-1] - 5000, p50[-1] + abs(p90[-1] - p50[-1]) * 0.25),
                fontsize=8, color=color, fontweight='bold')
    ax.annotate(f'EV {ev[-1]:+.0f}u', xy=(x[-1], ev[-1]),
                xytext=(x[-1] - 8000, ev[-1] - abs(p50[-1] - p10[-1]) * 0.25),
                fontsize=8, color='black', alpha=0.7)

    ax.set_title(label, fontsize=12, fontweight='bold', pad=10)
    ax.set_xlabel('Hands Played', fontsize=10)
    ax.set_ylabel('Net Units (Main + POG)', fontsize=10)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f'{int(v):,}'))
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.yaxis.grid(True, linestyle='--', alpha=0.4)
    ax.set_axisbelow(True)
    ax.legend(fontsize=8, loc='lower left')

    print(f"  Done. Final median: {p50[-1]:+.1f}u | EV: {ev[-1]:+.1f}u | "
          f"p10: {p10[-1]:+.1f}u | p90: {p90[-1]:+.1f}u")

fig.suptitle(
    f'Monte Carlo P&L — {N_PATHS} Independent Paths × {N_HANDS:,} Hands Each\n'
    'Bands: 10th–90th (light) and 25th–75th (dark) percentiles',
    fontsize=13, fontweight='bold', y=1.01
)
plt.tight_layout()
out = 'charts/05_monte_carlo_pnl.png'
plt.savefig(out, dpi=150, bbox_inches='tight')
plt.close()
print(f"\nSaved: {out}")
