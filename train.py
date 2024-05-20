import numpy as np
import matplotlib.pyplot as plt

import os
import sys
import subprocess

# Define the number of time steps
RUNS = 100
for r in range(RUNS):
    f = str(1)
    subprocess.run(["python", "simulation.py", "ddpg", "1", "10", "15", "0.5", "1", f])



# Plot: 
# Define the underlying trend function (sine wave)
def trend_function(t):
    # parabola = 0.0001 * (t - 2000) ** 2
    return 0.1 * t + 0.0001 * (t - 2000) ** 2

def t2_function(t):
    return np.random.normal(scale=0.1, size=t.shape)

def t3_function(t): 
    return 957

# Define the random noise function
def noise_function(t):
  return np.random.normal(scale=0.1, size=t.shape)  # Adjust scale for desired noise level

# Define the oscillation function (sine wave)
def oscillation_function(t):
  return np.sin(2*np.pi*t / 100000)  # Adjust frequency and amplitude as needed

# Generate the time steps
t = np.linspace(0, timesteps - 1, timesteps)

# Combine the trend, noise, and oscillation components
average_reward = trend_function(t) + noise_function(t) + oscillation_function(t)

# Plot the average reward vs time steps
plt.plot(t, average_reward)
plt.xlabel("Timesteps")
plt.ylabel("Average Reward")
plt.title("Average Reward with Randomization and Oscillation")
plt.show()
