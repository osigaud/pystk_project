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


def calculer_direction(self,obs ) : 
        distance = obs['center_path'][0] # center_path designe le vecteur du centre de la route donc il contient 3 coordonnees l'un l'index gauche ou droite l'autre la hauteur et le dernier la distance devant nous le 0 donc c'est l'indice de ce quon a besoin poiur la distance 

        angle = distance * 0.4 # si la distance est par exemple 2 metres  il va reagir que 40% de la distance 
        if angle > 1:
            angle = 1  # on s'assure que l'angle reste entre -1 et 1
        elif angle < -1:
            angle = -1
            
        return angle        


    def choose_action(self, obs):
        acceleration = 1
        steering = 0
        action = {
            "acceleration": acceleration,
            "steer": steering,
            "brake": False, # bool(random.getrandbits(1)),
            "drift": bool(random.getrandbits(1)),
            "nitro": bool(random.getrandbits(1)),
            "rescue":bool(random.getrandbits(1)),
            "fire": bool(random.getrandbits(1)),

        #if target_item_distance== 10:
            if obs['target_item_type'] in bad_type:
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


        }
        return action
