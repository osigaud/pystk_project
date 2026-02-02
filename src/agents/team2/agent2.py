import numpy as np
import random

from utils.track_utils import compute_curvature, compute_slope
from agents.kart_agent import KartAgent


class Agent2(KartAgent):
    def __init__(self, env, path_lookahead=3):
        super().__init__(env)
        self.path_lookahead = path_lookahead
        self.agent_positions = []
        self.obs = None
        self.isEnd = False
        self.name = "Team2" # replace with your chosen name

    def reset(self):
        self.obs, _ = self.env.reset()
        self.agent_positions = []

    def endOfTrack(self):
        return self.isEnd

    def choose_action(self, obs):
        acceleration = 0
        #random.random()
        steering = -1 #au lieu de radom pour aller a gauche
        #random.random()
        action = {
            "acceleration": acceleration,
            "steer": steering,
            "brake": False, # bool(random.getrandbits(1)),
            "drift": bool(random.getrandbits(1)),
            "nitro": bool(random.getrandbits(1)),
            "rescue":bool(random.getrandbits(1)),
            "fire": bool(random.getrandbits(1)),
        }
        #if target_item_distance== 10:
            if target_item_type in bad_type:
                if target_item_angle >5: # obstacle a droite
                    action["steer"]= - 0.5 # on tourne a gauche
                    action["nitro"]=False
                    action["acceleration"]= action["acceleration"] - 0.5 #val a determiner
                elif target_item_angle ==0 : # obstacle a droite
                    action["steer"]= - 0.5 # on tourne a gauche ou droite
                    action["nitro"]=False
                    action["acceleration"]= action["acceleration"] - 0.5 #val a determiner
                elif target_item_angle <-5: # obstacle a gauche 
                    action["steer"]= 0.5 # on tourne a droite
                    action["nitro"]=False
                    action["acceleration"]= action["acceleration"] - 0.5 #val a determiner

            elif target_item_type in good_type:
                if target_item_angle <-5: # a gauche 
                    action["steer"]= - 0.5 # on tourne a gauche
                    action["nitro"]=True
                    action["acceleration"]= action["acceleration"] + 0.5 #val a determiner
                elif target_item_angle >5: #a droite
                    action["steer"]= 0.5 # on tourne a droite
                    action["nitro"]=True
                    action["acceleration"]= action["acceleration"] + 0.5 #val a determiner


        return action
