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
            "acceleration": 0.5, 
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
class AgentCenter(AgentStraight):
    #initialisation de l'agent center de base
    def __init__(self, env, dist, ajust):
        super().__init__(env)
        self.dist = dist #écart max au centre de la piste qu'on accepte
        self.ajust = ajust #la valeur que l'on veut addi/soustr à notre steer, qui sert d'ajustement de la trajectoire


    def path_ajust(self, act, obs):
        s = act["steer"]
        center = obs["center_path_distance"]

        # gros ecart -> gros virage
        if center < -self.dist:
            s = s + self.ajust
        elif center > self.dist:
            s = s - self.ajust

        # petit ecart -> petit virage
        elif center < -self.dist / 2:
            s = s + self.ajust / 2
        elif center > self.dist / 2:
            s = s - self.ajust / 2

        act["steer"] = s
        return act

    
    def choose_action(self, obs):
            act = super().choose_action(obs)
            act_corr = self.path_ajust(act, obs)
            return act_corr

#AGENT FINAL :
class Agent1(AgentCenter):
    def __init__(self, env, path_lookahead=3): 
        dist = 0.5
        ajust = 0.25      
        super().__init__(env, dist, ajust)
