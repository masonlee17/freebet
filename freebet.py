#!/usr/bin/env python3
"""
Freebet - 5 Card Free Bet Blackjack Simulation
Simulates a 5-card game with specific payout rules based on card combinations.
"""

import random
import csv
import argparse
from typing import List, Tuple, Dict

class FreeBetSimulator:
    def __init__(self):
        # Card values for calculation (A=11 always, 2-9=pip value, T=J=Q=K=10)
        self.card_values = {
            'A': 11, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
            'T': 10, 'J': 10, 'Q': 10, 'K': 10
        }
        
        # All possible cards
        self.cards = ['A', '2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K']
        
    def get_card_value(self, card: str) -> int:
        """Get numeric value of a card"""
        return self.card_values[card]
    
    def is_face_card(self, card: str) -> bool:
        """Check if card is a face card (T, J, Q, K)"""
        return card in ['T', 'J', 'Q', 'K']
    
    def is_double_opportunity(self, val1: int, val2: int) -> bool:
        """Check if two values sum to 9, 10, or 11 (double opportunity)"""
        return (val1 + val2) in [9, 10, 11]
    
    def calculate_payout(self, cards: List[str]) -> int:
        """
        Calculate payout based on free bet blackjack rules
        
        Args:
            cards: List of 2 to 10 cards as strings
            
        Returns:
            Payout amount
        """
        if len(cards) < 2 or len(cards) > 10:
            raise ValueError("Must provide between 2 and 10 cards")
        
        # Rule 1 - Auto fail
        if self.is_face_card(cards[0]) or self.is_face_card(cards[1]):
            return 0
        
        # Use recursive approach to calculate tokens
        tokens = self._calculate_tokens_recursive(cards)
        
        # Convert tokens to payout (cap at 5 tokens = 101 payout)
        if tokens == 0:
            return 0
        elif tokens == 1:
            return 4
        elif tokens == 2:
            return 13
        elif tokens == 3:
            return 31
        elif tokens == 4:
            return 51
        else:
            return 101  # Cap at 5+ tokens
    
    def _calculate_tokens_recursive(self, cards: List[str]) -> int:
        """
        Calculate tokens using a shared card pointer, playing hands depth-first left to right.
        Each card is consumed exactly once, matching real deal order after splits.
        """
        max_cards = len(cards)
        ptr = [2]  # index of next card to deal; cards[0] and cards[1] are the starting hand
        tokens = [0]

        def play_hand(c1: str, c2: str) -> None:
            if c1 == c2:
                # Pair: split, then play left sub-hand before right (depth-first)
                tokens[0] += 1
                if ptr[0] < max_cards:
                    next_c = cards[ptr[0]]; ptr[0] += 1
                    play_hand(c1, next_c)
                if ptr[0] < max_cards:
                    next_c = cards[ptr[0]]; ptr[0] += 1
                    play_hand(c2, next_c)
            else:
                if self.is_double_opportunity(self.get_card_value(c1), self.get_card_value(c2)):
                    tokens[0] += 1

        play_hand(cards[0], cards[1])
        return tokens[0]
    
    def _display_analysis_recursive(self, cards: List[str], start_index: int, depth: int) -> None:
        """
        Recursively display analysis for free bet blackjack
        
        Args:
            cards: List of cards
            start_index: Starting index for this hand
            depth: Current depth for indentation
        """
        if start_index >= len(cards) - 1:
            return
        
        indent = "  " + "  " * depth
        
        # Check if we have a pair (split)
        if cards[start_index] == cards[start_index + 1]:
            if depth == 0:
                print(f"  🎯 Initial split: {cards[start_index]} + {cards[start_index + 1]}")
            else:
                print(f"{indent}→ Split: {cards[start_index]} = {cards[start_index + 1]}")
            
            # Process the split hands - each gets one card
            if start_index + 2 < len(cards):
                # First split hand: cards[start_index] + cards[start_index + 2]
                print(f"     → Split hand 1: {cards[start_index]} + {cards[start_index + 2]}")
                if self.is_double_opportunity(self.get_card_value(cards[start_index]), self.get_card_value(cards[start_index + 2])):
                    print(f"        → Double: {cards[start_index]} + {cards[start_index + 2]} = {self.get_card_value(cards[start_index]) + self.get_card_value(cards[start_index + 2])}")
                
                # Check for pair in first split hand (another split)
                if cards[start_index + 2] == cards[start_index]:
                    print(f"        → Split: {cards[start_index + 2]} = {cards[start_index]}")
                    # Process the sub-split
                    self._display_sub_split(cards, start_index, start_index + 2, start_index + 3, depth + 1)
            
            if start_index + 3 < len(cards):
                # Second split hand: cards[start_index + 1] + cards[start_index + 3]
                print(f"     → Split hand 2: {cards[start_index + 1]} + {cards[start_index + 3]}")
                if self.is_double_opportunity(self.get_card_value(cards[start_index + 1]), self.get_card_value(cards[start_index + 3])):
                    print(f"        → Double: {cards[start_index + 1]} + {cards[start_index + 3]} = {self.get_card_value(cards[start_index + 1]) + self.get_card_value(cards[start_index + 3])}")
                
                # Check for pair in second split hand (another split)
                if cards[start_index + 3] == cards[start_index + 1]:
                    print(f"        → Split: {cards[start_index + 3]} = {cards[start_index + 1]}")
                    # Process the sub-split
                    self._display_sub_split(cards, start_index + 1, start_index + 3, start_index + 4, depth + 1)
        else:
            # Check for double opportunity
            if self.is_double_opportunity(self.get_card_value(cards[start_index]), self.get_card_value(cards[start_index + 1])):
                if depth == 0:
                    print(f"  🎯 Immediate double: {cards[start_index]} + {cards[start_index + 1]} = {self.get_card_value(cards[start_index]) + self.get_card_value(cards[start_index + 1])}")
                    print(f"     → Payout = 4 (1 token)")
                else:
                    print(f"{indent}→ Double: {cards[start_index]} + {cards[start_index + 1]} = {self.get_card_value(cards[start_index]) + self.get_card_value(cards[start_index + 1])}")
            else:
                if depth == 0:
                    print(f"  ❌ No opportunities: {cards[start_index]} + {cards[start_index + 1]} = {self.get_card_value(cards[start_index]) + self.get_card_value(cards[start_index + 1])}")
                    print(f"     → Payout = 0")
    
    def _display_sub_split(self, cards: List[str], first_card_index: int, second_card_index: int, next_card_index: int, depth: int) -> None:
        """
        Display a sub-split (when a split hand gets another pair)
        
        Args:
            cards: List of cards
            first_card_index: Index of first card in the split hand
            second_card_index: Index of second card in the split hand (the pair)
            next_card_index: Index of next card to process
            depth: Current depth for indentation
        """
        if next_card_index >= len(cards):
            return
        
        indent = "  " + "  " * depth
        
        # First sub-split hand: first_card + next_card
        print(f"{indent}→ Sub-split hand 1: {cards[first_card_index]} + {cards[next_card_index]}")
        if self.is_double_opportunity(self.get_card_value(cards[first_card_index]), self.get_card_value(cards[next_card_index])):
            print(f"{indent}   → Double: {cards[first_card_index]} + {cards[next_card_index]} = {self.get_card_value(cards[first_card_index]) + self.get_card_value(cards[next_card_index])}")
        
        # Check for pair in first sub-split hand
        if cards[next_card_index] == cards[first_card_index]:
            print(f"{indent}   → Split: {cards[next_card_index]} = {cards[first_card_index]}")
            # Process another sub-split
            self._display_sub_split(cards, first_card_index, next_card_index, next_card_index + 1, depth + 1)
        
        # Second sub-split hand: second_card + next_card + 1
        if next_card_index + 1 < len(cards):
            print(f"{indent}→ Sub-split hand 2: {cards[second_card_index]} + {cards[next_card_index + 1]}")
            if self.is_double_opportunity(self.get_card_value(cards[second_card_index]), self.get_card_value(cards[next_card_index + 1])):
                print(f"{indent}   → Double: {cards[second_card_index]} + {cards[next_card_index + 1]} = {self.get_card_value(cards[second_card_index]) + self.get_card_value(cards[next_card_index + 1])}")
            
            # Check for pair in second sub-split hand
            if cards[next_card_index + 1] == cards[second_card_index]:
                print(f"{indent}   → Split: {cards[next_card_index + 1]} = {cards[second_card_index]}")
                # Process another sub-split
                self._display_sub_split(cards, second_card_index, next_card_index + 1, next_card_index + 2, depth + 1)
    
    def run_betting_simulation(self, num_hands: int, flat: bool = False):
        """
        Run a betting simulation.

        flat=False (default): progressive — start at 1 unit, increase by 1 after each win,
                              reset to 1 on a loss. Each run ends on a loss.
        flat=True:            flat — always bet 1 unit per hand, no reset concept.
        """
        import random

        # Exact probabilities derived from the 5-card enumeration (371,293 hands)
        probabilities = {
            0:  307580 / 371293,
            4:   55250 / 371293,
            13:   6576 / 371293,
            31:   1710 / 371293,
            51:    177 / 371293,
        }

        # Build a sorted lookup for the RNG
        outcomes = sorted(probabilities.keys())
        cumulative = []
        running = 0.0
        for p in outcomes:
            running += probabilities[p]
            cumulative.append(running)

        def sample_outcome():
            r = random.random()
            for i, threshold in enumerate(cumulative):
                if r <= threshold:
                    return outcomes[i]
            return outcomes[-1]

        total_wagered = 0
        total_returned = 0
        max_wins_in_row = 0

        if flat:
            print(f"Running flat-bet simulation ({num_hands:,} hands)...")
            net_per_hand = []
            for i in range(num_hands):
                payout = sample_outcome()
                total_wagered += 1
                total_returned += payout
                net_per_hand.append(payout - 1)
                if (i + 1) % 500000 == 0:
                    print(f"  {i+1:,} hands...")

            net = total_returned - total_wagered
            rtp = (total_returned / total_wagered) * 100

            print(f"\n=== FLAT BET RESULTS ({num_hands:,} hands) ===")
            print(f"Total wagered:  {total_wagered:,} units")
            print(f"Total returned: {total_returned:,} units")
            print(f"Net:            {net:+,} units")
            print(f"RTP:            {rtp:.4f}%")
            print(f"House edge:     {100 - rtp:.4f}%")

        else:
            print(f"Running progressive simulation ({num_hands:,} hands total across runs)...")
            run_results = []
            hands_played = 0

            while hands_played < num_hands:
                current_bet = 1
                run_net = 0
                wins = 0

                while True:
                    payout = sample_outcome()
                    total_wagered += current_bet
                    hands_played += 1

                    if payout > 0:
                        net_this_hand = (current_bet * payout) - current_bet
                        run_net += net_this_hand
                        total_returned += current_bet * payout
                        wins += 1
                        current_bet += 1
                    else:
                        run_net -= current_bet
                        total_returned += 0
                        break

                    if hands_played >= num_hands:
                        break

                run_results.append({'wins': wins, 'net': run_net})
                max_wins_in_row = max(max_wins_in_row, wins)

            net = total_returned - total_wagered
            rtp = (total_returned / total_wagered) * 100
            winning_runs = sum(1 for r in run_results if r['net'] > 0)
            losing_runs  = sum(1 for r in run_results if r['net'] < 0)
            avg_wins = sum(r['wins'] for r in run_results) / len(run_results)
            avg_net  = sum(r['net']  for r in run_results) / len(run_results)

            print(f"\n=== PROGRESSIVE BET RESULTS ({hands_played:,} hands, {len(run_results):,} runs) ===")
            print(f"Total wagered:     {total_wagered:,} units")
            print(f"Total returned:    {total_returned:,} units")
            print(f"Net:               {net:+,} units")
            print(f"RTP:               {rtp:.4f}%")
            print(f"House edge:        {100 - rtp:.4f}%")
            print(f"Winning runs:      {winning_runs:,} ({winning_runs/len(run_results)*100:.2f}%)")
            print(f"Losing runs:       {losing_runs:,}  ({losing_runs/len(run_results)*100:.2f}%)")
            print(f"Avg wins/run:      {avg_wins:.3f}")
            print(f"Avg net/run:       {avg_net:+.4f} units")
            print(f"Max wins in a row: {max_wins_in_row}")

    def generate_all_combinations(self, num_cards: int = 5) -> List[Tuple[List[str], int]]:
        """
        Generate all possible card combinations and calculate payouts
        
        Args:
            num_cards: Number of cards (5 or 6)
            
        Returns:
            List of tuples (cards, payout) for all possible combinations
        """
        if num_cards not in [5, 6]:
            raise ValueError("num_cards must be 5 or 6")
        
        results = []
        total_combinations = 13 ** num_cards
        print(f"Generating all {total_combinations:,} possible {num_cards}-card combinations...")
        
        for i in range(total_combinations):
            # Convert index to base-13 representation to get card combination
            hand = []
            temp = i
            for _ in range(num_cards):
                hand.append(self.cards[temp % 13])
                temp //= 13
            
            payout = self.calculate_payout(hand)
            results.append((hand, payout))
            
            # Progress indicator
            if (i + 1) % 50000 == 0:
                print(f"  Processed {i + 1:,} combinations...")
        
        print(f"Completed all {total_combinations:,} combinations!")
        return results
    
    def check_specific_hand(self, cards: List[str]) -> int:
        """
        Check a specific 5 or 6-card hand and return payout
        
        Args:
            cards: List of 5 or 6 cards as strings
            
        Returns:
            Payout amount
        """
        if len(cards) < 2 or len(cards) > 10:
            raise ValueError("Must provide between 2 and 10 cards")
        
        # Validate cards
        for card in cards:
            if card not in self.cards:
                raise ValueError(f"Invalid card: {card}. Valid cards are: {', '.join(self.cards)}")
        
        payout = self.calculate_payout(cards)
        return payout
    
    def save_results_to_csv(self, results: List[Tuple[List[str], int]], filename: str):
        """
        Save simulation results to CSV file
        
        Args:
            results: List of (cards, payout) tuples
            filename: Output CSV filename
        """
        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            
            # Determine number of cards from first result
            num_cards = len(results[0][0]) if results else 5
            
            # Write header based on number of cards
            if num_cards == 5:
                writer.writerow(['Card1', 'Card2', 'Card3', 'Card4', 'Card5', 'Payout', 'Payout_4', 'Payout_13', 'Payout_31', 'Payout_51', 'Increase'])
            else:  # 6 cards
                writer.writerow(['Card1', 'Card2', 'Card3', 'Card4', 'Card5', 'Card6', 'Payout', 'Payout_4', 'Payout_13', 'Payout_31', 'Payout_51', 'Increase'])
            
            # Write data
            for cards, payout in results:
                # Calculate indicator columns
                payout_4 = 1 if payout == 4 else 0
                payout_13 = 1 if payout == 13 else 0
                payout_31 = 1 if payout == 31 else 0
                payout_51 = 1 if payout == 51 else 0
                increase = 1 if payout > 0 else 0
                
                writer.writerow(cards + [payout, payout_4, payout_13, payout_31, payout_51, increase])
    
    def analyze_results(self, results: List[Tuple[List[str], int]]):
        """
        Analyze simulation results and print statistics
        
        Args:
            results: List of (cards, payout) tuples
        """
        total_hands = len(results)
        total_payout = sum(payout for _, payout in results)
        
        # Count different payout amounts
        payout_counts = {}
        for _, payout in results:
            payout_counts[payout] = payout_counts.get(payout, 0) + 1
        
        print(f"\n=== SIMULATION ANALYSIS ===")
        print(f"Total hands: {total_hands}")
        print(f"Total payout: {total_payout}")
        print(f"Average payout per hand: {total_payout / total_hands:.2f}")
        print(f"\nPayout distribution:")
        
        for payout in sorted(payout_counts.keys()):
            count = payout_counts[payout]
            percentage = (count / total_hands) * 100
            print(f"  Payout {payout}: {count} hands ({percentage:.1f}%)")
        
        # Calculate expected value
        expected_value = total_payout / total_hands
        print(f"\nExpected value: {expected_value:.2f}")

class FreeBetGame:
    """
    Full Free Bet Blackjack simulator — main hand + Pot of Gold side bet.

    Rules:
      - 6-deck shoe, reshuffle at 75% penetration
      - Dealer stands on soft 17
      - Push 22: dealer bust with 22 = push on all live player hands
      - Free split: always split non-10-value pairs (re-splitting allowed)
      - Free double: always double 2-card hard 9/10/11 (after splits too)
      - Lammer model: player only ever risks original main bet;
                      each split/double win pays in full but a lammer loss = $0
      - POG loses to dealer blackjack; otherwise pays by token count
    """

    CARD_VALUES = {
        'A': 11, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6,
        '7':  7, '8': 8, '9': 9, 'T': 10, 'J': 10, 'Q': 10, 'K': 10,
    }

    def __init__(self, num_decks: int = 6):
        self.num_decks = num_decks
        self._reshuffle()

    # ── shoe ────────────────────────────────────────────────────────────────

    def _reshuffle(self):
        ranks = ['A','2','3','4','5','6','7','8','9','T','J','Q','K']
        self._shoe = ranks * 4 * self.num_decks
        random.shuffle(self._shoe)
        self._pos  = 0
        self._cut  = int(len(self._shoe) * 0.75)

    def _deal(self) -> str:
        if self._pos >= self._cut:
            self._reshuffle()
        c = self._shoe[self._pos]; self._pos += 1
        return c

    # ── hand helpers ────────────────────────────────────────────────────────

    def _val(self, hand: list) -> int:
        total = sum(self.CARD_VALUES[c] for c in hand)
        aces  = hand.count('A')
        while total > 21 and aces:
            total -= 10; aces -= 1
        return total

    def _soft(self, hand: list) -> bool:
        return 'A' in hand and sum(self.CARD_VALUES[c] for c in hand) <= 21

    def _bj(self, hand: list) -> bool:
        return len(hand) == 2 and self._val(hand) == 21

    def _10val(self, card: str) -> bool:
        return card in ('T', 'J', 'Q', 'K')

    # ── basic strategy ──────────────────────────────────────────────────────

    def _action(self, hand: list, up: str) -> str:
        """Return H / S / P (free split) / D (free double)."""
        # Free split takes priority — pair, not 10-value
        if len(hand) == 2 and hand[0] == hand[1] and not self._10val(hand[0]):
            return 'P'
        v = self._val(hand)
        # Free double — 2-card hard 9/10/11 only
        if len(hand) == 2 and not self._soft(hand) and v in (9, 10, 11):
            return 'D'
        # Standard basic strategy (no surrender in FBJ)
        dv = self.CARD_VALUES[up]
        if self._soft(hand):
            if v >= 19:  return 'S'
            if v == 18:  return 'S' if dv <= 8 else 'H'
            return 'H'
        else:
            if v >= 17:  return 'S'
            if v >= 13:  return 'S' if dv <= 6 else 'H'
            if v == 12:  return 'S' if 4 <= dv <= 6 else 'H'
            return 'H'

    # ── hand play ───────────────────────────────────────────────────────────

    def _play_player(self, init: list, up: str, mb: float):
        """
        Play all hands depth-first (left before right after splits).
        Returns (hands, tokens).

        Each hand dict has:
          win  — amount won if hand beats dealer
          lose — amount lost if hand loses (0 for lammer hands)

        Lammer model:
          Original hand:  win=mb,  lose=mb
          Right split:    win=mb,  lose=0   (lammer — can win, can't lose extra)
          Free double:    win*=2,  lose unchanged
        """
        tokens = 0
        queue  = [[init[:], mb, mb]]  # [cards, win_bet, lose_bet]
        done   = []

        while queue:
            cards, wb, lb = queue.pop(0)
            while True:
                v = self._val(cards)
                if v > 21:
                    done.append({'cards': cards, 'win': wb, 'lose': lb}); break
                act = self._action(cards, up)
                if act == 'P':
                    tokens += 1
                    c1, c2 = cards[0], cards[1]
                    n1, n2 = self._deal(), self._deal()
                    # left child inherits parent bet; right child is a lammer
                    queue.insert(0, [[c2, n2], mb, 0 ])  # right — inserted first…
                    queue.insert(0, [[c1, n1], wb, lb])  # left  — …so left is next
                    break
                elif act == 'D':
                    tokens += 1
                    cards.append(self._deal())
                    done.append({'cards': cards, 'win': wb * 2, 'lose': lb}); break
                elif act == 'H':
                    cards.append(self._deal())
                elif act == 'S':
                    done.append({'cards': cards, 'win': wb, 'lose': lb}); break

        return done, tokens

    def _play_dealer(self, hand: list) -> int:
        while self._val(hand) < 17:
            hand.append(self._deal())
        return self._val(hand)

    # ── payout ──────────────────────────────────────────────────────────────

    def _pog_payout(self, tokens: int) -> int:
        """Total return per unit (stake included). 0 = lose bet."""
        if tokens == 0: return 0
        if tokens == 1: return 4
        if tokens == 2: return 13
        if tokens == 3: return 31
        if tokens == 4: return 51
        return 101

    # ── single hand ─────────────────────────────────────────────────────────

    def play_hand(self, main_bet: float, pog_bet: float = 1.0):
        """Returns (main_net, pog_net)."""
        player = [self._deal(), self._deal()]
        dealer = [self._deal(), self._deal()]
        up = dealer[0]

        dbj = self._bj(dealer)
        pbj = self._bj(player)

        if dbj:
            # POG always loses to dealer BJ; main pushes only on mutual BJ
            return (0.0 if pbj else -main_bet), -pog_bet

        if pbj:
            # Player BJ: 3:2, exempt from push-22; no POG tokens (face card)
            return main_bet * 1.5, -pog_bet

        hands, tokens = self._play_player(player, up, main_bet)
        dv      = self._play_dealer(dealer)
        push22  = (dv == 22)
        dbust   = (dv  > 21)

        main_net = 0.0
        for h in hands:
            pv = self._val(h['cards'])
            if pv > 21:
                main_net -= h['lose']           # player bust (already settled)
            elif push22:
                pass                            # dealer bust-22 = push
            elif dbust or pv > dv:
                main_net += h['win']            # player wins
            elif pv < dv:
                main_net -= h['lose']           # player loses

        pay = self._pog_payout(tokens)
        pog_net = (pay - 1) * pog_bet if pay > 0 else -pog_bet

        return main_net, pog_net

    # ── simulation ──────────────────────────────────────────────────────────

    def simulate(self, num_hands: int, scenario: str = 'flat5') -> dict:
        """
        Run num_hands hands and return result dict.

        scenario  main bet           POG bet
        flat5     5 units (fixed)    1 unit
        flat1     1 unit  (fixed)    1 unit
        progressive  starts 1, +1 after main-hand win, resets to 1 on loss/push  1 unit
        """
        pog_bet  = 1.0
        main_bet = 5.0 if scenario == 'flat5' else 1.0
        max_bet  = main_bet

        mw = mret = pw = pret = 0.0

        for i in range(num_hands):
            mn, pn = self.play_hand(main_bet, pog_bet)

            mw   += main_bet;  mret += main_bet + mn
            pw   += pog_bet;   pret += pog_bet  + pn

            if scenario == 'progressive':
                if mn > 0:
                    main_bet += 1
                    if main_bet > max_bet: max_bet = main_bet
                else:
                    main_bet = 1.0

            if (i + 1) % 250_000 == 0:
                print(f"    {i+1:,} hands...")

        cw  = mw   + pw
        cret = mret + pret
        return {
            'scenario':         scenario,
            'hands':            num_hands,
            'bet_range':        f"{'5' if scenario=='flat5' else '1'}{'–'+str(int(max_bet)) if scenario=='progressive' else ''}",
            'main_wagered':     mw,
            'main_net':         mret - mw,
            'main_rtp':         mret / mw * 100,
            'pog_wagered':      pw,
            'pog_net':          pret - pw,
            'pog_rtp':          pret / pw * 100,
            'combined_wagered': cw,
            'combined_net':     cret - cw,
            'combined_rtp':     cret / cw * 100,
        }


def main():
    """Main function with command line argument handling"""
    parser = argparse.ArgumentParser(description='Free Bet Blackjack 5-Card Analysis')
    parser.add_argument('--hand', nargs='+', metavar='CARD',
                       help='Check a specific 5 or 6-card hand (e.g., --hand A 2 3 4 5 or --hand A 2 3 4 5 6)')
    parser.add_argument('--all', action='store_true',
                       help='Generate all possible 5-card combinations and save to CSV')
    parser.add_argument('--all6', action='store_true',
                       help='Generate all possible 6-card combinations and save to CSV')
    parser.add_argument('--simulation', type=int, metavar='HANDS',
                       help='Run betting simulation for specified number of hands')
    parser.add_argument('--flat', action='store_true',
                       help='Use flat 1-unit bet per hand (default: progressive +1 on wins)')
    parser.add_argument('--game', type=int, metavar='HANDS',
                       help='Full game simulation (main hand + POG) for all 3 scenarios')
    
    args = parser.parse_args()
    
    simulator = FreeBetSimulator()
    
    if args.hand:
        # Check specific hand
        try:
            cards = [card.upper() for card in args.hand]
            if len(cards) < 2 or len(cards) > 10:
                print(f"Error: Must provide between 2 and 10 cards, got {len(cards)}")
                return 1
            payout = simulator.check_specific_hand(cards)
            
            print("Free Bet Blackjack 5-Card Hand Checker")
            print("=====================================")
            print(f"Hand: {' '.join(cards)}")
            print(f"Payout: {payout}")
            
            # Show readable analysis
            print(f"\nHand Analysis:")
            
            if simulator.is_face_card(cards[0]) or simulator.is_face_card(cards[1]):
                print(f"  ❌ Auto fail: First two cards contain a face card")
                print(f"     {cards[0]} + {cards[1]} → Payout = 0")
            else:
                # Use recursive display
                simulator._display_analysis_recursive(cards, 0, 0)
                
        except ValueError as e:
            print(f"Error: {e}")
            return 1
    
    elif args.all:
        # Generate all 5-card combinations
        print("Free Bet Blackjack 5-Card Complete Analysis")
        print("===========================================")
        print("Generating ALL possible 5-card combinations...")
        print("Total combinations: 371,293")
        print()
        
        # Generate all combinations
        results = simulator.generate_all_combinations(5)
        
        # Analyze results
        simulator.analyze_results(results)
        
        # Save to CSV
        filename = "freebet_analysis_5card.csv"
        simulator.save_results_to_csv(results, filename)
        print(f"\n5-card analysis complete! Results saved to: {filename}")
        
        # Show some example hands
        print(f"\nExample combinations:")
        for i, (cards, payout) in enumerate(results[:10]):
            print(f"  Combination {i+1}: {' '.join(cards)} → Payout: {payout}")
    
    elif args.all6:
        # Generate all 6-card combinations
        print("Free Bet Blackjack 6-Card Complete Analysis")
        print("===========================================")
        print("Generating ALL possible 6-card combinations...")
        print("Total combinations: 4,826,809")
        print()
        
        # Generate all combinations
        results = simulator.generate_all_combinations(6)
        
        # Analyze results
        simulator.analyze_results(results)
        
        # Skip CSV output to save space
        print(f"\n6-card analysis complete! (CSV output skipped to save space)")
        
        # Show some example hands
        print(f"\nExample combinations:")
        for i, (cards, payout) in enumerate(results[:10]):
            print(f"  Combination {i+1}: {' '.join(cards)} → Payout: {payout}")
        
        # Show some high-payout examples
        high_payouts = [(cards, payout) for cards, payout in results if payout > 0]
        if high_payouts:
            print(f"\nHigh-payout examples:")
            for i, (cards, payout) in enumerate(high_payouts[:5]):
                print(f"  {' '.join(cards)} → Payout: {payout}")
    
    elif args.game:
        print("Free Bet Blackjack — Full Game Simulation (Main Hand + Pot of Gold)")
        print("=====================================================================")
        scenarios = [
            ('flat5',       'Main=5u flat,        POG=1u'),
            ('flat1',       'Main=1u flat,        POG=1u'),
            ('progressive', 'Main progressive +1, POG=1u'),
        ]
        game = FreeBetGame()
        for sc, label in scenarios:
            print(f"\n[{label}]")
            r = game.simulate(args.game, sc)
            print(f"  Main hand:   wagered={r['main_wagered']:>12,.0f}u  net={r['main_net']:>+10,.1f}u  RTP={r['main_rtp']:.4f}%")
            print(f"  Pot of Gold: wagered={r['pog_wagered']:>12,.0f}u  net={r['pog_net']:>+10,.1f}u  RTP={r['pog_rtp']:.4f}%")
            print(f"  COMBINED:    wagered={r['combined_wagered']:>12,.0f}u  net={r['combined_net']:>+10,.1f}u  RTP={r['combined_rtp']:.4f}%")

    elif args.simulation:
        # Run betting simulation
        print("Free Bet Blackjack Betting Simulation")
        print("====================================")
        print(f"Running simulation for {args.simulation:,} hands...")
        print("Strategy: Increase bet by 1 unit after every winning hand")
        print()
        
        simulator.run_betting_simulation(args.simulation, flat=args.flat)
    
    else:
        # No arguments provided, show help
        parser.print_help()
        print("\nExamples:")
        print("  python3 freebet.py --hand A A A A A")
        print("  python3 freebet.py --hand 2 3 4 5 6")
        print("  python3 freebet.py --hand T J Q K A")
        print("  python3 freebet.py --all")
        print("  python3 freebet.py --simulation 10000")
    
    return 0

if __name__ == "__main__":
    exit(main())
