import numpy as np

from utils.track_utils import compute_curvature, compute_slope
from agents.kart_agent import KartAgent

class Agent3(KartAgent):
    def __init__(self, env, path_lookahead=3):
        super().__init__(env)
        self.path_lookahead = path_lookahead
        self.agent_positions = []
        self.obs = None
        self.isEnd = False
        self.name = "TEAM L'ÉCLAIR"

    def reset(self):
        self.obs, _ = self.env.reset()
        self.agent_positions = []

    def endOfTrack(self):
        return self.isEnd

    def choose_action(self, obs):
        acceleration = 0.7
        target = obs["paths_end"][0] #return a vector [x,y,z]
        x = target[0] #We extract the x axis
        if (x > 1):
        	x = 1 #Here, x represents the steering wheel in order to change the path
        elif (x < -1):
        	x = -1
        action = {
            "acceleration": acceleration,
            "steer": x,
            "brake": False,
            "drift": False,
            "nitro": False,
            "rescue": False,
            "fire": False,
        }
        return action
