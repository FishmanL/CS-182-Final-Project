import cards
import dominion
import game
import players
import combobot
import derivbot
from game import *
from players import *
from basic_ai import *
from combobot import *
from cards import variable_cards
from collections import defaultdict
import random
from keras import models, layers, regularizers, preprocessing
import csv
from final_project import *

# Options for Players:
# ComboLearner()            our q learner
# smithyComboBot()          from source code, basic ai
# chapelComboBot()          from source code, basic ai
# HillClimbBot(2, 3, 40)    from source code, basic ai
# ... any more that we create

def testing(player1, player2, iterations):
    game_results = []

    # play specified number of games
    for i in range(iterations):
        game = Game.setup([player1, player2], variable_cards)
        final_game, results = game.run()
        game_results.append(results)
        if isinstance(player1, ComboLearner):
            player1.terminal_val(final_game)
            player1.saveweights("test_player1.csv")
        if isinstance(player2, ComboLearner):
            player1.terminal_val(final_game)
            player2.saveweights("test_player2.csv")
        

    print(game_results)
    return game_results

if __name__ == '__main__':
    testing(ComboLearner(), BigMoney(), 1000)
    #testing(ComboLearner(), smithyComboBot(), chapelComboBot(), 10)
    #testing(ComboLearner(), HillClimbBot(), chapelComboBot(), 10)