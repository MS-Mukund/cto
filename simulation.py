import random
import sys
import os
import numpy as np

#files
import constant as ct
import update as up
import misc 

from DDPG.ddpg import DDPG
import argparse
import torch

# Model as a RL problem
# Reward - updated at each iteration, based on ALL(targets + observers within observer range) 
# policy - observer strategy (observers don't communicate with each other, observers can see all objects within their range)
# state - position of all objects (targets, observers) within observer's range at a given time step
# action - observer's movement at a given time step
# no. of states - done based on target's position and if any other observer is observing the target - total_num_target*100
# no. of actions - choosing the new angle (360 * 100)

strategy = sys.argv[1] if len(sys.argv) >= 2 else 'naive'
ct.ALPHA = float(sys.argv[2]) if len(sys.argv) >= 3 else 1
ct.NUM_OBS[-1] = int(sys.argv[3]) if len(sys.argv) >= 4 else ct.NUM_OBS[-1]
ct.NUM_TARGET[-1] = int(sys.argv[4]) if len(sys.argv) >= 5 else ct.NUM_TARGET[-1]
ct.TARG_SPEED[3] = float(sys.argv[5]) if len(sys.argv) >= 6 else ct.TARG_SPEED[3]
ct.MODEL = int(sys.argv[6]) if len(sys.argv) >= 7 else ct.MODEL
FRACT = (int)(sys.argv[7]) if len(sys.argv) >= 8 else 1
# # command-line arguments
# if len(sys.argv) >= 8  and sys.argv[7].lower() == 'no':
#     # print(f"bye alpha = {ct.ALPHA}")
#     # exit()
#     ct.USE_PYGAME = False
# else:
#     import pygame as pg
    
ct.TOTAL_TIME = 250

factor = 4
ct.AR_WID *= factor
ct.AR_HEI *= factor
ct.TARG_SPEED *= factor
ct.OBS_SPEED *= factor
ct.SENS_RAN[2] = 25
ct.TARG_RAD *= factor
ct.OBS_RAD *= factor
ct.USE_PYGAME = False


if ct.USE_PYGAME == True:
    pg.init()
    window = pg.display.set_mode((ct.AR_WID, ct.AR_HEI)) 
    pg.display.set_caption("Cooperative Target Observation")

# Creating targets
target_pos = [(random.uniform(0, ct.AR_WID), random.uniform(0, ct.AR_HEI))
              for _ in range(ct.NUM_TARGET[-1])]

# posi = open('write.txt', 'r+')
# lines = posi.readlines()

# target_pos = []
# for i in range(len(lines)):
#     if i < ct.NUM_TARGET[-1]:
#         a, b = lines[i].strip('\n').split(' ')
#         target_pos.append((float(a), float(b)))
target_dest = target_pos.copy()

# print(target_pos)
targ = []
if ct.USE_PYGAME == True:
    targ = [pg.draw.circle(pg.display.get_surface(), ct.RED, target, ct.TARG_RAD)
        for target in target_pos]

# Creating observers
obs_pos = [ (random.uniform(0, ct.AR_WID), random.uniform(0, ct.AR_HEI))
           for _ in range(ct.NUM_OBS[-1]) ]
# with open('obs_pos.txt', 'w') as f:
    # for obs in obs_pos:
        # f.write(f"{obs[0]} {obs[1]}\n")
with open('obs_pos.txt', 'r') as f:
    index = 0
    for line in f:
        a, b = line.strip('\n').split(' ')
        obs_pos[index] = (float(a), float(b))
        index += 1

# obs_pos = []
# for i in range(ct.NUM_TARGET[-1], len(lines)):
#     if i < ct.NUM_OBS[-1] + ct.NUM_TARGET[-1]:
#         a, b = lines[i].strip('\n').split(' ')
#         obs_pos.append((float(a), float(b)))
#         print(obs_pos[-1][0], obs_pos[-1][1])
obs_dest = obs_pos.copy()
obsvr = []
if ct.USE_PYGAME == True:
    obsvr = [pg.draw.circle(pg.display.get_surface(), ct.GREEN, obs, ct.OBS_RAD)
         for obs in obs_pos]

# parser = argparse.ArgumentParser(description='PyTorch on TORCS with Multi-modal')

# parser.add_argument('--mode', default='train', type=str, help='support option: train/test')
# parser.add_argument('--env', default='Pendulum-v0', type=str, help='open-ai gym environment')
# parser.add_argument('--hidden1', default=400, type=int, help='hidden num of first fully connect layer')
# parser.add_argument('--hidden2', default=300, type=int, help='hidden num of second fully connect layer')
# parser.add_argument('--rate', default=0.001, type=float, help='learning rate')
# parser.add_argument('--prate', default=0.0001, type=float, help='policy net learning rate (only for DDPG)')
# parser.add_argument('--warmup', default=100, type=int, help='time without training but only filling the replay memory')
# parser.add_argument('--discount', default=0.99, type=float, help='')
# parser.add_argument('--bsize', default=64, type=int, help='minibatch size')
# parser.add_argument('--rmsize', default=6000000, type=int, help='memory size')
# parser.add_argument('--window_length', default=1, type=int, help='')
# parser.add_argument('--tau', default=0.001, type=float, help='moving average for target network')
# parser.add_argument('--ou_theta', default=0.15, type=float, help='noise theta')
# parser.add_argument('--ou_sigma', default=0.2, type=float, help='noise sigma') 
# parser.add_argument('--ou_mu', default=0.0, type=float, help='noise mu') 
# strategy = 'explexpl' if strategy=='ddpg' and ct.USE_PYGAME == True else strategy
# parser.add_argument('--validate_episodes', default=20, type=int, help='how many episode to perform during validate experiment')
# parser.add_argument('--max_episode_length', default=500, type=int, help='')
# parser.add_argument('--validate_steps', default=2000, type=int, help='how many steps to perform a validate experiment')
# parser.add_argument('--output', default='output', type=str, help='')
# parser.add_argument('--debug', dest='debug', action='store_true')
# parser.add_argument('--init_w', default=0.003, type=float, help='') 
# parser.add_argument('--train_iter', default=200000, type=int, help='train iters each timestep')
# parser.add_argument('--epsilon', default=50000, type=int, help='linear decay of exploration policy')
# parser.add_argument('--seed', default=-1, type=int, help='')
# parser.add_argument('--resume', default='default', type=str, help='Resuming model path for testing')

# args = parser.parse_args()
print("before creating model")
init_st = [[False for _ in range(ct.NUM_TARGET[-1] + ct.NUM_OBS[-1])] for _ in range(ct.NUM_OBS[-1])]
for i in range(ct.NUM_OBS[-1]):
    x, y = obs_pos[i]
    for j in range(ct.NUM_TARGET[-1]):
        a, b = target_pos[j]
        if (x - a)**2 + (y - b)**2 <= ct.SENS_RAN[2]**2:
            init_st[i][j] = True
 
    for j in range(ct.NUM_OBS[-1]):
        a, b = obs_pos[j]
        if (x - a)**2 + (y - b)**2 <= ct.SENS_RAN[2]**2:
            init_st[i][ct.NUM_TARGET[-1] + j] = True
    
    init_st[i] = np.array(init_st[i], dtype=float)
        
net = [ DDPG(ct.NUM_OBS[-1], ct.NUM_TARGET[-1], ct.AR_WID, ct.AR_HEI, init_st[i], "memory" + str(i) + ".npz") for i in range(ct.NUM_OBS[-1]) ]        # nwa
# check if actor.pkl and critic.pkl exist
for i in range(ct.NUM_OBS[-1]):
    if os.path.exists("actor" + str(i) + ".pkl") and os.path.exists("critic" + str(i) + ".pkl"):
        net[i].load_weights(".", i)
        
print("after creating model")

Score = 0
gamma = 0
time_step = 0
pause = False
# print("start")
while time_step < ct.TOTAL_TIME:
    # print("time step: ", time_step)
    if ct.USE_PYGAME == True:
        # print("here")
        for event in pg.event.get():
            if event.type == pg.QUIT:
                time_step = ct.TOTAL_TIME    # Break the loop

            if event.type == pg.KEYDOWN:
                if event.key == pg.K_p:
                    pause = True
                    misc.paused(window)

        window.fill((0, 0, 0))
        # Update the position of targets
        up.TargUpdate( target_pos, targ, target_dest, obs_pos, obsvr, time_step, net )

        # Update the position of observers
        up.ObsUpdate( obs_pos, obsvr, obs_dest, target_pos, targ, time_step, strategy, net )

        # Check if the target is observed
        Score = up.ScrUpdate( target_pos, obs_pos, Score )
        
        # Display the score
        if pause == False:
            up.DispScr(Score)
            # misc.paused(window)

        # Update the screen
        pg.display.update()

        print(f"time_step: {time_step} Score: {Score}")
        # print(f"obs_pos = {[(int(f),int(s)) for f,s in obs_pos]}")
        # print(f"target_pos = {[(int(f),int(s)) for f,s in target_pos]}")
        print()
        pg.time.delay(100)

    else:
        # print("here, in else")
        print(f"time_step: {time_step} Score: {Score}")
        # print('before target update obs_pos: ', obs_pos)
        up.TargUpdate( target_pos, targ, target_dest, obs_pos, obs_dest, time_step, net )
        # print('before obs update obs_pos: ', obs_pos)
        up.ObsUpdate( obs_pos, obsvr, obs_dest, target_pos, targ, time_step, strategy, net )

        # print('before score update obs_pos: ', obs_pos)
        Score = up.ScrUpdate( target_pos, obs_pos, Score )
        if strategy.lower() == 'randomise':
            with open('a.txt', 'a') as f:
                f.write(f"{Score}\n")

    time_step += 1
    # pg.time.delay(10)

# save model
if strategy.lower() == 'ddpg':
    for i in range(ct.NUM_OBS[-1]):
        net[i].save_model(".", i)
        net[i].memory.save("memory" + str(i) + ".npz")

Score /= ct.TOTAL_TIME
# fname = 'obs_comp_' + strategy + '.txt'
fname = 'ddv1.txt'
with open(fname, 'a') as f:
    f.write(f"{Score}\n")

if ct.USE_PYGAME == True:
    pg.quit()
