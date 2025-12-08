from LieGameEnv import LieGameEnv
from agent import RandomAgent

def runSimulation():
    numPlayers = 3
    env = LieGameEnv(numPlayers)
    
    #make agents
    agents = []
    for i in range(numPlayers):
        agents.append(RandomAgent(i))

    print("Random Agents")
    turn = 0
    while not env.end and turn < 100:
        currPlayer = env.currPlayer
        obs = env.getObs(currPlayer)

        print(f"\Turn {turn}: Player {currPlayer}'s turn")
        print(f"Hand size: {len(obs['hand'])}")
        print(f"Current rank: {obs['currRank']}")

        action = agents[currPlayer].getAction(obs)
        print(f"Action: {action}")

        if action[0] == "PLAY":
            env.step(currPlayer, action[0], action[1], action[2])

        else: 
            env.step(currPlayer, action[0], None, None)
        turn+=1

    if env.winner is not None: 
        print(f"\nGame over: Winner is player {env.winner}")
    else: 
        print(f"\nGame stopped after {turn} turns")
    return env.winner
if __name__ == "__main__":
    runSimulation()
