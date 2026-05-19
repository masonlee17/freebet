# Free Bet Blackjack: Pot of Gold Side Bet Analysis

## Overview

This project simulates and analyzes the **Pot of Gold** side bet in Free Bet Blackjack, as offered at Sycuan Casino Resort. The simulation covers the side bet in isolation, the full main hand combined with the side bet, and several betting strategies across millions of hands.

---

## What is the Pot of Gold Bet?

The Pot of Gold is a side bet based on the number of **Free Bet Tokens** a player collects during a hand. Tokens are earned by:

- **Splitting** a non-10-value pair (1 token per split)
- **Doubling** on a two-card hard 9, 10, or 11 (1 token per double, including after splits)

Payouts are based on total tokens collected:

| Tokens | Payout (odds) | Total return |
|--------|--------------|--------------|
| 0      | Lose         | 0x           |
| 1      | 3 to 1       | 4x           |
| 2      | 12 to 1      | 13x          |
| 3      | 30 to 1      | 31x          |
| 4      | 50 to 1      | 51x          |
| 5+     | 100 to 1     | 101x         |

The bet loses entirely to a dealer blackjack regardless of tokens collected.

---

## Bug Fix: Token Counting Logic

The original simulation contained a critical bug in the recursive token-counting logic. When a split hand re-split, the card assignment used fixed index positions, causing a single card to be consumed by multiple hands simultaneously. This made the logic both over-count and under-count tokens depending on the split pattern.

The fix replaces the index-arithmetic recursion with a shared card pointer that advances depth-first (left hand before right hand), matching real deal order. This changed 980 of 371,293 five-card combinations (0.26%), with errors in both directions:

- 736 hands were previously under-counted (promoted to higher payout tiers)
- 244 hands were previously over-counted (demoted from 51x to 31x)

---

## Pot of Gold: Exact Probability Distribution (5-Card)

Computed from all 371,293 possible 5-card sequences (uniform infinite deck model):

| Payout | Hands     | Probability | EV Contribution |
|--------|-----------|-------------|-----------------|
| 0x     | 307,580   | 82.8402%    | 0.0000          |
| 4x     | 55,250    | 14.8804%    | 0.5952          |
| 13x    | 6,576     | 1.7711%     | 0.2302          |
| 31x    | 1,710     | 0.4606%     | 0.1428          |
| 51x    | 177       | 0.0477%     | 0.0243          |
| **Total** | 371,293 | 100%       | **0.9925**      |

**POG side bet RTP (5-card): 99.25%**
**House edge: 0.75%**

Note: 5-token hands (100:1 payout) require a minimum of 6 cards and cannot occur in a 5-card game. If the casino scores a 6th card, the model shifts to a 103.36% RTP, which would be a player edge. This suggests either the game uses a 5-card cap or real deck composition (finite shoe, without replacement) reduces the edge below 100%.

---

## Full Game Simulation: Main Hand + Pot of Gold

The full game simulator models:

- 6-deck shoe, reshuffled at 75% penetration
- Dealer stands on soft 17
- Push 22: dealer bust with 22 is a push on all live player hands (not a win)
- Free splits always taken on non-10-value pairs
- Free doubles always taken on two-card hard 9, 10, or 11
- Basic strategy for all other decisions
- Lammer model: player only ever risks their original main bet; split and double hands can win but cannot lose additional money beyond the original bet

### Lammer Model Details

In Free Bet Blackjack, the player's maximum loss per hand is always their original bet, regardless of how many free splits or doubles are taken. Each additional split hand (lammer) can win but contributes zero additional loss if it loses. Free doubles double the potential win without increasing the loss exposure.

This is a significant player benefit embedded in the main game and is correctly modeled in the simulation.

### Three-Scenario Results (1,000,000 hands each)

| Scenario | Main RTP | POG RTP | Combined RTP | House Edge |
|----------|----------|---------|--------------|------------|
| Main=5u flat, POG=1u | 99.23% | 97.58% | 98.96% | 1.04% |
| Main=1u flat, POG=1u | 99.04% | 97.08% | 98.06% | 1.94% |
| Main=1u progressive, POG=1u | 99.02% | 96.55% | 98.07% | 1.93% |

### Cross-Outcome Frequency (500K hands, main=1u, POG=1u)

| Outcome | Frequency |
|---------|-----------|
| Both win | 6.94% |
| Main wins, POG loses | 42.8% |
| POG wins, main loses | 6.51% |
| Both lose | 41.1% |
| Push or mixed | 2.65% |

The Pot of Gold side bet can pay out while the main hand loses. This occurs approximately 6.5% of the time.

---

## Strategy Analysis

### Key Relationship

The main hand carries a house edge of approximately **0.75%**. The Pot of Gold side bet carries a house edge of approximately **2.5%** (from simulation). Every unit bet on the POG costs 3.3x more in expected loss than the same unit on the main hand.

### Combined House Edge by Bet Ratio

The combined house edge follows:

```
combined_edge = (main_bet * 0.0075 + pog_bet * 0.025) / (main_bet + pog_bet)
```

| Main Bet | POG Bet | Combined Edge | Loss per 1,000 hands |
|----------|---------|---------------|----------------------|
| 1        | 1       | 1.625%        | 32.5 units           |
| 2        | 1       | 1.33%         | 40 units             |
| 5        | 1       | 1.04%         | 62.5 units           |
| 10       | 1       | 0.91%         | 100 units            |
| 20       | 1       | 0.83%         | 175 units            |
| 50       | 1       | 0.77%         | 400 units            |

As the main bet increases relative to the POG, the combined house edge approaches the main hand edge (0.75%). However, the absolute dollar loss per hand increases linearly with main bet size.

### Progressive Betting

A progressive strategy (+1 unit on main after each win, reset to 1 on loss) does not change the long-run expected value. It produces the same house edge percentage as flat betting, but increases total units wagered over a session, which increases absolute dollar losses.

Flat vs progressive at main=20, POG=1 (1M hands):
- Flat: 21,000,000 units wagered, -195,430 net
- Progressive: 21,601,024 units wagered, -201,442 net

Progressive is strictly worse for minimizing total loss.

---

## Optimal Strategy

**To minimize house edge percentage:** maximize the main bet relative to the POG bet. At 50:1 the combined edge drops to 0.77%.

**To minimize absolute dollar loss per session:** bet the minimum on both. At 1:1 you lose approximately 32.5 units per 1,000 hands, compared to 400 units per 1,000 hands at 50:1.

**Recommendation:** The POG is the expensive part of this strategy. Keeping the main bet at a level that dilutes the POG drag (roughly 5:1 or higher) reduces the blended house edge below 1.1% while keeping absolute exposure manageable.

Flat betting strictly dominates progressive betting for this game under any goal of loss minimization.

---

## Charts

All charts are in the `charts/` directory:

| File | Description |
|------|-------------|
| `01_pog_distribution.png` | POG payout tier probabilities (log scale) |
| `02_pog_ev_breakdown.png` | Frequency and EV contribution per tier |
| `03_ratio_vs_edge.png` | Combined house edge vs main:POG ratio |
| `04_loss_per_hand.png` | Expected loss per hand and house edge by main bet size |
| `05_cumulative_pnl.png` | Cumulative P&L over 200,000 hands across 3 scenarios |
| `06_outcome_breakdown.png` | Hand outcome distribution (both win, split outcomes, both lose) |
| `07_token_frequency.png` | POG token frequency from 500K simulated hands |
| `08_strategy_comparison.png` | Summary house edge comparison across strategies |

---

## Files

| File | Description |
|------|-------------|
| `freebet.py` | Core simulator: FreeBetSimulator (POG enumeration) and FreeBetGame (full game) |
| `graphs.py` | Chart generation script |
| `freebet_all_combinations.csv` | All 371,293 five-card combinations with corrected payouts |
| `freebet_analysis_6card.csv` | All 4,826,809 six-card combinations |
| `Sycuan-Casino-Resort-Guide-To-Free-Bet-Blackjack.pdf` | Source rules document |

---

## Methodology Notes

- Card probabilities use a uniform infinite deck model (each of 13 ranks has probability 1/13). This is equivalent to sampling with replacement and is a standard approximation for multi-deck shoes.
- 10-value cards (T, J, Q, K) are treated as four distinct ranks, each with probability 1/13, which correctly represents 16/52 combined probability matching a real deck.
- The lammer mechanic means player maximum loss per hand is always the original main bet, regardless of split count.
- Basic strategy is standard except free splits and free doubles are always accepted.
- Push 22 rule is applied but basic strategy is not adjusted for it (minor EV approximation).
