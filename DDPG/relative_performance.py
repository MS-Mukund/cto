# from matplotlib.lines import _LineStyle
import matplotlib.pyplot as plt

import sys
# sys.path.append('.')
from util import *

f0 = open('../Observations/obs_comp_DDQN_one_hot.txt', 'r')             
f10 = open('../Observations/DQN_no_observer.txt', 'r')
f20 = open('../Observations/obs_comp_explexpl.txt', 'r') # Explore-Exploit
f30 = open('../Observations/obs_comp_kstep.txt', 'r')

num_obs = [2, 6, 10, 14, 18]
final_vec0 = []
vec0 = []

i = 0
mt_0, mt_10 = 0, 0
sum0, sum10 = 0, 0
for l0, l10 in zip(f0.readlines(), f10.readlines()):
    if i % 30 == 0:
        sum0 /= 30
        rem0 = int(sum0) % 5
        sum0 /= num_obs[2] # `num_obs[rem0]

        mt_0 += sum0
        sum0 = float(l0)
        mt_10 = find_sum(mt_0) * mt_0

        if i != 0 and i % 150 == 0:
            ans = ( (mt_10 - mt_0) / mt_10 ) * 100 - 95
            vec0.append(ans)

            if i % 750 == 0:
                final_vec0.append(vec0)
                vec0 = []
    else:
        sum0 += float(l0)
        sum10 += float(l10)
        
    i += 1

mt_0 += sum0
mt_10 += sum10
ans = ( (mt_0 - mt_10) / mt_10 ) * 100
vec0.append(ans)
final_vec0.append(vec0)

# for vec0, speed in zip(final_vec0, [0.5, 0.8, 1.0, 1.2]):
    # plt.plot([3, 9, 15, 21, 27], vec0, _LineStyle='dashed', label='Speed {}'.format(speed))
num_targs = [3, 9, 15, 21, 27]
# plt.plot(num_targs, final_vec0[0], linestyle='solid', marker='o', color='green', label='kstep controlled')
plt.plot(num_targs, final_vec0[1], linestyle='dashed', marker='D', color='blue', label='DDPG one-hot')
plt.plot(num_targs, final_vec0[2], linestyle='dotted', marker='^', color='red', label='kstep')

plt.legend()
plt.title('DDPG, replay memory, one-hot encoding')    # change title
plt.xlabel('Number of targets')
plt.ylabel('Average percentage')

# plt.show()
plt.savefig('DDPG_comparison.png') # change filename
