from LieGameEnv import LieGameEnv
import random


class RandomAgent:

    #if awaitingChallenge, randomly CALL or NOCALL (biased to NOCALL)
    #otherwise, PLAY some cards
    #if it has currRank: truthfully play them
    #else, bluff with 1 random card

    def __init__(self, agentId):
        self.agentId = agentId

    def getAction(self, obs):
        #challenge phase
        if obs.get("awaitingChallenge", False):
            #small bias towards not calling
            if random.random() < 0.3:
                return ("CALL",)
            else:
                return ("NOCALL",)
            
        #play phase
        hand = obs["hand"]
        currRank = obs["currRank"]

        #all cards of the current rank
        cardsOfRank = [c for c in hand if c == currRank]

        if currRank:
            #truth: play however many we have
            cardsToPlay = cardsOfRank
            claimedRank = currRank
        else:
            #bluff, play 1 random card but claim currRank
            card = random.choice(hand)
            cardsToPlay = [card]
            claimedRank = currRank

        return("PLAY", claimedRank, cardsToPlay)


class OptimalAgent:

    def __init__(self, agentId, bluffThreshold=0.7):
        self.agentId = agentId
        self.bluffThreshold = bluffThreshold #if P(lie) > threshold, then CALL
        self.numPlayers = None

        #rankProbs[rank][player] ~ P(player holds this rank)
        self.rankProbs = {}

        #per opponent stats
        #opponents[id] = {"truthCount": prior truth count, "bluffCount": prior bluff count, "claims": total claims}
        self.opponents = {}

        self.hand = []
        self.pileSize = 0
        self.currRank = 1
        self.handSizes = []

        self.bluffAggression = 1.0
        #self.minBluffCards = 1
        #self.maxBluffCards = 4

        self.gamePhase = 0
        self.myPosition = 0
        self.consecutiveTruths = 0
        self.lastActionWasBluff = False
        self.bluffSuccessHistory = []

    def getAction(self, state):
        #on first call, initialize beliefs
        if self.numPlayers is None:
            self.initialize(state)

        #update beliefs from new state
        self.updateBelief(state)

        if state.get("awaitingChallenge", False):
            return self.challenge(state)
        else:
            return self.play(state)
    
    def initialize(self, state):
        self.numPlayers = len(state["handSizes"])
        self.hand = state["hand"][:] #make a copy
        self.handSizes = state["handSizes"][:] #make a copy
        self.currRank = state["currRank"]

        #initialize probabilities
        #each rank equally likely to be with each player
        self.rankProbs = {}
        for rank in range(1, 14):
            self.rankProbs[rank] = [1.0 / self.numPlayers] * self.numPlayers
        
        for player in range(self.numPlayers):
            if player != self.agentId:
                self.opponents[player] = {
                    "truthCount": 5.0,
                    "bluffCount": 1.0,
                    "claims": 0,
                } #initialize with ~ "likely truthful but can bluff"

    def updateBelief(self, state):
        #update known local hand and rankProbs
        newHand = state["hand"]
        if newHand != self.hand:
            self.updateHand(newHand)
            self.hand = newHand[:] #make a copy

        #update game state facts
        self.pileSize = state.get("pileSize", 0)
        self.currRank = state.get("currRank", 1)
        self.handSizes = state["handSizes"][:]

        #update after a resolved CALL or NOCALL event
        lastOutcome = state.get("lastLieOutcome")
        lastClaim = state.get("lastClaim")
        if lastOutcome is not None and lastClaim is not None:
            self.updateAfterChallenge(lastClaim, lastOutcome)
    
    def updateHand(self, newHand):
        #Rough update
        #if we see we have lots of a rank, decrease that ranks probability for others

        self.hand = newHand[:]
        for rank in range(1, 14):
            countInHand = newHand.count(rank)
            probs = self.rankProbs[rank]

            #if we hold some of this rank, we know others hold fewer
            if countInHand > 0:
                #set our probability up, scale down others
                probs[self.agentId] = min(1.0, 0.2 * countInHand)
                totalOther = sum(probs[p] for p in range(self.numPlayers) if p != self.agentId)
                if totalOther > 0:
                    scale = (1.0 - probs[self.agentId]) / totalOther
                    for p in range(self.numPlayers):
                        if p != self.agentId:
                            probs[p] *= scale
            
            self.rankProbs[rank] = probs

    
    def updateAfterChallenge(self, lastClaim, lastLieOutcome):
        #update the opponent bluff rate after a resolved CALL
        #lastClaim: (claimerId, claimedRank, claimedCount)
        #lastLieOutcome: {"challenger": id, "result": truth or lie}

        claimerId, claimedRank, claimedCount = lastClaim
        resultTruth = (lastLieOutcome["result"] == "truth")

        if claimerId == self.agentId:
            #We don't update our own opponent model here
            return
        
        opp = self.opponents.get(claimerId)
        if opp is None:
            return
        
        opp["claims"] += 1
        if resultTruth:
            opp["truthCount"] += 1.0
        else:
            opp["bluffCount"] += 1.0

    
    def challenge(self, state):
        #decide whether to CALL or NOCALL
        #based on: opponent's estimated bluff rate (Bayesian)
        #and Monte Carlo check of feasibility

        lastClaim = state["lastClaim"]
        claimerId, claimedRank, claimedCount = lastClaim

        #get estimated bluff probability
        opp = self.opponents.get(claimerId)
        if opp is not None:
            truthCount = opp["truthCount"]
            bluffCount = opp["bluffCount"]

            truthRate = truthCount / (truthCount + bluffCount)
            bluffRate = 1.0 - truthRate
        else:
            bluffRate = 0.3

        feasibilityEst = self.estimateFeasibility(state, claimerId, claimedRank, claimedCount)

        #if bluff rate is high or feasibility is very low, we CALL
        pLie = 0.5 * bluffRate + 0.5 * (1.0 - feasibilityEst)

        if pLie > self.bluffThreshold:
            return ("CALL",)
        else:
            return ("NOCALL",)
    
    def estimateFeasibility(self, state, claimerId, claimedRank, claimedCount, numSamples=200):
        #Monte Carlo heuristic
        

        #total copies of claimedRank in deck
        TOTAL = 4

        #how many of that rank we know we have
        myCount = state["hand"].count(claimedRank)

        #how many of that rank are not available to others
        remaining = max(0, TOTAL - myCount)

        if remaining < claimedCount:
            #impossible for others to have that many
            return 0.0
        
        probs = self.rankProbs[claimedRank][:]

        success = 0
        for i in range(numSamples):
            #alloc[p] = how many copies of claimedRank player p gets
            alloc = [0] * self.numPlayers

            #for each remaining copy, randomly choose which player recieves it,
            #with probability proportional to probs[p]

            for j in range(remaining):
                totalWeight = sum(probs)
                #if totalWeight is 0, return neutral value
                if totalWeight <= 0:
                    return 0.5
                
                r = random.random() * totalWeight
                cumulative = 0.0
                chosen = 0
                for p, w in enumerate(probs):
                    cumulative += w
                    if r <= cumulative:
                        chosen = p
                        break
                alloc[chosen] += 1
            
            #check if claimer got at least claimedCount copies in this sample
            if alloc[claimerId] >= claimedCount:
                success += 1
        
        #success / numSamples is the fraction of smaples in which the claim is feasible
        return success / numSamples if numSamples > 0 else 0.5
    

    def play(self, state):
        #Decide which cards to PLAY and what rank to CLAIM

        """
        Logic:
        Decide whether to bluff based on the aggressiveness of the other
        players and the stage of the game
        """

        hand = state["hand"]
        currRank = state["currRank"]
        

        #Find all cards matchinf the current target rank
        currCards = [c for c in hand if c == currRank]

        #compute an average bluff rate across all opponents
        #to see how dangerous it is to bluff
        bluffRates= self.getOpponentBluffRate()
        avgBluffRate = sum(bluffRates) / len(bluffRates) if bluffRates else 0.5

        shouldBluff, bluffCards, claimedRank = self.decideBluff(state, currCards, currRank, avgBluffRate)
        if shouldBluff:
            cardsToPlay = bluffCards
            claimedRank = currRank
            self.lastActionWasBluff= True
        else:
            cardsToPlay = currCards[:]
            claimedRank = currRank
            self.lastActionWasBluff = False
            if cardsToPlay:
                self.consecutiveTruths +=1
            else: 
                shouldBluff, cardsToPlay, claimedRank = self.forcedBluff(state, currRank)
                self.lastActionWasBluff = shouldBluff

        return("PLAY", claimedRank, cardsToPlay)
    
    def updateGame(self, state):
        totalCards = sum(state["handSizes"])
        if totalCards > 39:
            self.gameState = 0
        elif totalCards > 13:
            self.gameState = 1
        else:
            self.gameStage = 2

        self.pileSize = state.get("pileSize", 0)

        #track the last 10 bluffs
        if len(self.bluffSuccessHistory) > 10:
            self.bluffSuccessHistory.pop(0)

    def decideBluff(self, state, currCards, currRank, avgBluffRate):
        hand = state["hand"]
        handSize = len(hand)

        hasCards = len(currCards)>0
        if hasCards:
            truthProb = 0.8

        else: 
            truthProb = 0.0
        pileRisk = self.pileSize / 20.0
        truthProb +=0.3* (1-pileRisk)

        bluffReward = (1.0 - avgBluffRate) *0.2
        truthProb -=bluffReward

        #game stage
        if self.gamePhase == 0:
            truthProb += 0.1
        elif self.gamePhase == 2:
            truthProb -=0.2

        if self.bluffSuccessHistory:
            recentSuccessRate = sum(self.bluffSuccessHistory) / len(self.bluffSuccessHistory)

            if recentSuccessRate > 0.7:
                truthProb -=0.1
            elif recentSuccessRate < 0.3:
                truthProb += 0.1
        shouldBluff = random.random() > min(0.95, max(0.05, truthProb))

        if not shouldBluff or hasCards:
            return False, [], currRank
        
        bluffCards = self.chooseBluffCards(hand, currRank, avgBluffRate)
        claimedRank = currRank

        return True, bluffCards, claimedRank
    
    def chooseBluffCards(self, hand, currRank, avgBluffRate):
        if self.gamePhase == 0:
            bluffSize = random.randint(1, min(2, len(hand)))
        elif self.gamePhase == 2:
            bluffSize = random.randint(1, min(4, len(hand)))
        else:
            bluffSize = random.randint(1, (min(3, len(hand))))

        if avgBluffRate < 0.3:
            bluffSize = min(bluffSize + 1, len(hand), 4)
        elif avgBluffRate > 0.7:
            bluffSize = max(bluffSize -1, 1)
        bluffCards = random.sample(hand, bluffSize)
        return bluffCards
    
    def forcedBluff(self, state, currRank):
        hand = state["hand"]
        bluffRate = self.getOpponentBluffRate()
        avgBluffRate = sum(bluffRate) / len(bluffRate) if bluffRate else 0.5

        bluffCards =self.chooseBluffCards(hand, currRank, avgBluffRate)

        return True, bluffCards, currRank
    
    def getOpponentBluffRate(self):
        oppBluffRates = []
        for pid, opp in self.opponents.items():
            if opp["claims"] > 0:
                truthCount = opp["truthCount"]
                bluffCount = opp["bluffCount"]

                perceivedBluffRate = bluffCount / (truthCount + bluffCount) if (truthCount + bluffCount) > 0 else 0.3
                bluffRate = min(1.0, perceivedBluffRate *1.5)
                oppBluffRates.append(bluffRate)
        return oppBluffRates
    
    def updateAfterChalenge(self, lastClaim, lastLieOutcome):
        claimerId, claimedRank, claimedCount = lastClaim
        resultTruth = (lastLieOutcome["result"] == "truth")
        if claimerId == self.agentId and self.lastActionWasBluff:
            bluffSuccess = (lastLieOutcome["challenger"] is None) or (lastLieOutcome["result"] =="lie")
            self.bluffSuccessHistory.append(1 if bluffSuccess else 0)
            self.lastActionWasBluff = False

        if claimerId != self.agentId:
            opp = self.opponents.get(claimerId)
            if opp:
                opp["claimes"] += 1
                if resultTruth:
                    opp["truthCount"] += 1.0
                else:
                    opp["bluffCount"] +=1.0



            
    

        
