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

def test2():
    print("test 2: random agents")

    numPlayers = 3
    env = LieGameEnv(numPlayers)

    agents = [RandomAgent(i) for i in range(numPlayers)]

    turn = 0
    max_turns = 200

    while not env.end and turn < max_turns:
        currPlayer = env.currPlayer
        obs = env.getObs(currPlayer)

        print(f"\nTurn {turn}: Player {currPlayer}'s turn")
        print(f"Hand size: {len(obs['hand'])}")
        print(f"Current rank: {obs['currRank']}")
        print(f"Awaiting challenge? {obs['awaitingChallenge']}")

        action = agents[currPlayer].getAction(obs)
        print("Action:", action)

        if action[0] == "PLAY":
            _, claimedRank, cards = action
            env.step(currPlayer, "PLAY", claimedRank, cards)
        else:
            #("CALL",) or ("NOCALL",)
            env.step(currPlayer, action[0])

        turn += 1

        if env.winner is not None:
            print(f"\nGame over in {turn} turns: winner is player {env.winner}")
        else:
            print(f"\nGame stopped after {turn} turns (no winner)")

        print("test 2 DONE\n")
def test3():
    print("test 3: optimal agent")
    #player 0 is the optimal agent, other player are random

    numPlayers = 3
    env = LieGameEnv(numPlayers)

    agents = []
    for i in range(numPlayers):
        if i == 0:
            agents.append(OptimalAgent(i))
        else:
            agents.append(RandomAgent(i))

    turn = 0
    max_turns = 200

    while not env.end and turn < max_turns:
        currPlayer = env.currPlayer
        obs = env.getObs(currPlayer)

        print(f"\nTurn {turn}: Player {currPlayer}'s turn")
        print(f"Hand size: {len(obs['hand'])}")
        print(f"Current rank: {obs['currRank']}")
        print(f"Awaiting challenge? {obs['awaitingChallenge']}")

        action = agents[currPlayer].getAction(obs)
        print("Action:", action)

        if action[0] == "PLAY":
            _, claimedRank, cards = action
            env.step(currPlayer, "PLAY", claimedRank, cards)
        else:
            env.step(currPlayer, action[0])

        turn += 1

    if env.winner is not None:
        print(f"\nGame over in {turn} turns: winner is player {env.winner}")
    else:
        print(f"\nGame stopped after {turn} turns (no winner)")
    print("test 3 DONE\n")

if __name__ == "__main__":
    test1()
    test2()
    test3()