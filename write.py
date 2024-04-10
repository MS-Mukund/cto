import random

target_pos = [(random.uniform(0, 600), random.uniform(0, 600))
              for _ in range(9)]

obs_pos = [ (random.uniform(0, 600), random.uniform(0, 600))
           for _ in range(18) ]

for targ in target_pos:
    print(f'{targ[0]} {targ[1]}') 
for obs in obs_pos:
    print(f'{obs[0]} {obs[1]}')
