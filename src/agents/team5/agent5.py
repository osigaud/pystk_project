import numpy as np
import random

from utils.track_utils import compute_curvature, compute_slope
from agents.kart_agent import KartAgent


class Agent5(KartAgent):
    def __init__(self, env, path_lookahead=3):
        super().__init__(env)
        self.path_lookahead = path_lookahead
        self.agent_positions = []
        self.obs = None
        self.isEnd = False
        self.name = "Donkey Bombs" # replace with your chosen name

    def reset(self):
        self.obs, _ = self.env.reset()
        self.agent_positions = []

    def endOfTrack(self):
        return self.isEnd

    def choose_action(self, obs):
        acceleration = random.random()
        steering = 0 #random.random() #De -1 (Gauche) à 1 (Droite)
        action = {
            "acceleration": acceleration,
            "steer": steering,
            "brake": True, # bool(random.getrandbits(1)),
            "drift": 0,#bool(random.getrandbits(1)),
            "nitro": 0,#bool(random.getrandbits(1)),
            "rescue":0,#bool(random.getrandbits(1)),
            "fire": 0,#bool(random.getrandbits(1)),
        }
        return action
