import numpy as np
import random
import math

from utils.track_utils import compute_curvature, compute_slope
from agents.kart_agent import KartAgent

#Base d'Agent, mouvements aléatoires, initialisation des variables
class AgentBase(KartAgent):
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
            "acceleration": acceleration,
            "steer": steering,
            "brake": bool(random.getrandbits(1)),
            "drift": bool(random.getrandbits(1)),
            "nitro": bool(random.getrandbits(1)),
            "rescue": bool(random.getrandbits(1)),
            "fire": bool(random.getrandbits(1)),
        }
        return action

#Agent qui roule tout droit
class AgentStraight(AgentBase):
    def choose_action(self, obs):
        action = {
            "acceleration": 1, 
            "steer": 0, 
            "brake": False, 
            "drift": False, 
            "nitro": False, 
            "rescue": False, 
            "fire": False, 
        }
        return action

#AGENT FINAL :
class Agent1(AgentStraight):
    def __init__(self, env, path_lookahead=3):        
        super().__init__(env, path_lookahead)
