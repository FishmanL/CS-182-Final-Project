from dominiate import cards, dominion, game, players, combobot, derivbot
# from keras import models, layers, regularizers, preprocessing
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


class ComboLearner(combobot.ComboBot):
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
        a = g2f(game.counts)
        a.extend(c2f(deck))
        return a
        pass
    
    # features for which cards to permanently remove from the deck
    def from_state_features_trash (self, decision):
        game = decision.game
        state = decision.state()
        deck = decision.state().all_cards()
        a = g2f(game.counts)
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

    # scores at the end of a game
    def terminal_val (self, decision):
        state = decision.game.state()
        playerscores = [state.score() for state in decision.game.playerstates]
        score = state.score()
        if game.Game.over(decision.game):
            if score >= max(playerscores):
                return 100*(len(playerscores)) + score # reward for winning larger games
            else:
                return -max(playerscores) + score # you lost, but you should still get some reward for being close
        return score /(g2f(decision.game.counts)[3]) # score over remaining provinces

        pass
