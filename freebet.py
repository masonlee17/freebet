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
        
        # Cap at 5 cards (4 splits)
        if len(cards) > 5:
            cards = cards[:5]
        
        # Use recursive approach to calculate tokens
        tokens = self._calculate_tokens_recursive(cards, 0)
        
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
    
    def _calculate_tokens_recursive(self, cards: List[str], start_index: int) -> int:
        """
        Calculate tokens for free bet blackjack with 4-split cap
        
        Args:
            cards: List of cards
            start_index: Starting index for this hand
            
        Returns:
            Number of tokens
        """
        # Cap at 4 splits (5 cards total) - only process first 5 cards
        if start_index >= 4 or start_index >= len(cards) - 1:
            return 0
        
        tokens = 0
        
        # Check if we have a pair (split) - ALWAYS split pairs, never check for double first
        if cards[start_index] == cards[start_index + 1]:
            tokens += 1  # Split token
            
            # Process the split hands - each gets one card
            if start_index + 2 < len(cards) and start_index + 2 < 5:  # Cap at 5 cards
                # First split hand: cards[start_index] + cards[start_index + 2]
                if self.is_double_opportunity(self.get_card_value(cards[start_index]), self.get_card_value(cards[start_index + 2])):
                    tokens += 1  # Double token
                
                # Check for pair in first split hand (another split)
                if cards[start_index + 2] == cards[start_index]:
                    tokens += 1  # Split token
                    # Process the sub-split - only process remaining cards
                    tokens += self._process_sub_split(cards, start_index, start_index + 2, start_index + 3)
            
            if start_index + 3 < len(cards) and start_index + 3 < 5:  # Cap at 5 cards
                # Second split hand: cards[start_index + 1] + cards[start_index + 3]
                if self.is_double_opportunity(self.get_card_value(cards[start_index + 1]), self.get_card_value(cards[start_index + 3])):
                    tokens += 1  # Double token
                
                # Check for pair in second split hand (another split)
                if cards[start_index + 3] == cards[start_index + 1]:
                    tokens += 1  # Split token
                    # Process the sub-split - only process remaining cards
                    tokens += self._process_sub_split(cards, start_index + 1, start_index + 3, start_index + 4)
        else:
            # Only check for double opportunity if NOT a pair
            if self.is_double_opportunity(self.get_card_value(cards[start_index]), self.get_card_value(cards[start_index + 1])):
                tokens += 1  # Double token
        
        return tokens
    
    def _process_sub_split(self, cards: List[str], first_card_index: int, second_card_index: int, next_card_index: int) -> int:
        """
        Process a sub-split (when a split hand gets another pair)
        
        Args:
            cards: List of cards
            first_card_index: Index of first card in the split hand
            second_card_index: Index of second card in the split hand (the pair)
            next_card_index: Index of next card to process
            
        Returns:
            Number of tokens
        """
        if next_card_index >= len(cards):
            return 0
        
        # Cap at 4 splits (5 cards total)
        if next_card_index >= 5:
            return 0
        
        tokens = 0
        
        # First sub-split hand: first_card + next_card
        if self.is_double_opportunity(self.get_card_value(cards[first_card_index]), self.get_card_value(cards[next_card_index])):
            tokens += 1  # Double token
        
        # Check for pair in first sub-split hand
        if cards[next_card_index] == cards[first_card_index]:
            tokens += 1  # Split token
            # Process another sub-split
            tokens += self._process_sub_split(cards, first_card_index, next_card_index, next_card_index + 1)
        
        # Second sub-split hand: second_card + next_card + 1
        if next_card_index + 1 < len(cards):
            if self.is_double_opportunity(self.get_card_value(cards[second_card_index]), self.get_card_value(cards[next_card_index + 1])):
                tokens += 1  # Double token
            
            # Check for pair in second sub-split hand
            if cards[next_card_index + 1] == cards[second_card_index]:
                tokens += 1  # Split token
                # Process another sub-split
                tokens += self._process_sub_split(cards, second_card_index, next_card_index + 1, next_card_index + 2)
        
        return tokens
    
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
    
    def run_betting_simulation(self, num_runs: int):
        """
        Run a betting simulation with progressive betting strategy
        
        Each run continues until you lose, increasing bet after each win.
        
        Args:
            num_runs: Number of runs to simulate
        """
        import random
        
        # Approximate probabilities from your data
        probabilities = {
            0: 0.8284023669,  # 82.84% - no payout
            4: 0.1488043136,  # 14.88% - 1 token
            13: 0.01967718217,  # 1.97% - 2 tokens
            31: 0.002197725247,  # 0.22% - 3 tokens
            51: 0.0009184121435,  # 0.09% - 4 tokens
            101: 0.0001  # 0.09% - 5+ tokens (using same as 4 tokens for simplicity)
        }
        
        # Normalize probabilities
        total_prob = sum(probabilities.values())
        for payout in probabilities:
            probabilities[payout] /= total_prob
        
        # Simulation variables
        run_results = []
        total_bet = 0
        total_winnings = 0
        max_bet_reached = 0
        max_wins_in_row = 0
        
        print("Running simulation...")
        
        for run in range(num_runs):
            current_bet = 1
            run_winnings = 0
            wins_in_row = 0
            
            # Continue until we lose
            while True:
                # Place bet
                total_bet += current_bet
                
                # Determine outcome based on probabilities
                rand = random.random()
                cumulative_prob = 0
                payout = 0
                
                for p in sorted(probabilities.keys()):
                    cumulative_prob += probabilities[p]
                    if rand <= cumulative_prob:
                        payout = p
                        break
                
                if payout > 0:
                    # Win - calculate profit (winnings minus bet cost) and increase bet
                    profit = (current_bet * payout) - current_bet  # Net profit
                    run_winnings += profit
                    total_winnings += profit
                    wins_in_row += 1
                    current_bet += 1  # Increase bet by 1 for next hand
                    max_bet_reached = max(max_bet_reached, current_bet)
                else:
                    # Lose - end the run
                    run_winnings -= current_bet  # Subtract the losing bet cost
                    total_winnings -= current_bet
                    break
            
            run_results.append({
                'wins_in_row': wins_in_row,
                'final_bet': current_bet - 1,  # The bet that lost
                'net_result': run_winnings,
                'max_bet': current_bet - 1
            })
            
            max_wins_in_row = max(max_wins_in_row, wins_in_row)
            
            # Show progress every 1000 runs
            if (run + 1) % 1000 == 0:
                avg_result = sum(r['net_result'] for r in run_results) / len(run_results)
                print(f"  Run {run + 1:,}: Avg result={avg_result:+.2f}, Max wins={max_wins_in_row}")
        
        # Calculate final statistics
        net_result = total_winnings
        roi = (net_result / total_bet) * 100 if total_bet > 0 else 0
        
        # Analyze run results
        winning_runs = [r for r in run_results if r['net_result'] > 0]
        losing_runs = [r for r in run_results if r['net_result'] < 0]
        break_even_runs = [r for r in run_results if r['net_result'] == 0]
        
        avg_wins_per_run = sum(r['wins_in_row'] for r in run_results) / len(run_results)
        avg_net_per_run = sum(r['net_result'] for r in run_results) / len(run_results)
        
        print(f"\n=== SIMULATION RESULTS ===")
        print(f"Total runs: {num_runs:,}")
        print(f"Winning runs: {len(winning_runs):,} ({len(winning_runs)/num_runs*100:.2f}%)")
        print(f"Losing runs: {len(losing_runs):,} ({len(losing_runs)/num_runs*100:.2f}%)")
        print(f"Break-even runs: {len(break_even_runs):,} ({len(break_even_runs)/num_runs*100:.2f}%)")
        print(f"Total bet: {total_bet:,}")
        print(f"Total winnings: {total_winnings:,}")
        print(f"Net result: {net_result:+.2f}")
        print(f"ROI: {roi:+.2f}%")
        print(f"Average wins per run: {avg_wins_per_run:.2f}")
        print(f"Average net per run: {avg_net_per_run:+.2f}")
        print(f"Max wins in a row: {max_wins_in_row}")
        print(f"Max bet reached: {max_bet_reached}")
        
        # Show distribution of run results
        print(f"\nRun result distribution:")
        result_ranges = [
            (-float('inf'), -100, "Very bad"),
            (-100, -10, "Bad"),
            (-10, -1, "Small loss"),
            (-1, 0, "Break even"),
            (0, 10, "Small win"),
            (10, 100, "Good"),
            (100, float('inf'), "Very good")
        ]
        
        for min_val, max_val, label in result_ranges:
            count = len([r for r in run_results if min_val < r['net_result'] <= max_val])
            if count > 0:
                print(f"  {label}: {count:,} runs ({count/num_runs*100:.1f}%)")

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
    
    elif args.simulation:
        # Run betting simulation
        print("Free Bet Blackjack Betting Simulation")
        print("====================================")
        print(f"Running simulation for {args.simulation:,} hands...")
        print("Strategy: Increase bet by 1 unit after every winning hand")
        print()
        
        simulator.run_betting_simulation(args.simulation)
    
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
