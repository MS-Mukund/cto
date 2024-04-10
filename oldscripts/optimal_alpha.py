import subprocess
import sys

'''
This script is used to find the optimal alpha value for the following settings: 
1. Number of observers = 18     -- done
2. Number of targets = {3, 9, 15}   -- done
3. Sensor range = 15            -- done
4. Target strategy = Randomised strategy        -- done
5. Alpha discretization = {0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0}   -- done
6. Number of runs = 30                  -- done
'''

for alpha in range(1, 10+1):
    for num_targets in [3, 9, 15]:
        for _ in range(30):
            subprocess.run(["python", "simulation.py", "no", "kmeans", str(0.1*alpha), str(num_targets)])

with open('a.txt', 'r+') as f:
    lines = f.readlines()
    vec = []
    m_sum = 0
    for i, line in enumerate(lines):
        if i % 90 == 0:
            m_sum /= 90
            vec.append(m_sum)
            m_sum = float(line)
        else:
            m_sum += float(line) 
    
    vec.append(m_sum/90)
    vec.pop(0)
    vec = [ round(x, 2) for x in vec ]

    f.write("final array: " + str(vec) + "\n")
