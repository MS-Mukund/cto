'''
number of observers = {2, 6, 10, 14, 18}
number of targets = {3, 9, 15, 21, 27}
target speed = {0.5, 0.8, 1.0, 1.2}
sensor range = 15

Comparison: 
    a. Straight-line vs Random
    b. Controlled Random vs Random
    c. Controlled Random vs Straight-line   
'''

import subprocess

for prob in [0.0, 0.7, 1.0]:
    for speed in [0.5, 0.8, 1.0, 1.2]:
        for num_targets in [3, 9, 15, 21, 27]:
            for num_obs in [2, 6, 10, 14, 18]:
                for _ in range(30):
                    subprocess.run(["python", "simulation.py", "no", "explexpl", str(num_obs), str(num_targets), str(prob), str(speed) ])
                