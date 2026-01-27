import numpy as np
import random
import math

from utils.track_utils import compute_curvature, compute_slope
from agents.kart_agent import KartAgent


class Agent1(KartAgent):
    def __init__(self, env, path_lookahead=3):
        super().__init__(env)
        self.path_lookahead = path_lookahead
        self.agent_positions = []
        self.obs = None
        self.isEnd = False
        self.name = "Tasty Crousteam" # nom de l'équipe

    def reset(self):
        self.obs, _ = self.env.reset()
        self.agent_positions = []

    def endOfTrack(self):
        return self.isEnd

    def choose_action(self, obs):
        acceleration = random.random()
        steering = random.random()
        action = {
            "acceleration": 1,
            "steer": 0,
            "brake": False, # bool(random.getrandbits(1)),
            "drift": False, #pour pas qu'il drift et qu'il roule tout droit
            "nitro": False, #bool(random.getrandbits(1)),
            "rescue": False, #bool(random.getrandbits(1)),
            "fire": False, #bool(random.getrandbits(1)),
        }
        return action
