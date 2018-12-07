from dominiate import cards, dominion, game, players, combobot, derivbot, basic_ai
import csv
from final_project import *

# Options for Players:
# ComboLearner()            our q learner
# smithyComboBot()          from source code, basic ai
# chapelComboBot()          from source code, basic ai
# HillClimbBot(2, 3, 40)    from source code, basic ai
# ... any more that we create

def testRandomAgent(iterations):
    playerR = basic_ai.GreedyBot()
    player2 = players.BigMoney()
    wins = [] # binary array tracking wins of each game
    for i in range(iterations):
        board = game.Game.setup([playerR, player2], cards.variable_cards)
        results = board.run()    # returns a dictionary mapping players to scores
        if results[0][0].name == "RandomBot":
            scoreR = results[0][1]
            score2 = results[1][1]
        else:
            scoreR = results[1][1]
            score2 = results[0][1]
        
        # 1=R wins, 0 otherwise
        if scoreR >= score2:
            wins.append(1)
        else:
            wins.append(0)
    print(float(sum(wins)) / float(iterations))
    return float(sum(wins)) / float(iterations)
    # return winning percentage


        # win for R = 1, sum of array/trials = winning percentage



def testing(player1, player2, iterations):
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
    #testing(ComboLearner(), ComboLearner(), 10)
    #testing(ComboLearner(), smithyComboBot(), 10)
    #testing(ComboLearner(), HillClimbBot(), 10)
    testRandomAgent(100)