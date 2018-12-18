import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

### FIRST SET OF GRAPHS: CUMULATIVE WIN RATE DURING TRAINING ###

# get a list of the cumulative win rate during training
def getTrainingWins(index, winList):
	games = len(winList)
	cumulative = []
	for i in range(games):
		if winList[i] == None:
			winList[i] = 0.0
		cur_sum = sum(winList[:i+1])
		cumulative.append(cur_sum / (i+1))
	print(cumulative)
	return index, cumulative

# graph the win rate for the four variations of each bot(s) we trained against
def graphTrainingWins(trainedAgainst, botA, listA, botB, listB, botC, listC, botD, listD):
	# verify list lengths are correct and graphable
	if not len(listA) == len(listB) == len(listC)== len(listD):
		raise ValueError('Lists must have the same length')
	if len(listA) <= 1:
		raise ValueError("Not enough data to graph - need more iterations")

	# graph a line for each variation of the trained bot
	plt.plot(listA, 'k-', label=botA)
	plt.plot(listB, 'r-', label=botB)
	plt.plot(listC, 'g-', label=botC)
	plt.plot(listD, 'c-', label=botD)
	plt.legend()
	plt.xlabel("Iterations")
	plt.ylabel("Win Proportions")
	plt.title(trainedAgainst + ": Cumulative Win Rate During Training")
	plt.show()

### SECOND SET OF GRAPHS: Q-VALUES CONVERGING IN TRAINING PHASE ###

def graphQValues(bot, csv_name):
	# because there are different numbers of features, set N = the max # for accurate csv reading
	# there are 38 buys, 54 trashes, 21 discards, and 21 plays
	N = 54

	# read desired columns of the given CSV
	rawQVals = pd.read_csv(csv_name, header=None, index_col=False, names = list(range(0,N)))
	allQVals = pd.DataFrame(rawQVals)

	# Q-values for each decision point
		# remove columns where there are no features for a given decision point
		# transpose the dataframes so that each row is one feature
	buyQVals = allQVals.iloc[::4, :].dropna(axis=(0,1), how='all').reset_index(drop=True).transpose()
	trashQVals = allQVals.iloc[1::4, :].dropna(axis=(0,1), how='all').reset_index(drop=True).transpose()
	discardQVals = allQVals.iloc[2::4, :].dropna(axis=(0,1), how='all').reset_index(drop=True).transpose()
	playQVals = allQVals.iloc[3::4, :].dropna(axis=(0,1), how='all').reset_index(drop=True).transpose()

	# check number of iterations is graphable
	iterations = buyQVals.shape[1]
	if iterations <= 1:
		raise ValueError("Not enough data to graph - need more iterations")

	# graph Q-values for buy features
	for i in range(buyQVals.shape[0]):
		if i == 0:
			buyLine, = plt.plot(buyQVals.iloc[i], 'k-', label='Buy Features (38 total)')
		else:
			plt.plot(buyQVals.iloc[i], 'k-')

	# graph Q-values for trash features
	for i in range(trashQVals.shape[0]):
		if i == 0:
			trashLine, = plt.plot(trashQVals.iloc[i], 'r-', label='Trash Features (54 total)')
		else:
			plt.plot(trashQVals.iloc[i], 'r-')
	
	# graph Q-values for discard features
	for i in range(discardQVals.shape[0]):
		if i == 0:
			discardLine, = plt.plot(discardQVals.iloc[i], 'g-', label='Discard Features (21 total)')
		else:
			plt.plot(discardQVals.iloc[i], 'g-')
	
	# graph Q-values for play features
	for i in range(playQVals.shape[0]):
		if i == 0:
			playLine, = plt.plot(playQVals.iloc[i], 'c-', label='Play Features (21 total)')
		else:
			plt.plot(playQVals.iloc[i], 'c-')

	plt.legend(handles=[buyLine, trashLine, discardLine, playLine], ncol=2, loc=9)
	plt.xlabel("Iterations")
	plt.ylabel("Q-Value")
	plt.title(bot + ": Q-Values Converging in Training Phase")
	plt.show()

### THIRD SET OF GRAPHS: WIN/TIE/LOSS PERCENTAGES FOR TRAINED BOTS ###
		### TESTED AGAINST MULTIPLE OPPONENTS ###

def graphTestOutcomes(bot, winRates, tieRates, lossRates):
	r = [0, 1, 2, 3]	# win, tie, loss
	barWidth = 0.85
	names = ('RandomBot','GreedyBot','BigMoney','ChapelBot')
	
	# create bars for wins
	plt.bar(r, winRates, color='#8BF689', edgecolor='white', width=barWidth, label="Wins")
	# create bars for ties
	plt.bar(r, tieRates, bottom=winRates, color='#CAC3C2', edgecolor='white', width=barWidth, label="Ties")
	# create bars for losses
	plt.bar(r, lossRates, bottom=[i+j for i,j in zip(winRates, tieRates)], color='#FF7A68', edgecolor='white', width=barWidth, label="Losses")
	 
	plt.xticks(r, names)
	plt.xlabel("Opponent")
	plt.legend(loc='upper left', bbox_to_anchor=(0.15,1.06), ncol=3)
	plt.title(bot + ": Game Performance Against Various Opponents", pad=18.)
	plt.show()

# code for graphTestOutcomes modified from:
# https://python-graph-gallery.com/13-percent-stacked-barplot/

if __name__ == '__main__':
	# bot01, list01 = getTrainingWins('bot01', [None, None, None, None, None, None, None, None, None])
	# bot02, list02 = getTrainingWins('bot02', [0.0, None, 1.0, 0.0, 0.0, 1.0, 0.0, None, 1.0])
	# bot03, list03 = getTrainingWins('bot03', [1.0, 1.0, 1.0, None, 0.0, 1.0, 1.0, None, 1.0])
	# bot04, list04 = getTrainingWins('bot04', [None, None, 1.0, 1.0, 0.0, 1.0, 1.0, 0.0, 0.0])
	# graphTrainingWins('RandomBot', bot01, list01, bot02, list02, bot03, list03, bot04, list04)

	# graphQValues('bot01', 'test_player1.csv')

	graphTestOutcomes('TestBot', [0.5, 0.1, 0.0, 0.9], [0.2, 0.6, 0.5, 0.05], [0.3, 0.3, 0.5, 0.05])

