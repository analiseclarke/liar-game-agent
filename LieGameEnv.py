import random 

class LieGameEnv:

    def __init__(self, numPlayers):
        self.numPlayers = numPlayers

        self.deck = None

        self.hands = None
        
        self.handSizes = [] 

        #what player's turn
        self.currPlayer = None
        #what rank (1-13)
        self.currRank = None

        #the pile (face down cards in the center)
        self.pile = None
        self.lastClaim = None #(playerID, claimedRank, claimedCount)
        self.lastPlayedCards = None #cards in the last claim

        #info about the last Lie (if any)
        #{challenger: id, result = truth/lie}
        self.lastLieOutcome = None 

        #placeholder 
        self.belief = []

        #is the game over (when a hand is empty)
        self.end = None
        #id of the winner (0 cards)
        self.winner = None
        #the last player made a claim, and now the next must decide to call or no call
        self.awaitingChallenge = None

        self.reset()

    #reset the game
    def reset(self):
        #deck is numbers 1 through 13 (4 of each), excludes jokers
        self.deck = []
        for i in range(1,14):
            for j in range(4):
                self.deck.append(i) #add 4 of each rank
        random.shuffle(self.deck) #shuffle the deck

        
        self.hands = [] #list of lists, hands[playerID] = [cards]
        for i in range(self.numPlayers):
            self.hands.append([]) #init empty list for each player

        #deal the cards
        #go through the deck in order and deal one card at a time to each player
        player = 0
        for i in range(len(self.deck)):
            self.hands[player].append(self.deck[i])
            player = (player + 1) % (self.numPlayers)
        
        self.handSizes = []
        for i in range(len(self.hands)):
            self.handSizes.append(len(self.hands[i]))
        
        #what player is up 
        self.currPlayer = 0
        #what rank (1-13)
        self.currRank = 1

        #the pile (face down cards in the center)
        self.pile = [] #none in the beginning
        self.lastClaim = None #(playerID, claimedRank, claimedCount)
        self.lastPlayedCards = []
        self.awaitingChallenge = False
        self.lastLieOutcome = None

        self.end = False
        self.winner = None

    #helper for who is the next player
    def nextPlayer(self, playerId):

        #returns next player's index, loops around
        return (playerId + 1) % self.numPlayers

    #checks if any player has 0 cards left
    #if so the game ends and that player is the winner
    def checkWin(self):
        for i in range(len(self.hands)):
            if len(self.hands[i]) == 0:
                self.end = True
                self.winner = i #i is the players id
                return
            
    #advance the rank from 1 - 13, looping around
    def advanceRank(self):
        self.currRank = (self.currRank % 13) + 1

    #method for getting the observation of what a single player can see
    #in dictionary format
    def getObs(self, playerId):
        return{
            #info specific to player
            "playerId": playerId,
            "hand": list(self.hands[playerId]),

            #info for everyone
            "handSizes": list(self.handSizes),
            "currPlayer": self.currPlayer,
            "currRank": self.currRank,
            "pileSize": len(self.pile),
            "lastClaim": self.lastClaim, #(playerId, rank, count) or none
            "lastPlayedCards": self.lastPlayedCards if self.lastPlayedCards else None,
            "lastLieOutcome": self.lastLieOutcome, #dictionary or none
            "end": self.end,
            "winner": self.winner,
            "awaitingChallenge": self.awaitingChallenge
        }


    def step(self, playerId, action, claimedRank = None, cards = None):
        #update the state based on an action
        #action is "CALL", "NOCALL" or "PLAY"

        if self.end: #check if the game is terminated
            return
        
        if action == "PLAY":
            #cards is a list of the cards being played
            player = self.currPlayer

            #remove cards from the players hand
            for c in cards:
                self.hands[player].remove(c)
            #update the size of the hand
            self.handSizes[player] = len(self.hands[player])

            #add the cards to the pile
            for c in cards:
                self.pile.append(c)

            #store the claim
            self.lastClaim = (player, claimedRank, len(cards))

            self.lastPlayedCards = list(cards) #the cards used in this claim for resolving lie

            #enter awaiting challenge, so the nect plauer must call or no call
            self.awaitingChallenge = True
            self.lastLieOutcome = None

            self.checkWin()
            return
        
        #here we are in awaiting challenge

        claimerId, claimedRank, claimedCount = self.lastClaim
        challengerId = self.nextPlayer(claimerId) #only the next player can challenge

        if action == "CALL":
     
            truthful = True
            for i in range(len(self.lastPlayedCards)):
                if self.lastPlayedCards[i] != claimedRank:
                    truthful = False
            
            if truthful:
                #challenger was wrong, they pick up the entire pile
                self.hands[challengerId].extend(self.pile)
                self.handSizes[challengerId] = len(self.hands[challengerId])
                result = "truth"
                print("\nplayer", challengerId, " is getting ", len(self.pile), " cards")
            else:
                #claim was a lie, claimed picks up the entire pile
                self.hands[claimerId].extend(self.pile)
                self.handSizes[claimerId] = len(self.hands[claimerId])
                result = "lie"
            
            #clear pile and claim, awaiting challenge is over
            self.pile = []
            self.lastClaim = None
            self.lastPlayedCards = []
            self.awaitingChallenge = False

            #record the outcome
            self.lastLieOutcome = {
                "challenger": challengerId,
                "result": result,

            }
            #the challenger becomes the next player to play
            self.currPlayer = challengerId
            self.advanceRank()

            self.checkWin()
            return
        #no challenge
        elif action == "NOCALL":
            self.lastLieOutcome = None

            #end awaiting challenge
            self.awaitingChallenge = False
            #now its the challengers turn to play
            self.currPlayer = challengerId
            self.advanceRank()

            self.checkWin()
            return
        else:
            print("error")

    def copyState(self):
        #deep copy of the current state
        state = {
            "hands": [list(hand for hand in self.hands)],
            "handSizes": list(self.handSizes),
            "currPlayer": self.currPlayer, 
            "currRank": self.currRank,
            "pile": list(self.pile),
            "lastClaim": self.lastClaim,
            "lastPlayedCards":list(self.lastPlayedCards) if self.lastPlayedCards else None,
            "awaitingChallenge": self.awaitingChallenge,
            "lastLieOutcome": dict(self.lastLieOutcome) if self.lastLieOutcome else None,
            "end": self.end,
            "winner": self.winner
        }
        return state
   


def main():
    env = LieGameEnv(numPlayers=3)
    print("Initial hands:", env.hands)
    print("initial obs player 0:", env.getObs(0))

    #player 0 plays 2 cards
    p0Cards = env.hands[0][:2] #take the first two cards
    env.step(playerId=0, action="PLAY", claimedRank=env.currRank, cards=p0Cards)

    print("\nafter player:")
    print("pile:", env.pile)
    print("lastClaim", env.lastClaim)
    print("awaitingChallenge:", env.awaitingChallenge)
    print("obs for player 1:", env.getObs(1))

    #player one decides not to call lie
    env.step(playerId=1, action="NOCALL")

    print("\nAfter player 1 no call:")
    print("currPlayer(should be 1):", env.currPlayer)
    print("currRank:", env.currRank)
    print("handSizes:", env.handSizes)
    print("obs for player 1:", env.getObs(1))

    p1Cards = env.hands[1][:3]
    env.step(playerId=1, action="PLAY", claimedRank=env.currRank, cards=p1Cards)

    print("\nafter player1:")
    print("pile:", env.pile)
    print("lastClaim", env.lastClaim)
    print("awaitingChallenge:", env.awaitingChallenge)
    print("obs for player 2:", env.getObs(2))

    env.step(playerId=2, action="CALL")
    print("\nAfter player 2 call:")
    print("currPlayer(should be 2):", env.currPlayer)
    print("currRank:", env.currRank)
    print("handSizes:", env.handSizes)
    print("obs for player 1:", env.getObs(1))




if __name__ == "__main__":
    main()