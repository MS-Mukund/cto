import numpy as np
import matplotlib.pyplot as plt

import os
import sys
import subprocess

# Define the number of time steps
RUNS = 50
for r in range(RUNS):
    f = str(1)
    subprocess.run(["python", "simulation.py", "randomise", "1", "10", "15", "0.5", "1", f])

Score = 0
with open('brlp.txt', 'r') as f:
    for line in f:
        Score += float(line.split()[-1])

Score /= RUNS
print(f"Average Score: {Score}")