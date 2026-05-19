#!/usr/bin/env python3
"""
graphs.py - Generate all analysis charts for Free Bet Blackjack Pot of Gold study.
Run with: python3 graphs.py
Outputs charts/ directory with all PNGs.
"""

import os
import random
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from collections import Counter

from freebet import FreeBetGame, FreeBetSimulator

os.makedirs('charts', exist_ok=True)

SEED = 42
random.seed(SEED)

BLUE   = '#2E86AB'
ORANGE = '#E84855'
GREEN  = '#3BB273'
PURPLE = '#7B2D8B'
GREY   = '#AAAAAA'
DARK   = '#1a1a2e'

def style_ax(ax, title, xlabel, ylabel):
    ax.set_title(title, fontsize=14, fontweight='bold', pad=12)
    ax.set_xlabel(xlabel, fontsize=11)
    ax.set_ylabel(ylabel, fontsize=11)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.yaxis.grid(True, linestyle='--', alpha=0.5)
    ax.set_axisbelow(True)


# ── 1. POG payout distribution (5-card exact enumeration) ───────────────────
print("Chart 1: POG payout distribution...")

sim = FreeBetSimulator()
dist5 = {0: 307580, 4: 55250, 13: 6576, 31: 1710, 51: 177}
total5 = 371293
labels5 = ['0 (lose)', '4x (1 token)', '13x (2 tokens)', '31x (3 tokens)', '51x (4 tokens)']
probs5  = [dist5[k] / total5 * 100 for k in sorted(dist5)]
colors5 = [GREY, BLUE, GREEN, ORANGE, PURPLE]

fig, ax = plt.subplots(figsize=(9, 5))
bars = ax.bar(labels5, probs5, color=colors5, edgecolor='white', linewidth=0.8)
for bar, p in zip(bars, probs5):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
            f'{p:.3f}%', ha='center', va='bottom', fontsize=9)
style_ax(ax, 'Pot of Gold: Payout Distribution (5-Card Exact Enumeration)',
         'Payout Tier', 'Probability (%)')
ax.set_yscale('log')
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:.3g}%'))
plt.tight_layout()
plt.savefig('charts/01_pog_distribution.png', dpi=150)
plt.close()


# ── 2. POG payout distribution (log scale, annotated with EV contribution) ──
print("Chart 2: EV contribution by tier...")

ev_contribs = [dist5[k] * k / total5 for k in sorted(dist5)]
fig, axes = plt.subplots(1, 2, figsize=(12, 5))

ax = axes[0]
ax.bar(labels5, probs5, color=colors5, edgecolor='white')
style_ax(ax, 'Frequency by Tier', 'Payout', 'Probability (%)')
ax.set_yscale('log')
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:.3g}%'))

ax = axes[1]
bars2 = ax.bar(labels5, ev_contribs, color=colors5, edgecolor='white')
for bar, v in zip(bars2, ev_contribs):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.002,
            f'{v:.4f}', ha='center', va='bottom', fontsize=9)
style_ax(ax, 'EV Contribution by Tier', 'Payout', 'Expected Return per Hand')
ax.axhline(sum(ev_contribs), color=ORANGE, linestyle='--', linewidth=1.5,
           label=f'Total EV = {sum(ev_contribs):.4f}')
ax.legend()

fig.suptitle('Pot of Gold Side Bet Analysis (5-Card)', fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig('charts/02_pog_ev_breakdown.png', dpi=150, bbox_inches='tight')
plt.close()


# ── 3. Main:POG ratio vs combined house edge ─────────────────────────────────
print("Chart 3: Ratio vs house edge (theoretical)...")

main_edge = 0.0075
pog_edge  = 0.0250
ratios = np.linspace(1, 100, 300)
combined_edges = [(r * main_edge + pog_edge) / (r + 1) * 100 for r in ratios]

fig, ax = plt.subplots(figsize=(9, 5))
ax.plot(ratios, combined_edges, color=BLUE, linewidth=2.5)
ax.axhline(main_edge * 100, color=GREEN, linestyle='--', linewidth=1.5,
           label=f'Main hand edge ({main_edge*100:.2f}%)')
ax.axhline(pog_edge * 100, color=ORANGE, linestyle='--', linewidth=1.5,
           label=f'POG edge ({pog_edge*100:.2f}%)')
# Mark key ratios
for r in [1, 5, 10, 20, 50]:
    e = (r * main_edge + pog_edge) / (r + 1) * 100
    ax.scatter([r], [e], color=PURPLE, zorder=5, s=60)
    ax.annotate(f'{r}:1\n{e:.2f}%', xy=(r, e), xytext=(r+1.5, e+0.05),
                fontsize=8, color=PURPLE)
style_ax(ax, 'Combined House Edge vs Main:POG Bet Ratio',
         'Main Bet Size (POG = 1 unit)', 'Combined House Edge (%)')
ax.legend()
ax.set_xlim(0, 105)
plt.tight_layout()
plt.savefig('charts/03_ratio_vs_edge.png', dpi=150)
plt.close()


# ── 4. Expected loss per hand at different strategies ────────────────────────
print("Chart 4: Loss per hand by strategy...")

main_bets  = [1, 2, 5, 10, 20, 50]
loss_hands = [mb * main_edge + pog_edge for mb in main_bets]
total_wage = [mb + 1 for mb in main_bets]
edge_pcts  = [l / w * 100 for l, w in zip(loss_hands, total_wage)]

fig, axes = plt.subplots(1, 2, figsize=(12, 5))

ax = axes[0]
bars = ax.bar([str(m) for m in main_bets], [l * 1000 for l in loss_hands],
              color=BLUE, edgecolor='white')
for bar, l in zip(bars, loss_hands):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
            f'{l*1000:.2f}', ha='center', va='bottom', fontsize=9)
style_ax(ax, 'Expected Loss Per 1,000 Hands', 'Main Bet Size (POG = 1 unit)', 'Units Lost')

ax = axes[1]
bars2 = ax.bar([str(m) for m in main_bets], edge_pcts, color=ORANGE, edgecolor='white')
for bar, e in zip(bars2, edge_pcts):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
            f'{e:.2f}%', ha='center', va='bottom', fontsize=9)
style_ax(ax, 'Combined House Edge by Main Bet Size', 'Main Bet Size (POG = 1 unit)', 'House Edge (%)')

fig.suptitle('Cost Analysis: Main Bet Size vs POG = 1 Unit', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('charts/04_loss_per_hand.png', dpi=150, bbox_inches='tight')
plt.close()


# ── 5. Simulation: three scenarios cumulative P&L ────────────────────────────
print("Chart 5: Cumulative P&L across 3 scenarios (200K hands)...")

random.seed(SEED)
N_TRACK = 200_000
SAMPLE  = 500  # record every N hands

scenarios = [
    ('flat5',       5.0,  'Main=5u flat, POG=1u',        BLUE),
    ('flat1',       1.0,  'Main=1u flat, POG=1u',         GREEN),
    ('progressive', 1.0,  'Main progressive, POG=1u',     ORANGE),
]

fig, ax = plt.subplots(figsize=(11, 6))

for sc, start_mb, label, color in scenarios:
    random.seed(SEED)
    g = FreeBetGame()
    mb = start_mb
    cumulative = [0]
    running = 0.0
    for i in range(N_TRACK):
        mn, pn = g.play_hand(mb, 1.0)
        running += mn + pn
        if (i + 1) % SAMPLE == 0:
            cumulative.append(running)
        if sc == 'progressive':
            mb = mb + 1 if mn > 0 else 1.0
    x = [i * SAMPLE for i in range(len(cumulative))]
    ax.plot(x, cumulative, color=color, linewidth=1.8, label=label, alpha=0.9)

ax.axhline(0, color='black', linewidth=0.8, linestyle='-')
style_ax(ax, 'Cumulative P&L: 200,000 Hands (Main + POG Combined)',
         'Hands Played', 'Net Units (Main + POG)')
ax.legend(loc='lower left')
ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{int(x):,}'))
plt.tight_layout()
plt.savefig('charts/05_cumulative_pnl.png', dpi=150)
plt.close()


# ── 6. Win outcome breakdown ─────────────────────────────────────────────────
print("Chart 6: Hand outcome breakdown...")

random.seed(SEED)
g = FreeBetGame()
N_OUT = 500_000

both_win = main_win_pog_lose = pog_win_main_lose = both_lose = push_hands = 0

for _ in range(N_OUT):
    mn, pn = g.play_hand(1.0, 1.0)
    if   mn > 0 and pn > 0:  both_win         += 1
    elif mn > 0 and pn <= 0: main_win_pog_lose += 1
    elif mn < 0 and pn > 0:  pog_win_main_lose += 1
    elif mn < 0 and pn < 0:  both_lose         += 1
    else:                     push_hands        += 1

outcome_labels  = ['Both win', 'Main win\nPOG lose', 'POG win\nMain lose', 'Both lose', 'Push/mixed']
outcome_counts  = [both_win, main_win_pog_lose, pog_win_main_lose, both_lose, push_hands]
outcome_colors  = [GREEN, BLUE, ORANGE, ORANGE, GREY]
outcome_colors[3] = '#CC3333'

fig, axes = plt.subplots(1, 2, figsize=(12, 5))

ax = axes[0]
wedges, texts, autotexts = ax.pie(
    outcome_counts,
    labels=outcome_labels,
    colors=outcome_colors,
    autopct='%1.1f%%',
    startangle=90,
    pctdistance=0.75,
    wedgeprops={'edgecolor': 'white', 'linewidth': 1.5}
)
for t in autotexts:
    t.set_fontsize(9)
ax.set_title('Hand Outcome Distribution\n(500K hands, main=1u, POG=1u)',
             fontsize=12, fontweight='bold')

ax = axes[1]
pcts = [c / N_OUT * 100 for c in outcome_counts]
bars = ax.bar(outcome_labels, pcts, color=outcome_colors, edgecolor='white')
for bar, p in zip(bars, pcts):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2,
            f'{p:.1f}%', ha='center', va='bottom', fontsize=9)
style_ax(ax, 'Hand Outcome Frequencies', 'Outcome', 'Frequency (%)')

plt.tight_layout()
plt.savefig('charts/06_outcome_breakdown.png', dpi=150, bbox_inches='tight')
plt.close()


# ── 7. POG token frequency from live simulation ──────────────────────────────
print("Chart 7: POG token frequency from simulation...")

random.seed(SEED)
g = FreeBetGame()
token_counts = Counter()
N_TOK = 500_000
for _ in range(N_TOK):
    mn, pn = g.play_hand(1.0, 1.0)
    # reverse-engineer tokens from pog_net
    # pog_net = (payout - 1) if win, else -1
    # payout 0->0t, 4->1t, 13->2t, 31->3t, 51->4t, 101->5t
    payout_map = {-1: 0, 3: 1, 12: 2, 30: 3, 50: 4, 100: 5}
    t = payout_map.get(round(pn), 0)
    token_counts[t] += 1

tok_labels = ['0 tokens\n(lose)', '1 token\n(3:1)', '2 tokens\n(12:1)',
              '3 tokens\n(30:1)', '4 tokens\n(50:1)', '5+ tokens\n(100:1)']
tok_vals   = [token_counts[i] / N_TOK * 100 for i in range(6)]
tok_colors = [GREY, BLUE, GREEN, ORANGE, PURPLE, '#E8A838']

fig, ax = plt.subplots(figsize=(9, 5))
bars = ax.bar(tok_labels, tok_vals, color=tok_colors, edgecolor='white')
for bar, v in zip(bars, tok_vals):
    if v > 0:
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                f'{v:.3f}%', ha='center', va='bottom', fontsize=9)
style_ax(ax, 'POG Token Frequency (500K Simulated Hands)',
         'Token Count', 'Frequency (%)')
ax.set_yscale('log')
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:.3g}%'))
plt.tight_layout()
plt.savefig('charts/07_token_frequency.png', dpi=150)
plt.close()


# ── 8. Summary: house edge comparison bar ────────────────────────────────────
print("Chart 8: Summary comparison...")

compare_labels  = ['Main hand\nalone', 'POG side\nbet alone', '1:1 combined', '5:1 combined',
                   '20:1 combined', 'Progressive\n(1:1)']
compare_edges   = [
    main_edge * 100,
    pog_edge  * 100,
    (1*main_edge + pog_edge) / 2 * 100,
    (5*main_edge + pog_edge) / 6 * 100,
    (20*main_edge + pog_edge) / 21 * 100,
    (1*main_edge + pog_edge) / 2 * 100,  # progressive same as flat long-run
]
compare_colors  = [BLUE, ORANGE, PURPLE, GREEN, GREEN, GREY]

fig, ax = plt.subplots(figsize=(10, 5))
bars = ax.bar(compare_labels, compare_edges, color=compare_colors, edgecolor='white', width=0.6)
for bar, e in zip(bars, compare_edges):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
            f'{e:.2f}%', ha='center', va='bottom', fontsize=10, fontweight='bold')
style_ax(ax, 'House Edge by Strategy (Lower = Better for Player)',
         'Strategy', 'House Edge (%)')
ax.set_ylim(0, max(compare_edges) * 1.3)
plt.tight_layout()
plt.savefig('charts/08_strategy_comparison.png', dpi=150)
plt.close()


print("\nAll charts saved to charts/")
print(os.listdir('charts'))
