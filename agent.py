from LieGameEnv import LieGameEnv
import random

class Agent:
    """
    Abstract class for agents
    """
    def __init__(self, agentId, bluffThreshold=0.7):
        self.agentId =agentId
        self.bluffThreshold = bluffThreshold
        self.numPlayers = None
        self.rankProbs = None
        self.opponents = {}
        self.gameHistory = []
        self.hand = []



    def getAction(self, state):
        self.gameHistory.append(state)

        #if this is the beginning of the game, initialize
        if self.numPlayers is None:
            self.initialize(state)
       
        self.updateBelief(state)

        # either challenge (or not) or play a card
        if state.get('awaitingChallenge', False):
            return self.challenge(state)
        
        else:
            return self.play(state)
        
    def initialize(self, state):
        self.numPlayers = len(state['handSizes'])
        self.hand = state['hand'][:]
        self.rankProbs = {}

        #initialize probabilities
        for rank in range(1, 14):
            initialProb = 1.0 / self.numPlayers
            self.rankProbs[rank] = [initialProb] * self.numPlayers

        for player in range(self.numPlayers):
            if player != self.agentId:
                self.opponents[player]={
                    'bluffRate': 0.3,
                    'truths': 0.7,
                    'totalClaims': 0,
                    'numBluffs': 0,
                    'challenges': 0.3
                }
        
    def updateBelief(self, state):
        #update Bayesian beliefs
        newHand = state['hand']
        if newHand != self.hand:
            self.updateHand(newHand)
            self.hand = newHand[:]

        #update result
        if state.get('lastLieOutcome') and state.get('lastClaim'):
            self.updateAfterChallenge(
                state['lastClaim'],
                state['lastLieOutcome'],
                state.get('lastPlayedCards', [])
            )
        self.updateGameState(state)

    def updateHand(self, newHand):
        #update probabilities
        for rank in range(1, 14):
            numCardsInHand = newHand.count(rank)
            probs = self.rankProbs[rank]
        if numCardsInHand > 0:
            expected = probs[self.agentId] *4.0
            difference = numCardsInHand - expected
            if difference > 0: 
                diff = difference / 4.0
                probs[self.agentId] = min(1.0, probs[self.agentId] + diff)
                totalProbs = sum(probs) - probs[self.agentId]
                if totalProbs > 0:
                    scale = (1.0 - probs[self.agentId])/totalProbs
                    for p in range(self.numPlayers):
                        if p != self.agentId:
                            probs[p] *=scale

    def updateAfterChallenge(self, lastClaim, lastLieOutcome, revealedCards):
        claimerId, claimedRank, claimedCount = lastClaimresult = (lastLieOutcome['result'] =='truth')
        result = (lastLieOutcome['result'] == 'truth')
        if claimerId != self.agentId:
            opponent = self.opponents[claimerId]
            opponent['totalClaims'] += 1
            if result:
                opponent['truthRate'] +=1

            else:
                opponent['bluffCount'] += 1

            opponent['bluffRate'] = opponent['bluffCount'] / max(1, opponent['totalClaims'])
            opponent['truthRate'] = 1.0 - opponent['bluffRate']

            #update probabilities after cards a revealed
            if revealedCards:
                for card in revealedCards:
                    probs = self.rankProbs[card]
                if result:
                    for p in range(self.numPlayers):
                        if p== claimerId:
                            probs[p] = min(1.0, probs[p] * 1.5)
                        else: 
                            probs[p] = probs[p] *0.8
                else:
                    probs[claimerId] = max(0.0, probs[claimerId]*0.5)
                total = sum(probs)
                if total > 0:
                    for p in range(self.numPlayers):
                        probs[p] /= total

    def updateGameState(self, state):
        self.pileSize = state.get('pileSize', 0)
        self.currRank = state.get('currRank', 1)
        self.handSizes = state['handSizes'][:]

    def challenge(self, state):

    def play(self, state):
       


        

        
            
    
