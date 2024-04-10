import subprocess
import itertools
import sys

command = ["python", "simulation.py"]
# command = ["python", "simulation.py", "kstep"]
strategies = ["kmeans", "explexpl", "memo", "onestep", "kstep", "randomise"]
NUM_OBS      = [2, 6, 10, 14, 18]
NUM_TARGET   = [3, 9, 15, 21, 27]
# TARG_SPEED = [0.2, 0.5, 0.8, 1.0, 1.2, 1.5]
# SENS_RAN     = [5, 10, 15, 20, 25]

# for strategy, obs, tar in itertools.product(strategies, NUM_OBS, NUM_TARGET):
# for obs, tar in itertools.product(NUM_OBS, NUM_TARGET):

    # final_com = command + [strategy, str(obs), str(tar)]
    # final_com = command + [str(obs), str(tar)]

open('random.txt', 'w').close()
for strategy in strategies:
    final_com = command + [strategy]
    for _ in range(30):
        subprocess.run(final_com)

with open('random.txt', 'a') as f:
    mean = sum( [int(line) for line in f.readlines()] ) / len(f.readlines())
    f.write(f"Following the {strategy}, 18 observers, 27 targets, the score is {mean}\n")

with open('means.txt', 'a') as f:
    f.write(f"{strategy} {mean}\n")
