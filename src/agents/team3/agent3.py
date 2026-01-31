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
        self.time_blocked = 0

    def reset(self):
        self.obs, _ = self.env.reset()
        self.agent_positions = []


        

    def endOfTrack(self):
        return self.isEnd
    
    def choose_action(self, obs):
        target = obs["paths_end"][0] #return a vector [x,y,z]
        x = target[0] #Extracting the x
        if (abs(x) > 0.5 and obs["distance_down_track"] > 5.0):
        	acceleration = 0.15
        	brake = True
        else:
        	acceleration = 0.9
        	brake = False
        speed = obs["velocity"][2]
        if (speed < 0.20 and obs["distance_down_track"] > 5.0):
        	self.time_blocked = self.time_blocked + 1
        	if (self.time_blocked > 10):
        		acceleration = 0.0
        		brake = True
        		x = -x
        if (self.time_blocked == 18):
        	self.time_blocked = 0
        action = {
            "acceleration": acceleration,
            "steer": x,
            "brake": brake,
            "drift": False,
            "nitro": use_nitro,
            "rescue": False,
            "fire": use_fire,
        }
        return action
