from LieGameEnv import LieGameEnv
from agent import RandomAgent, OptimalAgent

def runSimulation(useOptimal=True, printing=True, maxTurns=200):
    numPlayers = 4
    env = LieGameEnv(numPlayers)
    
    #make agents
    agents = []
    optimal = useOptimal
    for i in range(numPlayers):
        if optimal:
            agents.append(OptimalAgent(i))
            optimal = False
        else:
            agents.append(RandomAgent(i))

    #print("Random Agents")
    turn = 0
    while not env.end and turn < 200:
        currPlayer = env.currPlayer
        obs = env.getObs(currPlayer)

        if printing:
            print(f"\nTurn {turn}: Player {currPlayer}'s turn")
            print(f"Hand size: {len(obs['hand'])}")
            print(f"Current rank: {obs['currRank']}")
            print(f"Awating challenge? {obs.get('awaitingChallenge', False)}")

        action = agents[currPlayer].getAction(obs)

        if printing:
            print(f"Action: {action}")

        if action[0] == "PLAY":
            #action: ("PLAY", claimedRank, cards)
            env.step(currPlayer, action[0], action[1], action[2])

        else: 
            #action is ("CALL",) or "NOCALL",
            env.step(currPlayer, action[0])
        turn+=1

    if env.winner is not None: 
        print(f"\nGame over: Winner is player {env.winner}")
    else: 
        print(f"\nGame stopped after {turn} turns")
    return env.winner, turn
if __name__ == "__main__":
    runSimulation(useOptimal=True)
