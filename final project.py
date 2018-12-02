from dominiate import cards, dominion, game, players, combobot, derivbot
from keras import models, layers, regularizers, preprocessing

canonical_order = [game.curse, game.estate, game.duchy, game.province, game.copper, game.silver, game.gold,
                   cards.village, cards.cellar, cards.smithy, cards.festival, cards.market, cards.laboratory,
                   cards.chapel, cards.warehouse, cards.council_room, cards.militia, cards.moat]


def c2f (cards):
    currarr = [0 for _ in len(canonical_order)]
    for c in cards:
        currarr[canonical_order.index(c)] += 1
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
        pass
    def from_state_features_trash (self, decision):
        game = decision.game
        pass
    def from_state_features_play (self, decision):
        state = decision.game.state
        hand = state.hand
        return c2f(hand)
        pass
    def from_state_features_discard (self, decision):
        game = decision.game
        pass
    def terminal_val (self, decision):
        if game.Game.over(decision.game):
            player = decision.player()
            return game.PlayerState.score(player) * 4
        return game.PlayerState.score(player)

    pass