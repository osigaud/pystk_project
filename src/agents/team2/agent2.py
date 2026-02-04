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
        self.name = "DemoPilote " # Tu peux remettre "DemoPilote" ici

        self.stuck_steps = 0    
        self.recovery_steps = 0  

    def reset(self):
        self.obs, _ = self.env.reset()
        self.agent_positions = []
        self.stuck_steps = 0
        self.recovery_steps = 0

    def endOfTrack(self):
        return self.isEnd

    def choose_action(self, obs):
        # --- 1. GESTION DU BLOCAGE (Si on est coincé) ---
        if self.recovery_steps > 0:
            self.recovery_steps -= 1
            # On freine et on attend (ou on recule si besoin)
            return {
                "acceleration": 0.0,
                "steer": 0.0,
                "brake": True,  
                "drift": False,
                "nitro": False,
                "rescue": False,
                "fire": False,
            }

        # --- 2. ANALYSE DE LA SITUATION ---
        velocity = np.array(obs["velocity"])
        speed = np.linalg.norm(velocity)
        
        # Correction ici : obs.get() prend des parenthèses, pas des crochets
        phase = obs.get("phase", 0) 
        
        # On récupère le chemin (path)
        # Note: Assure-toi que "paths_start" existe bien dans ton obs, 
        # sinon utilise obs['center_path'] comme avant.
        if "paths_start" in obs:
            nodes_path = obs["paths_start"]
        else:
            # Sécurité si paths_start n'existe pas
            nodes_path = [] 

        # --- 3. DETECTION SI ON EST COINCÉ ---
        # Si la phase (le temps) avance mais qu'on ne bouge pas (vitesse < 0.2)
        if phase > 2:  
            if speed < 0.2:  
                self.stuck_steps += 1
            else:
                self.stuck_steps = 0
               
        # Si on est coincé trop longtemps, on déclenche le mode "Recovery"
        if self.stuck_steps > 7:
            self.recovery_steps = 15
            self.stuck_steps = 0

        # --- 4. CALCUL DE LA DIRECTION (NOUVELLE LOGIQUE) ---
        angle = 0 # Valeur par défaut
        
        if len(nodes_path) > self.path_lookahead:
            target_node = nodes_path[self.path_lookahead]
            # Calcul de l'angle vers le point cible
            angle_target = np.arctan2(target_node[0], target_node[2])
            steering = np.clip(angle_target * 2, -1, 1)
            angle = angle_target # Pour l'affichage print plus bas
        else:
            # Si on ne trouve pas de chemin, on reste droit ou on utilise l'ancienne méthode
            steering = 0
           
        # Petit affichage pour t'aider à débugger
        # print(f"angle actuel: {angle:.3f} rad, {np.degrees(angle):.1f} deg")

        # --- 5. PREPARATION DE L'ACTION ---
        action = {
            "acceleration": 0.7,
            "steer": steering,
            "brake": False, 
            "drift": False,   # J'ai ajouté les virgules manquantes ici !
            "nitro": False,   # Ici aussi
            "rescue": False,  # Et ici
            "fire": False
        }
        
        # --- PARTIE ITEM (COMMENTÉE POUR L'INSTANT) ---
        # J'ai remis l'indentation correcte pour que tu puisses décommenter plus tard
        
        # if target_item_distance == 10:
        #     if obs['target_item_type'] in bad_type:
        #         if target_item_angle > 5: # obstacle a droite
        #             action["steer"] = -0.5 
        #             action["nitro"] = False
        #             action["acceleration"] -= 0.5 
        #         elif target_item_angle == 0: 
        #             action["steer"] = -0.5 
        #             action["nitro"] = False
        #             action["acceleration"] -= 0.5 
        #         elif target_item_angle < -5: # obstacle a gauche 
        #             action["steer"] = 0.5 
        #             action["nitro"] = False
        #             action["acceleration"] -= 0.5 
        #
        #     elif target_item_type in good_type:
        #         if target_item_angle < -5: # a gauche 
        #             action["steer"] = -0.5 
        #             action["nitro"] = True
        #             action["acceleration"] += 0.5 
        #         elif target_item_angle > 5: # a droite
        #             action["steer"] = 0.5 
        #             action["nitro"] = True
        #             action["acceleration"] += 0.5 

        return action
