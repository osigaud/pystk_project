import numpy as np
import math

from agents.kart_agent import KartAgent

from agents.team3.Rescue import Rescue

class Agent3(KartAgent):
    def __init__(self, env, path_lookahead=3):
        super().__init__(env)
        self.track = env.default_track
        self.agent_positions = []
        self.obs = None
        self.isEnd = False
        self.name = "Team L'Eclair"
        self.drift_dir = 0 
        self.stuck_timer = 0

    def reset(self):
        self.obs, _ = self.env.reset()
        self.agent_positions = []
        self.drift_dir = 0 
        self.stuck_timer = 0

    def endOfTrack(self):
        return self.isEnd

    def choose_action(self, obs):

        action = Rescue.choose_action(self, obs)
        
        
        return action
