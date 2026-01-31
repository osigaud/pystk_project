import numpy as np
import random

from utils.track_utils import compute_curvature, compute_slope
from agents.kart_agent import KartAgent
from .steering import Steering


class Agent4(KartAgent):
    def __init__(self, env, path_lookahead=3):
        super().__init__(env)
        self.path_lookahead = path_lookahead
        self.agent_positions = []
        self.obs = None
        self.isEnd = False
        self.name = "The Winners" # replace with your chosen name
        self.steering = Steering()

    def reset(self):
        self.obs, _ = self.env.reset()
        self.agent_positions = []

    def endOfTrack(self):
        return self.isEnd

    def choose_action(self, obs):
        acceleration = 1.0
        steering = self.steering.steering(obs)
        action = {
            "acceleration": acceleration,
            "steer": steering,
            "brake": False, # bool(random.getrandbits(1)),
            "drift": False,
            "nitro": False,
            "rescue":False,
            "fire": False,
        }
        return action
