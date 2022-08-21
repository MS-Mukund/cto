
'''
number of observers = 10
number of targets = {3, 9, 15, 21, 27}
target strategy = randomised
target speed = 1.0
sensor range = 15
Models: 0-1 model, 0-.5-1 model and (1/(num_targs+1))**2 model 
'''

import subprocess
import sys
from tabulate import tabulate

for model in range(3):
    for num_targets in [3, 9, 15, 21, 27]:
        for _ in range(30):
            # 10 - observers, 1.0 - target speed, model - which explore-exploit setting
            subprocess.run(["python", "simulation.py", "no", "explexpl", '10', str(num_targets), str(model) ])

with open('a.txt', 'r+') as f:
    lines = f.readlines()
    final_vec = [[3, 9, 15, 21, 27]]
    vec = []
    m_sum = 0
    for i, line in enumerate(lines):
        if i % 30 == 0:
            m_sum /= 30
            if i != 0:
                vec.append(m_sum)
                if i % 150 == 0:
                    final_vec.append(vec)
                    vec = []
            m_sum = float(line)
        else:
            m_sum += float(line) 
    
    vec.append(m_sum/30)
    final_vec.append(vec)
    final_vec = [ [ round(x, 2) for x in l ] for l in final_vec ] 

    f.write("final array: " + str(final_vec) + "\n")
    print(tabulate(final_vec, tablefmt='fancy_grid'))
