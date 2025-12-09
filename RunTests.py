import random
from LieGameEnv import LieGameEnv
from agent import RandomAgent, OptimalAgent


def test1():
    """
    Basic environment test that checks:
        - deck dealt correctly
        - total cards in hand
        - PLAY / NOCALL / CALL produce the expected card counts
    """

    print("test 1")
    env = LieGameEnv(numPlayers=4)

    #check total cards dealt
    totalCards = sum(len(h) for h in env.hands)
    print("Total cards in hands:", totalCards)
    assert totalCards == 52, "Total cards should be 52"

    print("Initial hands:", env.hands)
    print("Initial handSizes:", env.handSizes)
    print("currPlayer:", env.currPlayer, "currRank:", env.currRank)

    #Let player 0 play 2 cards (truth/lie doesnt matter here)
    p0Cards = env.hands[0][:2]
    env.step(playerId=0, action="PLAY", claimedRank=env.currRank, cards=p0Cards)
    print("\nAfter P0 PLAY:")
    print("pile:", env.pile)
    print("lastClaim:", env.lastClaim)
    print("awaitingChallenge:", env.awaitingChallenge)
    print("handSizes:", env.handSizes)

    #Player 1 NOCALL
    env.step(playerId=1, action="NOCALL")
    print("\nAfter P1 NOCALL:")
    print("currPlayer (should be 1):", env.currPlayer)
    print("currRank:", env.currRank)
    print("pile:", env.pile)
    print("handSizes:", env.handSizes)

    #player 1 plays 3 cards, then player 2 CALLS

    p1Cards = env.hands[1][:3]
    env.step(playerId=1, action="PLAY", claimedRank=env.currRank, cards=p1Cards)
    print("\nAfter P1 PLAY:")
    print("pile:", env.pile)
    print("lastClaim:", env.lastClaim)
    print("awaitingChallenge:", env.awaitingChallenge)
    print("handSizes:", env.handSizes)

    env.step(playerId=2, action="CALL")
    print("\nAfter P2 CALL:")
    print("currPlayer (should be 2):", env.currPlayer)
    print("currRank:", env.currRank)
    print("pile (should be empty):", env.pile)
    print("handSizes:", env.handSizes)
    print("lastLieOutcome:", env.lastLieOutcome)

    print("test 1 DONE\n")


if __name__ == "__main__":
    test1()