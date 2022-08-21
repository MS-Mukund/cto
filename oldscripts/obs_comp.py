'''
number of observers = {2, 6, 10, 14, 18}
number of targets = {3, 9, 15, 21, 27}
target speed = {0.5, 0.8, 1.0, 1.2}
sensor range = 15

Comparison: 
    a. Memorisation vs Explore-Exploit
    b. Onestep vs Explore-Exploit
    c. k-step vs Explore-Exploit
'''

import subprocess

for strategy in ['explexpl', 'memo', 'onestep', 'kstep']:
    for speed in [0.5, 0.8, 1.0, 1.2]:
        for num_targets in [3, 9, 15, 21, 27]:
            for num_obs in [2, 6, 10, 14, 18]:
                for _ in range(30):
                    subprocess.run(["python", "simulation.py", "no", strategy, str(num_obs), str(num_targets), str(speed) ])
                