import random
from RunSimulation import runSimulation

def evaluate_optimal_vs_random(numGames=200):
    winsOptimal = 0
    winsRandom = 0
    noWinner = 0
    totalTurns = 0

    for i in range(numGames):
        winner, turns = runSimulation(useOptimal=True, printing=False, maxTurns=300)
        totalTurns += turns

        if winner is None:
            noWinner += 1
        elif winner == 0:
            #OptimalAgent is player 0 and others are random
            winsOptimal += 1
        else:
            winsRandom += 1

    print(f"Games played: {numGames}")
    print(f"OptimalAgent wins: {winsOptimal}")
    print(f"Other (random) wins: {winsRandom}")
    print(f"No winner: {noWinner}")
    print(f"Optimal win rate (of games with a winner): "
          f"{winsOptimal / max(1, (winsOptimal + winsRandom))}")
    print(f"Average turns per game: {totalTurns / numGames}")

if __name__ == "__main__":
    evaluate_optimal_vs_random(numGames=200)
