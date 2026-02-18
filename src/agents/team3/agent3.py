import math
import numpy as np
from agents.kart_agent import KartAgent
from agents.team3.FireItems import FireItems

class Agent3(KartAgent):
    def __init__(self, env, path_lookahead=3):
        super().__init__(env)
        self.prev_err = 0.0
        self.obs = None
        self.isEnd = False
        self.agent_positions = [] 
        self.name = "Team L'Eclair"
        self.time_blocked = 0

    def reset(self):
        self.obs, _ = self.env.reset()
        self.prev_err = 0.0
        self.time_blocked = 0
    
    def endOfTrack(self):
        return self.isEnd

    def choose_action(self, obs):
        
        action = FireItems.choose_action(self, obs)
        
        return action
