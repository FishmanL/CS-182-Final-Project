import cards
import dominion
import game
from game import ActDecision, TrashDecision, BuyDecision, DiscardDecision
import copy
import players
import combobot
import derivbot
# from keras import models, layers, regularizers, preprocessing
import csv
from operator import itemgetter
import random

# each index corresponds to the amount of one specific card
canonical_order = [game.curse, game.estate, game.duchy, game.province, game.copper, game.silver, game.gold,
                   cards.village, cards.cellar, cards.smithy, cards.festival, cards.market, cards.laboratory,
                   cards.chapel, cards.warehouse, cards.council_room, cards.militia, cards.moat]


# converts from an array of cards into an array of canonical numbered cards
def c2f (cards):
    currarr = [0.0 for _ in canonical_order]
    for c in cards:
        currarr[canonical_order.index(c)] += 1.0 / (len(cards))
    return currarr

# converts from a dict of cards into an array of canonical numbered cards
def g2f (carddict):
    currarr = [0.0 for _ in canonical_order]
    for (c, count) in carddict.items():
        currarr[canonical_order.index(c)] = count / (sum([value for k, value in carddict.items()]))
    return currarr


class ComboLearner(players.AIPlayer):
    def __init__(self, loadfile=None, epsilon=0.25):
        if loadfile is None:
            self.buy_weights = [0 for _ in range((len(canonical_order) * 2) + 2)]
            self.trash_weights = [0 for _ in range((len(canonical_order) * 3))]
            self.discard_weights = [0 for _ in range((len(canonical_order) + 3))]
            self.play_weights = [0 for _ in range((len(canonical_order) + 3))]
            self.weights = [self.buy_weights, self.trash_weights, self.discard_weights, self.play_weights]
        else:
            self.loadweights(filename=loadfile)
            self.weights = [self.buy_weights, self.trash_weights, self.discard_weights, self.play_weights]

        self.buy_dict = dict()
        self.play_dict = dict()
        self.trash_dict = dict()
        self.discard_dict = dict()

        self.epsilon = epsilon
        self.gamma = 0.5
        self.name = "Q-learner"
        players.AIPlayer.__init__(self)

    """
    4 separate q learners
    """
    # gets four sets of weights from a csv file, if it exists
    def loadweights(self, filename = "weights.csv"):
        with open(filename, "r") as file:
            reader = csv.reader(file)
            introws = [[float(r) for r in row] for row in reader]
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
    def from_state_features_buy (self, decision, game = None, state = None):
        if game is None:
            game = decision.game
        if state is None:
            state = decision.state()
        deck = state.all_cards()
        a = g2f(game.card_counts)
        a.extend(c2f(deck))
        a.extend([state.buys, state.hand_value()])
        return a
        pass
    
    # features for which cards to permanently remove from the deck
    def from_state_features_trash (self, decision, game = None, state = None):
        if game is None:
            game = decision.game
        if state is None:
            state = decision.state()
        deck = state.all_cards()
        a = g2f(game.card_counts)
        a.extend(c2f(deck))
        a.extend(c2f(state.hand))
        return a
        pass

    # features for playing a card (action) from hand
    def from_state_features_play (self, decision, state = None):
        if state is None:
            state = decision.state()
        hand = state.hand
        a = c2f(hand)
        a.extend([state.actions, state.buys, state.hand_value()])
        return a
        pass

    # features for which cards to discard from your hand
    def from_state_features_discard (self, decision):
        game = decision.game
        state = decision.game.state()
        a = c2f(state.hand)
        a.extend([state.actions, state.buys, state.hand_value()])
        return a
        pass

    # general function for updating the q val at a given decision point
    def update_one_qval(self, reward, cur_weights, cur_dict):
        new_weights_list = list()

        for key in cur_dict:
            features = list(key[0])
            action = key[1]
            cur_q_value = key[2]
            count = cur_dict[key][0]
            max_q = cur_dict[key][1]

            difference = reward - cur_q_value
            new_weights = [cur_weights[i] + 0.5*difference*features[i] for i in range(len(cur_weights))]
            new_weights_list.append(new_weights)

        for idx in range(len(cur_weights)):
            cur_weights[idx] = 0
            for l in new_weights_list:
                cur_weights[idx] += l[idx]
            cur_weights[idx] /= (len(new_weights_list) + 1)

        # normalize the weights from 0 to 1
        s = sum(map(abs,cur_weights)) + 0.0001
        cur_weights = [i/s for i in cur_weights]
        return cur_weights

    # I made this into the general function above bc we kept reusing it,
    # but if it needs to be independent I saved the original code, so just lmk
    # if the general thing doesn't work and I can fix it as needed

    # def update_q_values(self, reward):
    #     cur_weights = self.buy_weights
    #     new_weights_list = list()

    #     for key in self.buy_dict:
    #         features = list(key[0])
    #         action = key[1]
    #         cur_q_value = key[2]
    #         count = self.buy_dict[key][0]
    #         max_q = self.buy_dict[key][1]

    #         difference = reward - cur_q_value
    #         new_weights = [cur_weights[i] + 0.5*difference*features[i] for i in range(len(cur_weights))]
    #         new_weights_list.append(new_weights)

    #     for idx in range(len(self.buy_weights)):
    #         self.buy_weights[idx] = 0
    #         for l in new_weights_list:
    #             self.buy_weights[idx] += l[idx]
    #         self.buy_weights[idx] /= len(new_weights_list)

    #     # normalize the weights from 0 to 1
    #     s = sum(self.buy_weights)
    #     self.buy_weights = [i/s for i in self.buy_weights]

    # update the q-vals for all four decision points
    def update_q_values(self, reward):
        self.buy_weights = self.update_one_qval(reward, self.buy_weights, self.buy_dict)
        self.play_weights = self.update_one_qval(reward, self.play_weights, self.play_dict)

        if self.trash_dict != {}:
            self.trash_weights = self.update_one_qval(reward, self.trash_weights, self.trash_dict)
        if self.discard_dict != {}:
            self.discard_weights = self.update_one_qval(reward, self.discard_weights, self.discard_dict)

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
        raise ValueError('Reached terminal_val without it being terminal state')
        pass

    # return the best card and its corresponding q-value
    def best_choice(self, game, decision, cur_q_value, actions, features, weights):

        best_q_value = cur_q_value
        best_card = None
        for card in actions: # Already processed None
            ngame = game.simulated_copy()
            if decision is ActDecision:
                state = ngame.state()
                if card is None:
                    newgame = ngame.change_current_state(
                        delta_actions=-state.actions
                    )
                else:
                    newgame = card.perform_action(ngame.current_play_action(card))
                features = self.from_state_features_play(ActDecision(newgame))
                weights = self.play_weights

            if decision is BuyDecision:
                state = ngame.state()
                if card is None:
                    newgame = ngame.change_current_state(
                        delta_buys=-state.buys
                    )
                else:
                    newgame = ngame.remove_card(card).replace_current_state(
                        state.gain(card).change(delta_buys=-1, delta_coins=-card.cost)
                    )
                features = self.from_state_features_buy(BuyDecision(newgame))
                weights = self.buy_weights

            new_q_value = sum([features[i]*weights[i] for i in range(len(features))])
            if new_q_value >= best_q_value:
                best_q_value = new_q_value
                best_card = card

        return (best_q_value, best_card)

    # return an ordered list of the best cards and their corresponding q-values
    def best_choices_ordered(self, game, decision, actions, features, weights):
        options = []
        for card in actions:
            ngame = game.simulated_copy()
            if decision is TrashDecision:
                state = ngame.state()

                state = state.trash_card(card)
                newgame = ngame.replace_current_state(state)
                features = self.from_state_features_trash(TrashDecision(newgame))
                weights = self.trash_weights
            if decision is DiscardDecision:
                state = ngame.state()
                state = state.discard_card(card)
                newgame = ngame.replace_current_state(state)
                features = self.from_state_features_discard(DiscardDecision(newgame))
                weights = self.discard_weights

            qval = sum([features[i]*weights[i] for i in range(len(features))])
            options.append((card, qval))

        # sort in order of highest q-value to lowest q-value
        options = sorted(options, key=itemgetter(1), reverse=True)
        return options

    def make_buy_decision(self, decision):
        """
        Choose a card to buy
        """

        features = self.from_state_features_buy(decision)
        weights = self.buy_weights
        game = decision.game

        # All remaining cards that could be bought 
        actions = decision.choices()

        cur_q_value = sum([features[i]*weights[i] for i in range(len(features))])

        # with probability epsilon, randomly select action
        if random.random() < self.epsilon:
            actions = [random.choice(actions)]
        (best_q_value, best_card) = self.best_choice(game, decision, cur_q_value, actions, features, weights)

        # Add the action we take and corresponding Q-value to history to update later
        if (tuple(features), best_card) in self.buy_dict:
            self.buy_dict[(tuple(features), best_card, cur_q_value)][0] += 1
        else:
            self.buy_dict[(tuple(features), best_card, cur_q_value)] = [1, best_q_value]
        return best_card

    
    def make_act_decision(self, decision):
        """
        Choose an Action to play.
        By default, this chooses the action with the highest positive
        act_priority.
        """

        features = self.from_state_features_play(decision)
        weights = self.play_weights
        game = decision.game

        actions = decision.choices()

        if random.random() < self.epsilon:
            actions = [random.choice(actions)]

        cur_q_value = sum([features[i]*weights[i] for i in range(len(features))])

        (best_q_value, best_card) = self.best_choice(game, decision, cur_q_value, actions, features, weights)

        # Add the action we take and corresponding Q-value to history to update later
        if (tuple(features), best_card) in self.play_dict:
            self.play_dict[(tuple(features), best_card, cur_q_value)][0] += 1
        else:
            self.play_dict[(tuple(features), best_card, cur_q_value)] = [1, best_q_value]
        return best_card

    def make_trash_decision(self, decision):
        """
        The default way to decide which cards to trash is to repeatedly
        choose one card to trash until None is chosen.
        TrashDecision is a MultiDecision, so return a list.
        """
        features = self.from_state_features_trash(decision)
        weights = self.trash_weights
        game = decision.game

        # All remaining cards that could be trashed 
        actions = decision.choices()

        if actions == []:
            return []

        # sometimes, just choose randomly
        if random.random() < self.epsilon:
            random_selection = True
            if not decision.max:
                decision.max = len(actions)
            if not decision.min:
                decision.min = 0
            actions = random.sample(actions, min(random.randint(decision.min, decision.max), len(actions)))
        else:
            random_selection = False

        cur_q_value = sum([features[i]*weights[i] for i in range(len(features))])

        best_options = self.best_choices_ordered(game, decision, actions, features, weights)
        # select best card options

        if random_selection:
            selections = best_options
        else:
            selections = []
            for i in range(min(decision.max,len(best_options))):
                if best_options[i][1] >= cur_q_value or i < decision.min:
                    selections.append(best_options[i])
                else:
                    break

        # Add the actions we take and corresponding Q-value to history to update later
        for (card, value) in selections:
            if (tuple(features), card) in self.trash_dict:
                self.trash_dict[(tuple(features), card, cur_q_value)][0] += 1
            else:
                self.trash_dict[(tuple(features), card, cur_q_value)] = [1, value]

        best_cards = [x[0] for x in selections]
        return best_cards

    def make_discard_decision(self, decision):
        features = self.from_state_features_discard(decision)
        weights = self.discard_weights
        game = decision.game

        # All remaining cards that could be discarded 
        actions = decision.choices()

        if actions == []:
            return []

        # sometimes, just choose randomly
        if random.random() < self.epsilon:
            random_selection = True
            if not decision.max:
                decision.max = len(actions)
            if not decision.min:
                decision.min = 0
            actions = random.sample(actions, min(random.randint(decision.min, decision.max), len(actions)))
        else:
            random_selection = False

        cur_q_value = sum([features[i]*weights[i] for i in range(len(features))])

        best_options = self.best_choices_ordered(game, decision, actions, features, weights)

        if random_selection:
            selections = best_options
        else:
            selections = []
            for i in range(min(decision.max,len(best_options))):
                if best_options[i][1] >= cur_q_value or i < decision.min:
                    selections.append(best_options[i])
                else:
                    break

        # Add the actions we take and corresponding Q-value to history to update later
        for (card, value) in selections:
            if (tuple(features), card) in self.discard_dict:
                self.discard_dict[(tuple(features), card, cur_q_value)][0] += 1
            else:
                self.discard_dict[(tuple(features), card, cur_q_value)] = [1, value]

        best_cards = [x[0] for x in selections]
        return best_cards
