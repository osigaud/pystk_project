import numpy as np
import random

from utils.track_utils import compute_curvature, compute_slope
from agents.kart_agent import KartAgent


class Agent2(KartAgent):
    def __init__(self, env, path_lookahead=3):
        super().__init__(env)
        self.path_lookahead = path_lookahead
        self.agent_positions = []
        self.obs = None
        self.isEnd = False
        self.name = "Team2" # replace with your chosen name

    def reset(self):
        self.obs, _ = self.env.reset()
        self.agent_positions = []

    def endOfTrack(self):
        return self.isEnd

    def choose_action(self, obs):
        acceleration = 1.0
        steering = 0.1
        action = {
            "acceleration": acceleration,
            "steer": steering,
            "brake": False, # bool(random.getrandbits(1)),
            "drift": False,#bool(random.getrandbits(1)),
            "nitro": False,#bool(random.getrandbits(1)),
            "rescue": False,#bool(random.getrandbits(1)),
            "fire": False,#bool(random.getrandbits(1)),
        }
        return action
