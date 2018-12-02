from dominiate import cards, dominion, game, players, combobot, derivbot
from keras import models, layers, regularizers, preprocessing

canonical_order = [game.curse, game.estate, game.duchy, game.province, game.copper, game.silver, game.gold,
                   cards.village, cards.cellar, cards.smithy, cards.festival, cards.market, cards.laboratory,
                   cards.chapel, cards.warehouse, cards.council_room, cards.militia, cards.moat]


def c2f (cards):
    currarr = [0 for _ in canonical_order]
    for c in cards:
        currarr[canonical_order.index(c)] += 1
    return currarr

def g2f (carddict):
    currarr = [0 for _ in canonical_order]
    for (c, count) in carddict.items():
        currarr[canonical_order.index(c)] =count
    return currarr



class combo_learner(combobot.ComboBot):
    def __init__(self):
        self.buy_weights = []
        self.trash_weights = []
        self.discard_weights = []
        self.play_weights = []

    """
    4 separate q learners
    """
    def from_state_features_buy (self, decision):
        game = decision.game
        deck = decision.state().all_cards()
        a = g2f(game.counts)
        a.extend(c2f(deck))
        return a
        pass
    def from_state_features_trash (self, decision):
        game = decision.game
        state = decision.state()
        deck = decision.state().all_cards()
        a = g2f(game.counts)
        a.extend(c2f(deck))
        a.extend(c2f(state.hand))
        return a
        pass
    def from_state_features_play (self, decision):
        state = decision.game.state()
        hand = state.hand
        a = c2f(hand)
        a.extend([state.actions, state.buys, state.hand_value()])
        return a
        pass
    def from_state_features_discard (self, decision):
        game = decision.game
        state = decision.game.state()
        hand = state.hand
        return c2f(hand).extend([state.actions, state.buys, state.hand_value()])
        pass
    def terminal_val (self, decision):
        player = decision.player()
        if game.Game.over(decision.game):

            return game.PlayerState.score(player) * 4
        return game.PlayerState.score(player)

    pass