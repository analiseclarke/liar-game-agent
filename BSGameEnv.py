import random 

class BSGameEnv:

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

        #beliefs
        self.belief = []

        #is the game over (when a hand is empty)
        self.end = False
        self.winner = None

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


def main():
    print("main")
    gameEnv = BSGameEnv(numPlayers=4)
    #print(gameEnv.deck)
    print(gameEnv.handSizes)


if __name__ == "__main__":
    main()