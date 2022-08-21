import subprocess

for strategy in ['explexpl', 'memo', 'onestep', 'kstep']:
                for _ in range(30):
                    subprocess.run(["python", "simulation.py", "no", strategy ])

with open('a.txt', 'r') as f:
    i = 0
    sum = 0
    for line in f.readlines():
        if i % 30 == 0:
            sum /= 30
            print(sum)
            sum = float(line)
        else:
            sum += float(line)

        i += 1
    
    sum /= 30
    print(sum)
    