from game import *
from players import *
from basic_ai import *
from combobot import *
from cards import variable_cards
from collections import defaultdict
import random
from dominiate import cards, dominion, game, players, combobot, derivbot
from keras import models, layers, regularizers, preprocessing
import csv
from final_project import *

# Options for Players:
# ComboLearner()            our q learner
# smithyComboBot()          from source code, basic ai
# chapelComboBot()          from source code, basic ai
# HillClimbBot(2, 3, 40)    from source code, basic ai
# ... any more that we create

def testing(player1, player2, player3, iterations):
    game_results = []

    # play specified number of games
    for i in range(iterations):
        game = Game.setup([player1, player2, player3], variable_cards)
        results = game.run()
        game_results.append(results)

    player1.saveweights("test1_player1.csv")
    player2.saveweights("test1_player2.csv")
    player3.saveweights("test1_player3.csv")
    
    print(game_results)
    return game_results

# run our q learner against the basic bots
def test2():
    player1 = smithyComboBot()
    player2 = chapelComboBot()
    player3 = HillClimbBot(2, 3, 40)
    player4 = ComboLearner()
    game_results = []

    # play 10 games
    for i in range(10):
        game = Game.setup([player1, player2, player3, player4], variable_cards)
        results = game.run()
        game_results.append(results)

    player1.saveweights("test1_player1.csv")
    player2.saveweights("test1_player2.csv")
    player3.saveweights("test1_player3.csv")
    
    print(game_results)
    return game_results



if __name__ == '__main__':
    test1()
    test2()