import collections
import gym
import numpy as np
import os
import sys
import tensorflow as tf

from gfootball.env import observation_preprocessing
from gfootball.env import wrappers

EnvOutput = collections.namedtuple(
    'EnvOutput', 'reward done observation abandoned episode_step')

def prepare_agent_input(observation, prev_action, state):
    # SEED RL agent accepts input in a form of EnvOutput. When not training
    # only observation is used for generating action, so we use a dummy values
    # for the rest.
    env_output = EnvOutput(reward=tf.zeros(shape=[], dtype=tf.float32),
        done=tf.zeros(shape=[], dtype=tf.bool),
        observation=observation, abandoned=False,
        episode_step=tf.zeros(shape=[], dtype=tf.int32))
    # add batch dimension
    prev_action, env_output = tf.nest.map_structure(
        lambda t: tf.expand_dims(t, 0), (prev_action, env_output))

    return (prev_action, env_output, state)

# Previously executed action
previous_action = tf.constant(0, dtype=tf.int64)
# Queue of recent observations (SEED agent we trained uses frame stacking).
observations = collections.deque([], maxlen=4)
# Current state of the agent (used by recurrent agents).
state = ()

# Load previously trained Tensorflow model.
policy = tf.compat.v2.saved_model.load('./agent/saved_model')

def agent(obs):
    global step
    global previous_action
    global observations
    global state
    global policy
    # Get observations for the first (and only one) player we control.
    obs = obs['players_raw'][0]
    # Agent we trained uses Super Mini Map (SMM) representation.
    # See https://github.com/google-research/seed_rl/blob/master/football/env.py for details.
    obs = observation_preprocessing.generate_smm([obs])[0]
    if not observations:
        observations.extend([obs] * 4)
    else:
        observations.append(obs)
    
    obs = np.concatenate(list(observations), axis=-1)
    # SEED packs observations to reduce transfer times.
    # See PackedBitsObservation in https://github.com/google-research/seed_rl/blob/master/football/observation.py
    obs = np.packbits(obs, axis=-1)
    if obs.shape[-1] % 2 == 1:
        obs = np.pad(obs, [(0, 0)] * (obs.ndim - 1) + [(0, 1)], 'constant')
    obs = obs.view(np.uint16)
    # Execute our agent to obtain action to take.
    agent_output, state = policy.get_action(*prepare_agent_input(obs, previous_action, state))
    previous_action = agent_output.action[0]
    return [int(previous_action)]
