from game import TrashDecision, DiscardDecision
from players import AIPlayer, BigMoney
import cards as c
import random
import logging, sys

class SmithyBot(BigMoney):
    def __init__(self, cutoff1=3, cutoff2=6, cards_per_smithy=8):
        self.cards_per_smithy = 8
        self.name = 'SmithyBot(%d, %d, %d)' % (cutoff1, cutoff2,
        cards_per_smithy)
        BigMoney.__init__(self, cutoff1, cutoff2)
    
    def num_smithies(self, state):
        return list(state.all_cards()).count(c.smithy)

    def buy_priority_order(self, decision):
        state = decision.state()
        provinces_left = decision.game.card_counts[c.province]
        if provinces_left <= self.cutoff1:
            order = [None, c.estate, c.silver, c.duchy, c.province]
        elif provinces_left <= self.cutoff2:
            order = [None, c.silver, c.smithy, c.duchy, c.gold, c.province]
        else:
            order = [None, c.silver, c.smithy, c.gold, c.province]
        if ((self.num_smithies(state) + 1) * self.cards_per_smithy
           > state.deck_size()) and (c.smithy in order):
            order.remove(c.smithy)
        return order

    def make_act_decision(self, decision):
        return c.smithy

class HillClimbBot(BigMoney):
    def __init__(self, cutoff1=2, cutoff2=3, simulation_steps=100):
        self.simulation_steps = simulation_steps
        if not hasattr(self, 'name'):
            self.name = 'HillClimbBot(%d, %d, %d)' % (cutoff1, cutoff2,
            simulation_steps)
        BigMoney.__init__(self, cutoff1, cutoff2)

    def buy_priority(self, decision, card):
        state = decision.state()
        total = 0
        if card is None: add = ()
        else: add = (card,)
        for coins, buys in state.simulate_hands(self.simulation_steps, add):
            total += buying_value(coins, buys)

        # gold is better than it seems
        if card == c.gold: total += self.simulation_steps/2
        self.log.debug("%s: %s" % (card, total))
        return total
    
    def make_buy_decision(self, decision):
        choices = decision.choices()
        provinces_left = decision.game.card_counts[c.province]
        
        if c.province in choices: return c.province
        if c.duchy in choices and provinces_left <= self.cutoff2:
            return c.duchy
        if c.estate in choices and provinces_left <= self.cutoff1:
            return c.estate
        return BigMoney.make_buy_decision(self, decision)

class RandomBot(AIPlayer):
    """
    This AI randomly selects an option from among those available
    """
    def __init__(self):
        if not hasattr(self, 'name'):
            self.name = 'RandomBot'
        AIPlayer.__init__(self)

    def make_buy_decision(self, decision):
        return random.choice(decision.choices())
    def make_act_decision(self, decision):
        return random.choice(decision.choices())
    def make_trash_decision(self, decision):
        latest = False
        chosen = []
        choices = decision.choices()
        while choices and latest is not None and len(chosen) < decision.max:
            latest = random.choice(choices)
            if latest is not None:
                choices.remove(latest)
                chosen.append(latest)
        return chosen
    def make_discard_decision(self, decision):
        latest = False
        chosen = []
        choices = decision.choices()
        while choices and latest is not None and len(chosen) < decision.max:
            latest = random.choice(choices)
            if latest is not None:
                choices.remove(latest)
                chosen.append(latest)
        return chosen

class GreedyBot(AIPlayer):
    """
    This AI chooses the card with highest value to buy and lowest cost to discard/trash
    """
    def __init__(self):
        if not hasattr(self, 'name'):
            self.name = 'GreedyBot'
        AIPlayer.__init__(self)

    def order_cards(self, choices):
        """
        Provide a buy_priority by ordering the cards from least to most
        important.
        """
        if None in choices:
            choices.remove(None)
        return sorted(choices, key=lambda choice: choice.cost)

    def make_buy_decision(self, decision):
        print decision.choices()
        return self.order_cards(decision.choices())[-1]
    def make_act_decision(self, decision):
        return self.order_cards(decision.choices())[-1]
    def make_trash_decision(self, decision):
        chosen = []
        choices = self.order_cards(decision.choices())
        return choices[0:decision.min]
    def make_discard_decision(self, decision):
        chosen = []
        choices = self.order_cards(decision.choices())
        return choices[0:decision.min]

def buying_value(coins, buys):
    if coins > buys*8: coins = buys*8
    if (coins - (buys-1)*8) in (1, 7):  # there exists a useless coin
        coins -= 1
    return coins

