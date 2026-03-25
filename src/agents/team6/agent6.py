import numpy as np
import random

from utils.track_utils import compute_curvature, compute_slope
from agents.kart_agent import KartAgent



class Agent6(KartAgent):
    def __init__(self, env, path_lookahead=3):
        super().__init__(env)
        self.path_lookahead = path_lookahead
        self.agent_positions = []
        self.obs = None
        self.isEnd = False
        self.name = "Team6" # replace with your chosen name

    def reset(self):
        self.obs, _ = self.env.reset()
        self.agent_positions = []

    def endOfTrack(self):
        return self.isEnd

    def suivre_piste(self, obs, action):
        steer = action["steer"]
        centre = obs["paths_end"][2]
        if (abs(centre[0])>2):
            steer += 0.1 * centre[0]
        action["steer"]=steer
        return action



    def choose_action(self, obs):
        acceleration = random.random()
        steering = random.random()
        action = {
            "acceleration" : 0.7,
            "steer": 0,
            "brake": False, # bool(random.getrandbits(1)),
            "drift": False,
            "nitro": bool(random.getrandbits(1)),
            "rescue":bool(random.getrandbits(1)),
            "fire": bool(random.getrandbits(1)),
        }
        action = self.suivre_piste(obs,action)
        return action
