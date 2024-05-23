import numpy as np
import matplotlib.pyplot as plt

import os
import sys
import subprocess

# Define the number of time steps
RUNS = 5016
for r in range(RUNS):
    f = str(1)
    subprocess.run(["python", "simulation.py", "ddpg", "1", "10", "15", "0.5", "1", f])


with open("ddv1.txt", "r") as f:
    rewards = f.readlines()
    computed_rewards = []
    for reward in rewards:
        computed_rewards.append(float(reward))

# Plot the average reward vs time steps
plt.plot([i for i in range(RUNS)], computed_rewards)
plt.xlabel("Timesteps")
plt.ylabel("Average Reward")
plt.plot("DDPG v1")
plt.savefig("ddv1.png")
