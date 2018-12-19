import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


###############################################
### GRAPHS 1: WIN/TIE RATES DURING TRAINING ###
###############################################


# get a list of the cumulative win rate during training
def getTrainingWins(winList):
	games = len(winList)
	cumulative = []
	for i in range(games):
		if winList[i] == None:
			winList[i] = 0.0
		cur_sum = sum(winList[:i+1])
		cumulative.append(cur_sum / (i+1))
	print(cumulative)
	return cumulative


# graph the win rate during training for 5 bots
def graphTrainingWins(listA, listB, listC, listD, listE):
	# verify list lengths are correct and graphable
	if not len(listA) == len(listB) == len(listC) == len(listD) == len(listE):
		raise ValueError('Lists must have the same length')
	if len(listA) <= 1:
		raise ValueError("Not enough data to graph - need more iterations")

	# graph a line for each variation of the trained bot
	plt.plot(listA, 'k-', label='Bot01 (Random, Proportional)', alpha=0.7)
	plt.plot(listB, 'r-', label='Bot05 (Greedy, Proportional)', alpha=0.7)
	plt.plot(listC, 'g-', label='Bot07 (Greedy, Zero Sum)', alpha=0.7)
	plt.plot(listD, 'c-', label='Bot09 (BigMoney, Proportional)', alpha=0.7)
	plt.plot(listE, 'm--', label='Bot11 (BigMoney, Zero Sum', alpha=0.7)
	plt.legend()
	plt.xlabel("Iterations")
	plt.ylabel("Win Proportions")
	plt.title("Cumulative Win Rate During Training (100 iterations)")
	plt.show()


# graph the win rate for 100 rounds of 100 iterations each
def graphTrainingWTLoop(Awins, Aties, Bwins, Bties, Cwins, Cties, Dwins, Dties):

	# graph a line for each variation of the trained bot
	plt.plot(Awins, 'r-', label='Bot05 vs Random, Win Rate')
	plt.plot(Aties, 'r--', label='Bot05 vs Random, Tie Rate')
	plt.plot(Bwins, 'g-', label='Bot05 vs Greedy, Win Rate')
	plt.plot(Bties, 'g--', label='Bot05 vs Greedy, Tie Rate')
	plt.plot(Cwins, 'c-', label='Bot07 vs Random, Win Rate')
	plt.plot(Cties, 'c--', label='Bot07 vs Random, Tie Rate')
	plt.plot(Dwins, 'm-', label='Bot07 vs Greedy, Win Rate')
	plt.plot(Dties, 'm--', label='Bot07 vs Greedy, Tie Rate')

	plt.legend(ncol=2, loc="center", bbox_to_anchor=(0.7,0.6), fontsize='x-small')
	plt.xlabel("Rounds")
	plt.title("Win and Tie Rates During Training")
	plt.show()


#######################################################
### GRAPHS 2: Q-VALUES CONVERGING IN TRAINING PHASE ###
#######################################################


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


######################################################
### GRAPHS 3: WIN/TIE/LOSS RATES FOR TRAINED BOTS, ###
### 	  TESTED AGAINST MULTIPLE OPPONENTS 	   ###
######################################################


def graphTestOutcomes(bot, winRates, tieRates, lossRates):
	r = [0, 1, 2, 3]	# win, tie, loss
	barWidth = 0.2
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

	# win rates during training for select bots + opponents
	bot05vRandomW = [0.78, 0.78, 0.79, 0.77, 0.79, 0.78, 0.82, 0.79, 0.75, 0.79, 0.72, 0.77, 0.86, 0.79, 0.84, 0.82, 0.8, 0.81, 0.76, 0.8, 0.83, 0.81, 0.75, 0.77, 0.75, 0.68, 0.72, 0.75, 0.71, 0.73, 0.76, 0.79, 0.78, 0.84, 0.7, 0.84, 0.77, 0.82, 0.81, 0.81, 0.87, 0.81, 0.77, 0.83, 0.85, 0.87, 0.74, 0.74, 0.76, 0.74, 0.86, 0.75, 0.86, 0.81, 0.79, 0.81, 0.77, 0.78, 0.76, 0.77, 0.77, 0.8, 0.7, 0.79, 0.83, 0.81, 0.84, 0.79, 0.75, 0.76, 0.79, 0.77, 0.86, 0.8, 0.87, 0.83, 0.83, 0.77, 0.84, 0.86, 0.79, 0.8, 0.85, 0.75, 0.81, 0.82, 0.75, 0.75, 0.78, 0.72, 0.75, 0.78, 0.79, 0.78, 0.82, 0.83, 0.84, 0.86, 0.74, 0.78]
	bot05vGreedyW = [0.2, 0.26, 0.26, 0.31, 0.4, 0.26, 0.28, 0.35, 0.27, 0.28, 0.32, 0.3, 0.26, 0.26, 0.26, 0.29, 0.28, 0.27, 0.28, 0.22, 0.24, 0.23, 0.25, 0.28, 0.25, 0.29, 0.22, 0.27, 0.28, 0.32, 0.24, 0.26, 0.25, 0.27, 0.27, 0.32, 0.27, 0.28, 0.23, 0.29, 0.27, 0.21, 0.25, 0.25, 0.28, 0.3, 0.22, 0.26, 0.2, 0.3]
	bot07vRandomW = [0.73, 0.75, 0.84, 0.79, 0.76, 0.83, 0.81, 0.79, 0.84, 0.78, 0.83, 0.78, 0.83, 0.82, 0.79, 0.81, 0.88, 0.83, 0.77, 0.77, 0.75, 0.76, 0.77, 0.78, 0.82, 0.8, 0.79, 0.8, 0.8, 0.77, 0.8, 0.8, 0.76, 0.84, 0.72, 0.77, 0.87, 0.73, 0.79, 0.84, 0.81, 0.78, 0.77, 0.85, 0.84, 0.85, 0.84, 0.86, 0.79, 0.85]
	bot07vGreedyW = [0.27, 0.19, 0.21, 0.31, 0.39, 0.26, 0.28, 0.3, 0.31, 0.24, 0.29, 0.28, 0.29, 0.31, 0.27, 0.27, 0.26, 0.25, 0.3, 0.3, 0.29, 0.32, 0.34, 0.32, 0.34, 0.21, 0.3, 0.32, 0.29, 0.21, 0.24, 0.28, 0.27, 0.3, 0.33, 0.24, 0.2, 0.17, 0.27, 0.39, 0.26, 0.26, 0.27, 0.3, 0.31, 0.29, 0.27, 0.21, 0.28, 0.26]

	# tie rates during training for select bots + opponents
	bot05vRandomT = [0.03, 0.05, 0.04, 0.07, 0.03, 0.03, 0.03, 0.05, 0.04, 0.03, 0.08, 0.08, 0.02, 0.07, 0.06, 0.03, 0.03, 0.07, 0.07, 0.07, 0.02, 0.06, 0.08, 0.03, 0.03, 0.09, 0.14, 0.05, 0.06, 0.04, 0.09, 0.06, 0.1, 0.05, 0.04, 0.04, 0.04, 0.08, 0.04, 0.05, 0.03, 0.05, 0.07, 0.04, 0.0, 0.02, 0.07, 0.05, 0.07, 0.09, 0.02, 0.06, 0.03, 0.02, 0.06, 0.05, 0.07, 0.02, 0.09, 0.05, 0.04, 0.09, 0.06, 0.04, 0.04, 0.04, 0.04, 0.07, 0.05, 0.02, 0.04, 0.11, 0.05, 0.04, 0.03, 0.05, 0.03, 0.06, 0.03, 0.03, 0.04, 0.04, 0.02, 0.06, 0.03, 0.02, 0.07, 0.06, 0.04, 0.06, 0.04, 0.03, 0.06, 0.04, 0.03, 0.06, 0.03, 0.06, 0.07, 0.09]
	bot05vGreedyT = [0.3, 0.23, 0.23, 0.25, 0.21, 0.3, 0.19, 0.14, 0.27, 0.2, 0.22, 0.25, 0.2, 0.22, 0.2, 0.23, 0.2, 0.21, 0.22, 0.31, 0.24, 0.24, 0.21, 0.22, 0.22, 0.19, 0.28, 0.25, 0.33, 0.22, 0.31, 0.27, 0.23, 0.19, 0.27, 0.26, 0.27, 0.3, 0.27, 0.24, 0.19, 0.24, 0.27, 0.19, 0.27, 0.25, 0.25, 0.23, 0.31, 0.19]
	bot07vRandomT = [0.05, 0.06, 0.03, 0.03, 0.02, 0.04, 0.04, 0.05, 0.04, 0.01, 0.02, 0.07, 0.01, 0.04, 0.04, 0.01, 0.01, 0.06, 0.08, 0.05, 0.06, 0.06, 0.07, 0.04, 0.04, 0.07, 0.07, 0.05, 0.06, 0.03, 0.07, 0.04, 0.06, 0.03, 0.06, 0.04, 0.05, 0.04, 0.01, 0.02, 0.01, 0.01, 0.07, 0.02, 0.03, 0.03, 0.05, 0.02, 0.08, 0.04]
	bot07vGreedyT = [0.27, 0.31, 0.24, 0.31, 0.3, 0.29, 0.2, 0.17, 0.19, 0.3, 0.29, 0.21, 0.23, 0.24, 0.29, 0.15, 0.25, 0.3, 0.29, 0.23, 0.23, 0.22, 0.18, 0.33, 0.18, 0.2, 0.25, 0.2, 0.22, 0.24, 0.29, 0.26, 0.28, 0.26, 0.19, 0.25, 0.26, 0.31, 0.27, 0.2, 0.23, 0.22, 0.28, 0.27, 0.2, 0.2, 0.28, 0.27, 0.33, 0.27]

	graphTrainingWTLoop(bot05vRandomW[:50], bot05vRandomT[:50], bot05vGreedyW, bot05vGreedyT, bot07vRandomW, bot07vRandomT, bot07vGreedyW, bot07vGreedyT)

