import cards
import dominion
import game
import players
from combobot import *
import derivbot
import math
from game import *
from players import *
from basic_ai import *
from combobot import *
from cards import variable_cards
from collections import defaultdict
import random

import csv
from final_project import *

# Options for AI Players:
# ComboLearner()            our q learner
# RandomBot()               an agent that randomly selects an available option
# GreedyBot()               an agent that chooses the card with highest value to buy
#                               and lowest cost to discard/trash
# BigMoney()                built-in, basic ai. An agent that aims to buy money
#                               and then buy victory
# chapelComboBot()          built-in, basic ai

# testing loop for non-Q learning agents
def testNotQAgents(player1, player2, iterations):
    wins = [] # binary array tracking wins of each game

    # play specified number of games
    for i in range(iterations):
        board = game.Game.setup([player1, player2], cards.variable_cards)
        final_game, results = board.run()    # returns a dictionary mapping players to scores
        if results[0][0].name == player1.name:
            score1 = results[0][1]
            score2 = results[1][1]
        else:
            score1 = results[1][1]
            score2 = results[0][1]
    
    # return winning percentage
        if score1 > score2:
            wins.append(1.0)
        elif score2 > score1:
            wins.append(0.0)
        else:
            wins.append(None)

    # return winning percentage
    wins_no_ties = filter(lambda x: x is not None, wins)
    win_rate = float(sum(wins_no_ties)) / len(wins)
    tie_rate = float(iterations - len(wins_no_ties)) / len(wins)

    # print(game_results)
    print("WIN RATE: " + str(win_rate))
    print("TIE RATE: " + str(tie_rate))
    print("LOSE RATE: " + str(1.0-tie_rate-win_rate))
    
# testing/training loop for Q-learning agents
def testQAgents(player1, player2, iterations):
    game_results = []
    wins = []

    # play specified number of games
    for i in range(iterations):
        game = Game.setup([player1, player2], variable_cards)

        final_game, results = game.run()
        game_results.append(results)
        if isinstance(player1, ComboLearner):
            player1.terminal_val(final_game)
            player1.saveweights("test_player1.csv")
        if isinstance(player2, ComboLearner):
            player2.terminal_val(final_game)
            player2.saveweights("test_player2.csv")

        if results[0][0].name == player1.name:
            score1 = results[0][1]
            score2 = results[1][1]
        else:
            score1 = results[1][1]
            score2 = results[0][1]

        # 1 if player 1 wins, 0 if loss, None if tie
        if score1 > score2:
            wins.append(1.0)
        elif score2 > score1:
            wins.append(0.0)
        else:
            wins.append(None)

    # return winning percentage
    wins_no_ties = filter(lambda x: x is not None, wins)
    win_rate = float(sum(wins_no_ties)) / len(wins)
    tie_rate = float(iterations - len(wins_no_ties)) / len(wins)

    # print(game_results)
    print("WIN RATE: " + str(win_rate))
    print("TIE RATE: " + str(tie_rate))
    print("LOSE RATE: " + str(1.0-tie_rate-win_rate))
    # print(wins)
    return win_rate, tie_rate

# determine improvement in performance over training; track win/tie rates
def testQtrackWins(trainer, player2, reward):

    wins_overall = []
    ties_overall = []

    w, t = testQAgents(ComboLearner(reward_fun=reward, epsilon=0.25), trainer, 1)

    # play specified number of games, tracking wins
    for rnd in range(20):
        game_results = []
        wins = []

        # define player
        player1 = ComboLearner(reward_fun=reward, epsilon=0, loadfile='test_player1.csv', learning_mode=False)

        # run 100 test games
        for i in range(100):
            game = Game.setup([player1, player2], variable_cards)

            final_game, results = game.run()
            game_results.append(results)
            if isinstance(player1, ComboLearner):
                player1.terminal_val(final_game)
            if isinstance(player2, ComboLearner):
                player2.terminal_val(final_game)

            if results[0][0].name == player1.name:
                score1 = results[0][1]
                score2 = results[1][1]
            else:
                score1 = results[1][1]
                score2 = results[0][1]

            # 1 if player 1 wins, 0 if loss, None if tie
            if score1 > score2:
                wins.append(1.0)
            elif score2 > score1:
                wins.append(0.0)
            else:
                wins.append(None)

        # get winning percentage for this round
        wins_no_ties = filter(lambda x: x is not None, wins)
        win_rate = float(sum(wins_no_ties)) / len(wins)
        tie_rate = float(100 - len(wins_no_ties)) / len(wins)

        wins_overall.append(win_rate)
        ties_overall.append(tie_rate)

        # train one more iteration
        testQAgents(ComboLearner(reward_fun=reward, epsilon=0.25, loadfile='test_player1.csv'), trainer, 1)

    print(wins_overall)
    print(ties_overall)

    return wins_overall, ties_overall

# training loop for decreasing epsilon
def QDecreaseEpsilon(player2=GreedyBot(), iterations=100, reward_fun='proportional',iEpsilon=1.0):
	p1 = ComboLearner(reward_fun=reward_fun, epsilon=iEpsilon)
	wins, ties = testQAgents(p1, player2, 1)
	for i in range(iterations - 1):
		p1.epsilon = iEpsilon/math.exp(i/math.sqrt(iterations))
 		win, tie = testQAgents(p1, player2, 1)
		wins += win
		ties += tie

	win_rate = wins / iterations
	tie_rate = ties / iterations

	print("WIN RATE: " + str(win_rate))
	print("TIE RATE: " + str(tie_rate))
	print("LOSE RATE: " + str(1.0-tie_rate-win_rate))

	return win_rate, tie_rate

# train on three AIs iteratively
def iterativeTraining(opponent1=GreedyBot(), opponent2=BigMoney(), opponent3=chapelComboBot, iterations=100, reward='proportional'):
    p1 = ComboLearner(reward_fun=reward)
    wins, ties = testQAgents(p1, GreedyBot(), 1)
    for i in range(int((iterations-1) / 3)):
        win1, tie1 = testQAgents(p1, opponent1, 1)
        win2, tie2 = testQAgents(p1, opponent2, 1)
        win3, tie3 = testQAgents(p1, opponent3, 1)
        wins = wins + win1 + win2 + win3
        ties = ties + tie1 + tie2 + tie3

    win_rate = wins / iterations
    tie_rate = ties / iterations

    print("WIN RATE: " + str(win_rate))
    print("TIE RATE: " + str(tie_rate))
    print("LOSE RATE: " + str(1.0-tie_rate-win_rate))


if __name__ == '__main__':
    # test bots against each other as baseline
    # testNotQAgents(GreedyBot(), BigMoney(), 100)

    ###############################################
    ### COMBOLEARNERS TRAINED AGAINST RANDOMBOT ###
    ###############################################

    # Bot 01
    #  testQAgents(ComboLearner(reward_fun='proportional', epsilon=0.25), RandomBot(), 100)
    #  testQAgents(ComboLearner(reward_fun='proportional', epsilon=0, loadfile='weights/weightsBot01.csv', learning_mode=False), RandomBot(), 100)
    #  testQAgents(ComboLearner(reward_fun='proportional', epsilon=0, loadfile='weights/weightsBot01.csv', learning_mode=False), GreedyBot(), 100)
    #  testQAgents(ComboLearner(reward_fun='proportional', epsilon=0, loadfile='weights/weightsBot01.csv', learning_mode=False), BigMoney(), 100)
    #  testQAgents(ComboLearner(reward_fun='proportional', epsilon=0, loadfile='weights/weightsBot01.csv', learning_mode=False), chapelComboBot, 100)

    # Bot 02
    # QDecreaseEpsilon(RandomBot())
    # testQAgents(ComboLearner(reward_fun='proportional', epsilon=0, loadfile='weights/weightsBot02.csv', learning_mode=False), RandomBot(), 100)
    # testQAgents(ComboLearner(reward_fun='proportional', epsilon=0, loadfile='weights/weightsBot02.csv', learning_mode=False), GreedyBot(), 100)
    # testQAgents(ComboLearner(reward_fun='proportional', epsilon=0, loadfile='weights/weightsBot02.csv', learning_mode=False), BigMoney(), 100)
    # testQAgents(ComboLearner(reward_fun='proportional', epsilon=0, loadfile='weights/weightsBot02.csv', learning_mode=False), chapelComboBot, 100)

    # Bot 03
    # testQAgents(ComboLearner(reward_fun='zero sum', epsilon=0.25), RandomBot(), 100)
    # testQAgents(ComboLearner(reward_fun='zero sum', epsilon=0, loadfile='weights/weightsBot03.csv', learning_mode=False), RandomBot(), 100)
    # testQAgents(ComboLearner(reward_fun='zero sum', epsilon=0, loadfile='weights/weightsBot03.csv', learning_mode=False), GreedyBot(), 100)
    # testQAgents(ComboLearner(reward_fun='zero sum', epsilon=0, loadfile='weights/weightsBot03.csv', learning_mode=False), BigMoney(), 100)
    # testQAgents(ComboLearner(reward_fun='zero sum', epsilon=0, loadfile='weights/weightsBot03.csv', learning_mode=False), chapelComboBot, 100)

    # Bot 04
    # QDecreaseEpsilon(RandomBot(),reward_fun='zero sum')
    # testQAgents(ComboLearner(reward_fun='zero sum', epsilon=0, loadfile='weights/weightsBot04.csv', learning_mode=False), RandomBot(), 100)
    # testQAgents(ComboLearner(reward_fun='zero sum', epsilon=0, loadfile='weights/weightsBot04.csv', learning_mode=False), GreedyBot(), 100)
    # testQAgents(ComboLearner(reward_fun='zero sum', epsilon=0, loadfile='weights/weightsBot04.csv', learning_mode=False), BigMoney(), 100)
    # testQAgents(ComboLearner(reward_fun='zero sum', epsilon=0, loadfile='weights/weightsBot04.csv', learning_mode=False), chapelComboBot, 100)


    ############################################
    ### COMBOLEARNERS TRAINED AGAINST GREEDY ###
    ############################################

    # Bot 05
    # testQAgents(ComboLearner(reward_fun='proportional', epsilon=0.25), GreedyBot(), 100)
    # testQAgents(ComboLearner(reward_fun='proportional', epsilon=0, loadfile='weights/weightsBot05.csv', learning_mode=False), RandomBot(), 100)
    # testQAgents(ComboLearner(reward_fun='proportional', epsilon=0, loadfile='weights/weightsBot05.csv', learning_mode=False), GreedyBot(), 100)
    # testQAgents(ComboLearner(reward_fun='proportional', epsilon=0, loadfile='weights/weightsBot05.csv', learning_mode=False), BigMoney(), 100)
    # testQAgents(ComboLearner(reward_fun='proportional', epsilon=0, loadfile='weights/weightsBot05.csv', learning_mode=False), chapelComboBot, 100)

    # Bot 06

    # QDecreaseEpsilon()
    # testQAgents(ComboLearner(reward_fun='proportional', epsilon=0, loadfile='weights/weightsBot06.csv', learning_mode=False), RandomBot(), 100)
    # testQAgents(ComboLearner(reward_fun='proportional', epsilon=0, loadfile='weights/weightsBot06.csv', learning_mode=False), GreedyBot(), 100)
    # testQAgents(ComboLearner(reward_fun='proportional', epsilon=0, loadfile='weights/weightsBot06.csv', learning_mode=False), BigMoney(), 100)
    # testQAgents(ComboLearner(reward_fun='proportional', epsilon=0, loadfile='weights/weightsBot06.csv', learning_mode=False), chapelComboBot, 100)

    # Bot 07
    # testQAgents(ComboLearner(reward_fun='zero sum', epsilon=0.25), GreedyBot(), 500)
    # testQAgents(ComboLearner(reward_fun='zero sum', epsilon=0, loadfile='weights/weightsBot07.csv', learning_mode=False), RandomBot(), 100)
    # testQAgents(ComboLearner(reward_fun='zero sum', epsilon=0, loadfile='weights/weightsBot07.csv', learning_mode=False), GreedyBot(), 100)
    # testQAgents(ComboLearner(reward_fun='zero sum', epsilon=0, loadfile='weights/weightsBot07.csv', learning_mode=False), BigMoney(), 100)
    # testQAgents(ComboLearner(reward_fun='zero sum', epsilon=0, loadfile='weights/weightsBot07.csv', learning_mode=False), chapelComboBot, 100)

    # Bot 08
    # QDecreaseEpsilon(GreedyBot(),reward_fun='zero sum')
    # testQAgents(ComboLearner(reward_fun='zero sum', epsilon=0, loadfile='weights/weightsBot08.csv', learning_mode=False), RandomBot(), 100)
    # testQAgents(ComboLearner(reward_fun='zero sum', epsilon=0, loadfile='weights/weightsBot08.csv', learning_mode=False), GreedyBot(), 100)
    # testQAgents(ComboLearner(reward_fun='zero sum', epsilon=0, loadfile='weights/weightsBot08.csv', learning_mode=False), BigMoney(), 100)
    # testQAgents(ComboLearner(reward_fun='zero sum', epsilon=0, loadfile='weights/weightsBot08.csv', learning_mode=False), chapelComboBot, 100)

    ##############################################
    ### COMBOLEARNERS TRAINED AGAINST BIGMONEY ###
    ##############################################

    # Bot 09
    # testQAgents(ComboLearner(reward_fun='proportional', epsilon=0.25), BigMoney(), 100)
    # testQAgents(ComboLearner(reward_fun='proportional', epsilon=0, loadfile='weights/weightsBot09.csv', learning_mode=False), RandomBot(), 100)
    # testQAgents(ComboLearner(reward_fun='proportional', epsilon=0, loadfile='weights/weightsBot09.csv', learning_mode=False), GreedyBot(), 100)
    # testQAgents(ComboLearner(reward_fun='proportional', epsilon=0, loadfile='weights/weightsBot09.csv', learning_mode=False), BigMoney(), 100)
    # testQAgents(ComboLearner(reward_fun='proportional', epsilon=0, loadfile='weights/weightsBot09.csv', learning_mode=False), chapelComboBot, 100)

    # Bot 10
    # QDecreaseEpsilon(BigMoney())
    # testQAgents(ComboLearner(reward_fun='proportional', epsilon=0, loadfile='weights/weightsBot10.csv', learning_mode=False), RandomBot(), 100)
    # testQAgents(ComboLearner(reward_fun='proportional', epsilon=0, loadfile='weights/weightsBot10.csv', learning_mode=False), GreedyBot(), 100)
    # testQAgents(ComboLearner(reward_fun='proportional', epsilon=0, loadfile='weights/weightsBot10.csv', learning_mode=False), BigMoney(), 100)
    # testQAgents(ComboLearner(reward_fun='proportional', epsilon=0, loadfile='weights/weightsBot10.csv', learning_mode=False), chapelComboBot, 100)

    # Bot 11
    # testQAgents(ComboLearner(reward_fun='zero sum', epsilon=0.25), BigMoney(), 100)
    # testQAgents(ComboLearner(reward_fun='zero sum', epsilon=0, loadfile='weights/weightsBot11.csv', learning_mode=False), RandomBot(), 100)
    # testQAgents(ComboLearner(reward_fun='zero sum', epsilon=0, loadfile='weights/weightsBot11.csv', learning_mode=False), GreedyBot(), 100)
    # testQAgents(ComboLearner(reward_fun='zero sum', epsilon=0, loadfile='weights/weightsBot11.csv', learning_mode=False), BigMoney(), 100)
    # testQAgents(ComboLearner(reward_fun='zero sum', epsilon=0, loadfile='weights/weightsBot11.csv', learning_mode=False), chapelComboBot, 100)

    # Bot 12
    # QDecreaseEpsilon(BigMoney(), reward_fun='zero sum')
    # testQAgents(ComboLearner(reward_fun='zero sum', epsilon=0, loadfile='weights/weightsBot12.csv', learning_mode=False), RandomBot(), 100)
    # testQAgents(ComboLearner(reward_fun='zero sum', epsilon=0, loadfile='weights/weightsBot12.csv', learning_mode=False), GreedyBot(), 100)
    # testQAgents(ComboLearner(reward_fun='zero sum', epsilon=0, loadfile='weights/weightsBot12.csv', learning_mode=False), BigMoney(), 100)
    # testQAgents(ComboLearner(reward_fun='zero sum', epsilon=0, loadfile='weights/weightsBot12.csv', learning_mode=False), chapelComboBot, 100)

    ####################################################
    ### COMBOLEARNERS TRAINED AGAINST CHAPELCOMBOBOT ###
    ####################################################

    # Bot 13
    #testQAgents(ComboLearner(reward_fun='proportional', epsilon=0.25), chapelComboBot, 100)
    #testQAgents(ComboLearner(reward_fun='proportional', epsilon=0, loadfile='weights/weightsBot13.csv', learning_mode=False), RandomBot(), 100)
    #testQAgents(ComboLearner(reward_fun='proportional', epsilon=0, loadfile='weights/weightsBot13.csv', learning_mode=False), GreedyBot(), 100)
    #testQAgents(ComboLearner(reward_fun='proportional', epsilon=0, loadfile='weights/weightsBot13.csv', learning_mode=False), BigMoney(), 100)
    #testQAgents(ComboLearner(reward_fun='proportional', epsilon=0, loadfile='weights/weightsBot13.csv', learning_mode=False), chapelComboBot, 100)

    # Bot 14
    # QDecreaseEpsilon(chapelComboBot)
    # testQAgents(ComboLearner(reward_fun='proportional', epsilon=0, loadfile='weights/weightsBot14.csv', learning_mode=False), RandomBot(), 100)
    # testQAgents(ComboLearner(reward_fun='proportional', epsilon=0, loadfile='weights/weightsBot14.csv', learning_mode=False), GreedyBot(), 100)
    # testQAgents(ComboLearner(reward_fun='proportional', epsilon=0, loadfile='weights/weightsBot14.csv', learning_mode=False), BigMoney(), 100)
    # testQAgents(ComboLearner(reward_fun='proportional', epsilon=0, loadfile='weights/weightsBot14.csv', learning_mode=False), chapelComboBot, 100)

    # Bot 15
    #testQAgents(ComboLearner(reward_fun='zero sum', epsilon=0.25), chapelComboBot, 100)
    # testQAgents(ComboLearner(reward_fun='zero sum', epsilon=0, loadfile='weights/weightsBot15.csv', learning_mode=False), RandomBot(), 100)
    # testQAgents(ComboLearner(reward_fun='zero sum', epsilon=0, loadfile='weights/weightsBot15.csv', learning_mode=False), GreedyBot(), 100)
    # testQAgents(ComboLearner(reward_fun='zero sum', epsilon=0, loadfile='weights/weightsBot15.csv', learning_mode=False), BigMoney(), 100)
    # testQAgents(ComboLearner(reward_fun='zero sum', epsilon=0, loadfile='weights/weightsBot15.csv', learning_mode=False), chapelComboBot, 100)

    # Bot 16
    # QDecreaseEpsilon(chapelComboBot,reward_fun='zero sum')
    # testQAgents(ComboLearner(reward_fun='zero sum', epsilon=0, loadfile='weights/weightsBot16.csv', learning_mode=False), RandomBot(), 100)
    # testQAgents(ComboLearner(reward_fun='zero sum', epsilon=0, loadfile='weights/weightsBot16.csv', learning_mode=False), GreedyBot(), 100)
    # testQAgents(ComboLearner(reward_fun='zero sum', epsilon=0, loadfile='weights/weightsBot16.csv', learning_mode=False), BigMoney(), 100)
    # testQAgents(ComboLearner(reward_fun='zero sum', epsilon=0, loadfile='weights/weightsBot16.csv', learning_mode=False), chapelComboBot, 100)

    #########################################  
    ### COMBOLEARNERS TRAINED ITERATIVELY ###
    #########################################

    # Bot 17
    # iterativeTraining()

    # testQAgents(ComboLearner(reward_fun='proportional', epsilon=0, loadfile='weights/weightsBot17.csv', learning_mode=False), RandomBot(), 100)
    # testQAgents(ComboLearner(reward_fun='proportional', epsilon=0, loadfile='weights/weightsBot17.csv', learning_mode=False), GreedyBot(), 100)
    # testQAgents(ComboLearner(reward_fun='proportional', epsilon=0, loadfile='weights/weightsBot17.csv', learning_mode=False), BigMoney(), 100)
    # testQAgents(ComboLearner(reward_fun='proportional', epsilon=0, loadfile='weights/weightsBot17.csv', learning_mode=False), chapelComboBot, 100)

    # Bot 18
    # iterativeTraining(reward='zero sum')

    # testQAgents(ComboLearner(reward_fun='proportional', epsilon=0, loadfile='weightsBot18.csv', learning_mode=False), RandomBot(), 100)
    # testQAgents(ComboLearner(reward_fun='proportional', epsilon=0, loadfile='weightsBot18.csv', learning_mode=False), GreedyBot(), 100)
    # testQAgents(ComboLearner(reward_fun='proportional', epsilon=0, loadfile='weightsBot18.csv', learning_mode=False), BigMoney(), 100)
    # testQAgents(ComboLearner(reward_fun='proportional', epsilon=0, loadfile='weightsBot18.csv', learning_mode=False), chapelComboBot, 100)


    #############################################  
    ### TRACK WIN RATE CHANGES OF SELECT BOTS ###
    #############################################

    # testing bot05
    # testQtrackWins(GreedyBot(), RandomBot(), 'proportional')
    # testQtrackWins(GreedyBot(), GreedyBot(), 'proportional')

    # testing bot07
    # testQtrackWins(GreedyBot(), RandomBot(), 'zero sum')
    # testQtrackWins(GreedyBot(), GreedyBot(), 'zero sum')

    # testing 
    # testQtrackWins(BigMoney(), GreedyBot(), 'proportional')

