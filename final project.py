from dominiate import cards, dominion, game, players, combobot, derivbot
from keras import models, layers, regularizers, preprocessing

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
        game = decision.game
        pass
    def from_state_features_discard (self, decision):
        game = decision.game
        pass
    def terminal_val (self, decision):
        if game.Game.over(decision.game):
            player = decision.player()
            return game.PlayerState.score(player)
        return 0

    pass