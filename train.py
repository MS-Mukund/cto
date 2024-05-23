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

computed_rewards = []
with open("ddv1.txt", "r") as f:
    rewards = f.readlines()
    for reward in rewards:
        computed_rewards.append(float(reward))

# Plot the average reward vs time steps
mean10 = [sum(computed_rewards[i:i+10])/10 for i in range(5016-10)]

x = [i for i in range(5016)]
# plt.plot(x, computed_rewards, color='blue', label='ddpg v1')
plt.plot(x[10:], mean10, color='blue', label='ddpg v1')
plt.plot(x, [2.934*250 for i in range(5016)], color='red', linestyle='--', label='brlp benchmark')
plt.xlabel("Iteration no.")
plt.ylabel("Score observed")
plt.legend()
plt.title("DDPG v1")
plt.savefig("ddv1.png")
