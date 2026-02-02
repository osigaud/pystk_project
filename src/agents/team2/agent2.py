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

    #implémentation du code calcul d'angle 
    def _calcul_angle(self,obs):
        if len(obs) < 1 :  #permet de vérifier si obs existe 
            return 0.0 
        elif len(obs["paths_start"]) < 1:
            return 0.0
        elif len(obs["paths_end"]) < 1: # paths_end renvoie un segment de fin 
            return 0.0
        elif len(obs["karts_position"]) < 1 :
            return 0.0
        elif len(obs["velocity"]) < 3 : 
            return 0.0
        else : 
            paths_start = obs["paths_start"] # x y z 
            paths_end = obs["paths_end"] # x2 y2 z2 
            karts_position = obs["karts_position"] 
            #nodes = obs["path_nodes"] n existe pas 
            
            idx = min(self.path_lookahead, len(paths_start) - 1)

            seg_start = np.array(paths_start[idx])
            seg_end = np.array(paths_end[idx]) 
            pos = np.array(karts_position[0])
            
            cible = (seg_start+seg_end)/2
            vecteur_traj = cible - pos
            
            vecteur_vit = np.array(obs["velocity"][0:3]) #[0:3] -> on prend les coordonnées x y z 
            
            produit_vect = vecteur_traj[0]*vecteur_vit[2] - vecteur_traj[2]*vecteur_vit[0]
            produit_scal = vecteur_traj[0]*vecteur_vit[0] + vecteur_traj[2]*vecteur_vit[2]
            angle = np.arctan2(produit_vect,produit_scal)
            
            return angle             
    
    def choose_action(self, obs):
        angle = self._calcul_angle(obs)
        print(f"Angle actuel: {angle:.3f} rad, {np.degrees(angle):.1f}°")

        acceleration = 0
        steering = -1.0
        action = {
            "acceleration": acceleration,
            "steer":  False, #np.clip(angle, -0.5, 0.5),
            "brake": False, #abs(angle) > 1.0, # bool(random.getrandbits(1)),
            "drift": False, 
            "nitro": False,
            "rescue": False,
            "fire": False,
>>>>>>> cda782b (Ajout de la fonction _calcul_angle dans le fichier agent2)
        }
        return action
