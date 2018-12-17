import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


# read desired columns of the given CSV
csv_name = 'graphtest.csv'
rawQVals = pd.read_csv(csv_name, header=None, index_col=False)
allQVals = pd.DataFrame(rawQVals)

# Q-values for buy (located every fourth row from row 0)
buyQVals = allQVals.iloc[::4, :].dropna(axis=(0,1), how='all').reset_index(drop=True)

# Q-values for trash (located every fourth row from row 1)
trashQVals = allQVals.iloc[1::4, :].dropna(axis=(0,1), how='all').reset_index(drop=True)

# Q-values for discard (located every fourth row from row 2)
discardQVals = allQVals.iloc[2::4, :].dropna(axis=(0,1), how='all').reset_index(drop=True)

# Q-values for play/action (located every fourth row from row 3)
playQVals = allQVals.iloc[3::4, :].dropna(axis=(0,1), how='all').reset_index(drop=True)

print(buyQVals)
print(trashQVals)
print(discardQVals)
print(type(playQVals))


# # use df.dropna to drop rows
# # use df.reset_index(drop=True, inplace=True)

def grapher(move_type, csv_name):
	if move_type == 'buy':
		x = 0
	elif move_type == 'trash':
		x = 1
	elif move_type == 'discard':
		x = 2
	elif move_type == 'play':
		x = 3
	else:
		print("Error: move_type must be buy, trash, discard, or play")
		return

	rawQVals = pd.read_csv(csv_name, header=None, index_col=False)
	allQVals = pd.DataFrame(rawQVals)
	QVals = allQVals.iloc[x::4, :].dropna(axis=(0,1), how='all').reset_index(drop=True)

	# set up x axis (number of iterations)
	iterations = QVals.shape()[0]	# rows

	if iterations == 1:
		print("Error: Not enough data to graph")
		return

	xaxis = [i for i in range(iterations-1)]

	# set up y axis (one line for each feature)
	features = QVals.shape()[1]		# columns

	# need to create an array for each feature
	for f in range(features-1):
		feature = []
		for i in range(iterations-1):
			# iterate for index f each row, add to a list,
			# then add that list to a list of lists (np.array?)

#     "    # get lists for each desired metric\n",
#     "    for index, x in np.ndenumerate(graph_marray):\n",
#     "        # get total changes\n",
#     "        if index[1] == 0:\n",
#     "            graph_totals.append(x)\n",
#     "        # get total length 0\n",
#     "        elif index[1] == 1:\n",
#     "            graph_len0s.append(x)\n",
#     "        # get total unique diff hashes\n",
#     "        elif index[1] == 2:\n",
#     "            graph_diffs.append(x)\n",
#     "        # get total unique text diff hashes\n",
#     "        elif index[1] == 3:\n",
#     "            graph_txtdiffs.append(x)\n",
#     "        # not collecting this metric; move on\n",
#     "        else:\n",
#     "            continue\n",
#     "\n",
#     "    # draw graph with four metrics\n",
#     "    plt.plot(graph_dates, graph_totals, 'ko-', label='Total Changes')\n",
#     "    plt.plot(graph_dates, graph_len0s, 'r--', label='Diff Length Zero')\n",
#     "    plt.plot(graph_dates, graph_diffs, 'g--', label='Unique Diffs')\n",
#     "    plt.plot(graph_dates, graph_txtdiffs, 'c--', label='Unique Text Diffs')\n",
#     "    plt.legend()\n",
#     "    plt.title(site_name)\n",
#     "    plt.xticks(graph_dates, graph_dates, rotation=40, ha='right')\n",
#     "    plt.show()"

#    "source": [
#     "### GRAPH THE METRICS FROM ONE DOMAIN ROW ###\n",
#     "# accepts input of type string, corresponding to domain name\n",
#     "\n",
#     "def graph_site(site_name):\n",
#     "    row = domain_stats[domain_stats['Domain Name'] == site_name]\n",
#     "\n",
#     "    # make sure exactly 1 row was selected\n",
#     "    if row.shape[0] > 1:\n",
#     "        print(\"Input matches more than one site\")\n",
#     "    elif row.shape[0] == 0:\n",
#     "        print(\"Input does not match any domain in dataframe\")\n",
#     "    else:\n",
#     "        grapher(row.squeeze())"