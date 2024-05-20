from __future__ import absolute_import
from collections import deque, namedtuple
import warnings
import random

import numpy as np

# Given state0, performing action yields reward and results in state1
Experience = namedtuple('Experience', 'state0, action, reward, state1')


def sample_batch_indexes(low, high, size):
    if high - low >= size:
        r = range(low, high)
        batch_idxs = random.sample(r, size)
    else:
        warnings.warn('Not enough entries to sample without replacement. Consider increasing your warm-up phase to avoid oversampling!')
        batch_idxs = np.random.random_integers(low, high - 1, size=size)
    assert len(batch_idxs) == size
    return batch_idxs


class RingBuffer(object):
    def __init__(self, maxlen):
        self.maxlen = maxlen
        self.start = 0
        self.length = 0
        self.data = [None for _ in range(maxlen)]

    def __len__(self):
        return self.length

    def __getitem__(self, idx):
        if idx < 0 or idx >= self.length:
            raise KeyError()
        return self.data[(self.start + idx) % self.maxlen]

    def append(self, v):
        if self.length < self.maxlen:
            self.length += 1
        elif self.length == self.maxlen:
            # remove the first item.
            self.start = (self.start + 1) % self.maxlen
        else:
            raise RuntimeError()
        self.data[(self.start + self.length - 1) % self.maxlen] = v

def zeroed_observation(observation):
    if hasattr(observation, 'shape'):
        return np.zeros(observation.shape)
    elif hasattr(observation, '__iter__'):
        out = []
        for x in observation:
            out.append(zeroed_observation(x))
        return out
    else:
        return 0.


class Memory(object):
    def __init__(self, window_length, ignore_episode_boundaries=False):
        self.window_length = window_length
        self.ignore_episode_boundaries = ignore_episode_boundaries

        self.recent_observations = deque(maxlen=window_length)

    def sample(self, batch_size, batch_idxs=None):
        raise NotImplementedError()

    def append(self, observation, action, reward, training=True):
        self.recent_observations.append(observation)

    def get_recent_state(self, current_observation):
        # This code is slightly complicated by the fact that subsequent observations might be
        # from different episodes. We ensure that an experience never spans multiple episodes.
        # This is probably not that important in practice but it seems cleaner.
        state = [current_observation]
        idx = len(self.recent_observations) - 1
        for offset in range(0, self.window_length - 1):
            current_idx = idx - offset
            state.insert(0, self.recent_observations[current_idx])
        while len(state) < self.window_length:
            state.insert(0, zeroed_observation(state[0]))
        return state

    def get_config(self):
        config = {
            'window_length': self.window_length,
            'ignore_episode_boundaries': self.ignore_episode_boundaries,
        }
        return config

class SequentialMemory(Memory):
    def __init__(self, limit, **kwargs):
        super(SequentialMemory, self).__init__(**kwargs)
        
        self.limit = limit

        # Do not use deque to implement the memory. This data structure may seem convenient but
        # it is way too slow on random access. Instead, we use our own ring buffer implementation.
        self.actions = RingBuffer(limit)
        self.rewards = RingBuffer(limit)
        self.observations = RingBuffer(limit)

    def sample(self, batch_size, batch_idxs=None):
        if batch_idxs is None:
            # Draw random indexes such that we have at least a single entry before each
            # index.
            batch_idxs = sample_batch_indexes(0, self.nb_entries - 1, size=batch_size)
        batch_idxs = np.array(batch_idxs) + 1
        assert np.max(batch_idxs) < self.nb_entries
        assert len(batch_idxs) == batch_size

        # Create experiences
        experiences = []
        for idx in batch_idxs:
            state0 = self.observations[idx - 1]
            # while len(state0) < self.window_length:
                # state0.insert(0, zeroed_observation(state0[0]))
            action = self.actions[idx - 1]
            reward = self.rewards[idx - 1]

            # Okay, now we need to create the follow-up state. This is state0 shifted on timestep
            # to the right.  
            state1 = self.observations[idx]
            
            # print("here")
            # print(state0, state1 )
            # print(len(state0), len(state1))
            
            if len(state0) != len(state1):
                if len(state0) == 1:
                    state0 = state0[0]
                elif len(state1) == 1:
                    state1 = state1[0]

            # assert len(state0) == self.window_length
            assert len(state1) == len(state0)
            experiences.append(Experience(state0=state0, action=action, reward=reward,
                                          state1=state1))
        assert len(experiences) == batch_size
        return experiences

    def sample_and_split(self, batch_size, batch_idxs=None):
        experiences = self.sample(batch_size, batch_idxs)
        # print('begin ', batch_idxs, batch_size)

        state0_batch = []
        reward_batch = []
        action_batch = []
        state1_batch = []
        for e in experiences:
            # print('experiences ', e.state0)
            state0_batch.append(e.state0)
            state1_batch.append(e.state1)
            reward_batch.append(e.reward)
            action_batch.append(e.action)

        # Prepare and validate parameters.
        # print('state0_batch ', state0_batch, len(state0_batch))
        state0_batch = np.array(state0_batch)
        state1_batch = np.array(state1_batch)
        reward_batch = np.array(reward_batch)
        action_batch = np.array(action_batch)

        return state0_batch, action_batch, reward_batch, state1_batch

    def append(self, observation, action, reward, training=True):
        super(SequentialMemory, self).append(observation, action, reward, training=training)
        
        # This needs to be understood as follows: in `observation`, take `action`, obtain `reward`
        self.observations.append(observation)
        self.actions.append(action)
        self.rewards.append(reward)

    @property
    def nb_entries(self):
        return len(self.observations)

    def get_config(self):
        config = super(SequentialMemory, self).get_config()
        config['limit'] = self.limit
        return config


class EpisodeParameterMemory(Memory):
    def __init__(self, limit, **kwargs):
        super(EpisodeParameterMemory, self).__init__(**kwargs)
        self.limit = limit

        self.params = RingBuffer(limit)
        self.intermediate_rewards = []
        self.total_rewards = RingBuffer(limit)

    def sample(self, batch_size, batch_idxs=None):
        if batch_idxs is None:
            batch_idxs = sample_batch_indexes(0, self.nb_entries, size=batch_size)
        assert len(batch_idxs) == batch_size

        batch_params = []
        batch_total_rewards = []
        for idx in batch_idxs:
            batch_params.append(self.params[idx])
            batch_total_rewards.append(self.total_rewards[idx])
        return batch_params, batch_total_rewards

    def append(self, observation, action, reward, training=True):
        super(EpisodeParameterMemory, self).append(observation, action, reward, training=training)
        if training:
            self.intermediate_rewards.append(reward)

    def finalize_episode(self, params):
        total_reward = sum(self.intermediate_rewards)
        self.total_rewards.append(total_reward)
        self.params.append(params)
        self.intermediate_rewards = []

    @property
    def nb_entries(self):
        return len(self.total_rewards)

    def get_config(self):
        config = super(SequentialMemory, self).get_config()
        config['limit'] = self.limit
        return config