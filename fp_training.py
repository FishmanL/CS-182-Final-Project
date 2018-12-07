from dominiate import cards, dominion, game, players, combobot, derivbot, basic_ai
import csv
from final_project import *

# Options for AI Players:
# ComboLearner()            our q learner
# RandomBot()               an agent that randomly selects an available option
# GreedyBot()               an agent that chooses the card with highest value to buy
#                               and lowest cost to discard/trash
# BigMoney()                built-in, basic ai. An agent that aims to buy money
#                               and then buy victory
# SmithyBot()               built-in, basic ai
# HillClimbBot              built-in, basic ai
# ... any more that we create

# testing loop for non-Q learning agents
def testNotQAgents(player1, player2, iterations):
    wins = [] # binary array tracking wins of each game
    for i in range(iterations):
        board = game.Game.setup([player1, player2], cards.variable_cards)
        results = board.run()    # returns a dictionary mapping players to scores
        if results[0][0].name == player1.name:
            score1 = results[0][1]
            score2 = results[1][1]
        else:
            score1 = results[1][1]
            score2 = results[0][1]
        
        # 1 if player 1 wins, 0 otherwise
        if score1 > score2:
            wins.append(1)
        else:
            wins.append(0)
    
    # return winning percentage
    print(float(sum(wins)) / float(iterations))
    return float(sum(wins)) / float(iterations)
    

def testQAgents(player1, player2, iterations):
    game_results = []

    # play specified number of games
    for i in range(iterations):
        game = Game.setup([player1, player2], variable_cards)
        results = game.run()
        player1.saveweights("test_player1.csv")
        player2.saveweights("test_player2.csv")
        game_results.append(results)

    print(game_results)
    return game_results

if __name__ == '__main__':
    # testQAgents(ComboLearner(), ComboLearner(), 10)
    # testQAgents(ComboLearner(), smithyComboBot(), 10)
    # testQAgents(ComboLearner(), HillClimbBot(), 10)
    # testNotQAgents(players.BigMoney(), basic_ai.GreedyBot(), 10)
    # testNotQAgents(basic_ai.GreedyBot(), basic_ai.GreedyToTest(), 100)
    testNotQAgents(basic_ai.RandomBot(), basic_ai.RandomToTest(), 2)