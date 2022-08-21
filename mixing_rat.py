'''
number of observers = 10
number of targets = {3, 9, 15, 21, 27}
target speed = 1.0
sensor range = 15
targets straight-line movement percentages: 30%, 50%, 70%   
'''

import subprocess
from tabulate import tabulate

for prob in [0.3, 0.5, 0.7] :
    for num_targets in [3, 9, 15, 21, 27]:
        for _ in range(30):
            # 10 - observers, 1.0 - target speed, model - which explore-exploit setting
            subprocess.run(["python", "simulation.py", "no", "explexpl", '10', str(num_targets), str(prob) ])

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
