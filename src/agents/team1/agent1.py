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

#Agent qui suit le centre de la piste
#méthodes à rajouter ici
class AgentCenter(KartAgent):
    def __init__(self, env, dist, ajust, base_agent):
        super().__init__(env)
        self.base = base_agent
        self.dist = dist
        self.ajust = ajust

    def path_ajust(self, act, obs, min_d, max_d):
        s = act["steer"]
        center = obs["center_path_distance"]
        if center < min_d: 
            s=s+self.ajust
        elif center > max_d: 
            s=s-self.ajust
        act["steer"] = s
        return act 
    
    def choose_action(self, obs):
            act = self.base.choose_action(obs)
            act_corr = self.path_ajust(act, obs, -0.5, 0.5)
            return act_corr

#AGENT FINAL :
class Agent1(AgentCenter):
    def __init__(self, env, path_lookahead=3):        
        super().__init__(env, path_lookahead)
