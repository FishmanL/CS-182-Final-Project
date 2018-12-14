import cards
import dominion
import game
import players
import combobot
import derivbot
from keras import models, layers, regularizers, preprocessing
import csv

# each index corresponds to the amount of one specific card
canonical_order = [game.curse, game.estate, game.duchy, game.province, game.copper, game.silver, game.gold,
                   cards.village, cards.cellar, cards.smithy, cards.festival, cards.market, cards.laboratory,
                   cards.chapel, cards.warehouse, cards.council_room, cards.militia, cards.moat]


# converts from an array of cards into an array of canonical numbered cards
def c2f (cards):
    currarr = [0 for _ in canonical_order]
    for c in cards:
        currarr[canonical_order.index(c)] += 1
    return currarr

# converts from a dict of cards into an array of canonical numbered cards
def g2f (carddict):
    currarr = [0 for _ in canonical_order]
    for (c, count) in carddict.items():
        currarr[canonical_order.index(c)] =count
    return currarr


class ComboLearner(players.BigMoney):
    def __init__(self, loadfile = None):
        if loadfile is None:
            self.buy_weights = [0 for _ in range((len(canonical_order) * 2))]
            self.trash_weights = [0 for _ in range((len(canonical_order) * 3))]
            self.discard_weights = [0 for _ in range((len(canonical_order) + 3))]
            self.play_weights = [0 for _ in range((len(canonical_order) + 3))]
            self.weights = [self.buy_weights, self.trash_weights, self.discard_weights, self.play_weights]
        else:
            self.loadweights(filename=loadfile)
            self.weights = [self.buy_weights, self.trash_weights, self.discard_weights, self.play_weights]

        self.buy_dict = dict()
        self.gamma = 0.5
        self.name = "Q-learner"
        players.BigMoney.__init__(self)

    """
    4 separate q learners
    """
    # gets four sets of weights from a csv file, if it exists
    def loadweights(self, filename = "weights.csv"):
        with open(filename, "r") as file:
            reader = csv.reader(file)
            introws = [[int(r) for r in row] for row in reader]
            self.buy_weights = introws[0]
            self.trash_weights = introws[1]
            self.discard_weights = introws[2]
            self.play_weights = introws[3]
    
            # saves weights to a csv file
            a = len(introws)
            self.buy_weights = introws[a-4]
            self.trash_weights = introws[a-3]
            self.discard_weights = introws[a-2]
            self.play_weights = introws[a-1]
    
    # saves weights to a csv file
    def saveweights(self, filename = "weights.csv"):
        with open(filename, "a+") as file:
            writer = csv.writer(file)
            self.weights = [self.buy_weights, self.trash_weights, self.discard_weights, self.play_weights]
            for weight in self.weights:
                writer.writerow(weight)
    
    # features for buying decisions, when you add a card from game to discard pile
    def from_state_features_buy (self, decision):
        game = decision.game
        deck = decision.state().all_cards()
        a = g2f(game.card_counts)
        a.extend(c2f(deck))
        return a
        pass
    
    # features for which cards to permanently remove from the deck
    def from_state_features_trash (self, decision):
        game = decision.game
        state = decision.state()
        deck = decision.state().all_cards()
        a = g2f(game.card_counts)
        a.extend(c2f(deck))
        a.extend(c2f(state.hand))
        return a
        pass

    # features for playing a card from hand
    def from_state_features_play (self, decision):
        state = decision.game.state()
        hand = state.hand
        a = c2f(hand)
        a.extend([state.actions, state.buys, state.hand_value()])
        return a
        pass

    # features for which cards to discard from your hand
    # TODO : is that correct interpretation? edit if needed
    def from_state_features_discard (self, decision):
        game = decision.game
        state = decision.game.state()
        a = c2f(state.hand)
        a.extend([state.actions, state.buys, state.hand_value()])
        return a
        pass

    def update_q_values(self, reward):
        cur_weights = self.buy_weights
        new_weights_list = list()

        for key in self.buy_dict:
            features = list(key[0])
            action = key[1]
            cur_q_value = key[2]
            count = self.buy_dict[key][0]
            max_q = self.buy_dict[key][1]

            difference = reward + self.gamma * max_q - cur_q_value
            new_weights = [cur_weights[i] + 1.0*difference*features[i] for i in range(len(cur_weights))]
            new_weights_list.append(new_weights)

        for idx in range(len(self.buy_weights)):
            self.buy_weights[idx] = 0
            for l in new_weights_list:
                self.buy_weights[idx] += l[idx]
            self.buy_weights[idx] /= len(new_weights_list)


    # scores at the end of a game
    def terminal_val (self, g):
        state = g.state()
        playerscores = [state.score() for state in g.playerstates]
        score = state.score()
        if game.Game.over(g):
            if score >= max(playerscores):
                final_score = 100*(len(playerscores)) + score # reward for winning larger games
            else:
                final_score = -max(playerscores) + score # you lost, but you should still get some reward for being close
            self.update_q_values(final_score)
            return final_score

        return score /(g2f(g.counts)[3]) # score over remaining provinces

        pass


    def getAction(self, actions):
        '''if math.random() > 0.05:
            return random.choice(legalActions)

        return self.computeActionFromQValues(state)'''
        pass


    def make_buy_decision(self, decision):
        """
        Choose a card to buy
        """

        features = self.from_state_features_buy(decision)
        weights = self.buy_weights
        game = decision.game

        # All remaining cards that could be bought 
        choices = [card for card, count in game.card_counts.items() if count > 0]
        actions = [card for card in choices if card.cost <= decision.coins()]

        cur_q_value = sum(features[i]*weights[i] for i in range(len(features)))

        # Find the best action to take
        best_q_value = cur_q_value
        best_card = None
        for card in actions: #Already processed None
            new_counts = game.card_counts.copy()
            new_counts[card] -= 1

            state = decision.state()
            new_deck = state.hand + state.tableau + state.drawpile + (state.discard+(card,))

            new_features = g2f(new_counts)
            new_features.extend(c2f(new_deck))

            new_q_value = sum(new_features[i]*weights[i] for i in range(len(features)))
            if new_q_value >= best_q_value:
                best_q_value = new_q_value
                best_card = card

        # Add the action we take and corresponding Q-value to history to update later
        if (tuple(features), best_card) in self.buy_dict:
            self.buy_dict[(tuple(features), best_card, cur_q_value)][0] += 1
        else:
            self.buy_dict[(tuple(features), best_card, cur_q_value)] = [1, best_q_value]
        #print best_card, actions
        return best_card

    
    def make_act_decision(self, decision):
        """
        Choose an Action to play.
        By default, this chooses the action with the highest positive
        act_priority.
        """
        return None

    def make_trash_decision(self, decision):
        """
        The default way to decide which cards to trash is to repeatedly
        choose one card to trash until None is chosen.
        TrashDecision is a MultiDecision, so return a list.
        """
        return None

    def make_discard_decision(self, decision):
        return None