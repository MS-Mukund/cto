
import numpy as np

import torch
import torch.nn as nn
from torch.optim import Adam

import sys
# relative imports
from .util import *
from .model import (Actor, Critic)
from .memory import SequentialMemory
from .random_process import OrnsteinUhlenbeckProcess

sys.path.append('../oldscripts/')
import constant
import update
# from ipdb import set_trace as debug

criterion = nn.MSELoss()

H1 = 40
H2 = 30
INIT_W = 3e-3
LR = 1e-4
RATE = 1e-3
RMSIZE = 10000
WINDOW_LENGTH = 1
OU_THETA = 0.15
OU_MU = 0.0 
OU_SIGMA = 0.2
BSIZE = 1
TAU = 0.001
DISCOUNT = 0.99
EPSILON = 5000

class DDPG(object):
    def __init__(self, num_observ, num_adv, WID, HT, init_pos):
        self.nb_states = num_observ * num_adv
        self.nb_actions = WID * HT    # (x, y) coordinates, 100 divisions per unit length 
        self.WID = WID
        self.HT = HT
        self.num_adv = int(num_adv)
        self.num_observ = num_observ
        self.H1 = H1
        
        # Create Actor and Critic Network
        net_cfg = {  
            'hidden1': self.H1,
            'hidden2': H2, 
            'init_w': INIT_W
        }
        
        # print("before actor")
        self.actor = Actor(int(num_adv) + int(num_observ), self.nb_states, self.nb_actions, **net_cfg)
        # print("before targ")
        self.actor_target = Actor(num_adv + num_observ, self.nb_states, self.nb_actions, **net_cfg)
        # print("before optim")
        self.actor_optim  = Adam(self.actor.parameters(), lr=LR)

        self.critic = Critic(num_adv + num_observ, self.nb_states, self.nb_actions, **net_cfg)
        self.critic_target = Critic(num_adv + num_observ, self.nb_states, self.nb_actions, **net_cfg)
        self.critic_optim  = Adam(self.critic.parameters(), lr=RATE)

        hard_update(self.actor_target, self.actor) # Make sure target is with the same weight
        hard_update(self.critic_target, self.critic)
        
        #Create replay buffer
        self.memory = SequentialMemory(limit=RMSIZE, window_length=1)
        self.random_process = OrnsteinUhlenbeckProcess(size=2, theta=OU_THETA, mu=OU_MU, sigma=OU_SIGMA)

        # Hyper-parameters
        self.batch_size = BSIZE
        self.tau = TAU
        self.discount = DISCOUNT
        self.depsilon = 1.0 / EPSILON

        # 
        self.epsilon = 1.0
        self.s_t = init_pos
        self.a_t = None # Most recent action
        self.is_training = True

        # 
        if USE_CUDA: self.cuda()

    def update_policy(self):
        # Sample batch
    
        state_batch, action_batch, reward_batch, \
        next_state_batch = self.memory.sample_and_split(self.batch_size)

        # Prepare for the target q batch
        # return 
        next_q_values = self.critic_target([
            to_tensor(next_state_batch, volatile=True),
            self.actor_target(to_tensor(next_state_batch, volatile=True)),
        ])
        next_q_values.volatile=False

        # print(reward_batch.shape)
        reward_ratio = reward_batch / (reward_batch.sum(keepdims=True) + 1e-8) 
        target_q_batch = to_tensor(reward_ratio) + \
            self.discount*next_q_values

        # Critic update
        self.critic.zero_grad()
        # print('critic update: ', state_batch, action_batch)
        q_batch = self.critic([ to_tensor(state_batch), to_tensor(action_batch) ])
        value_loss = criterion(q_batch, target_q_batch)
        value_loss.backward()
        self.critic_optim.step()

        # Actor update
        self.actor.zero_grad()

        policy_loss = -self.critic([
            to_tensor(state_batch),
            self.actor(to_tensor(state_batch))
        ])

        policy_loss = policy_loss.mean()
        policy_loss.backward()
        self.actor_optim.step()

        # Target update
        soft_update(self.actor_target, self.actor, self.tau)
        soft_update(self.critic_target, self.critic, self.tau)

    def eval(self):
        self.actor.eval()
        self.actor_target.eval()
        self.critic.eval()
        self.critic_target.eval()

    def cuda(self):
        self.actor.cuda()
        self.actor_target.cuda()
        self.critic.cuda()
        self.critic_target.cuda()

    def observe(self, r_t, a_t, s_t1):
        if self.is_training:
            self.memory.append(self.s_t, a_t, r_t, False)
            self.s_t = s_t1

    def random_action(self):
        action = np.random.uniform(-1.,1.,self.nb_actions)
        self.a_t = action
        return action

    def select_action(self, x, y, s_t, decay_epsilon=True):        
        # count number of ones in the first num_adv elements
        num_adv = np.sum(np.array(s_t[:self.num_adv]))
        num_observ = np.sum(np.array(s_t[self.num_adv:]))
              
        targ_rew = int(num_adv) / (num_observ + 1)
        action = to_numpy(
            self.actor(to_tensor(np.array([s_t])))
        ).squeeze(0)
        action += self.is_training*max(self.epsilon, 0)*self.random_process.sample() 
        
        if decay_epsilon:
            self.epsilon -= self.depsilon
        
        action = np.clip(action, -1., 1.)
        # action - change from angle to (x, y) coordinates   
        final_x = x + constant.GAMMA * constant.OBS_SPEED * np.cos(action)
        final_y = y + constant.GAMMA * constant.OBS_SPEED * np.sin(action)
        final_x = np.clip(final_x, 0, constant.AR_WID)
        final_y = np.clip(final_y, 0, constant.AR_HEI)
        
        self.action = np.array([final_x, final_y])
        return self.action

    def reset(self, obs):
        self.s_t = obs
        self.random_process.reset_states()

    def load_weights(self, output, ind):
        if output is None: return

        self.actor.load_state_dict(
            torch.load('{}/actor{}.pkl'.format(output, ind))
        )

        self.critic.load_state_dict(
            torch.load('{}/critic{}.pkl'.format(output, ind))
        )


    def save_model(self,output, i):
        torch.save(
            self.actor.state_dict(),
            '{}/actor{}.pkl'.format(output, i)
        )
        torch.save(
            self.critic.state_dict(),
            '{}/critic{}.pkl'.format(output, i)
        )

    def seed(self,s):
        torch.manual_seed(s)
        if USE_CUDA:
            torch.cuda.manual_seed(s)