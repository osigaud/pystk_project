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
        self.name = "DemoPilote " 

        self.stuck_steps = 0    
        self.recovery_steps = 0  

    def reset(self):
        self.obs, _ = self.env.reset()
        self.agent_positions = []
        self.stuck_steps = 0
        self.recovery_steps = 0

    def endOfTrack(self):
        return self.isEnd
        
    
    def coorection_centrePiste(self, obs):
        """
        Calcule la correction nécessaire pour rester au centre de la piste.
        """
        #center_path contient le vecteur vers le centre de la route
        center_path = obs.get('path_start', np.array([0, 0, 0])) #si il y a 'path_start' alors center_path='center_path' sinon center_path est un vecteur par défaut mit a [0,0,0] jusqu'à qu'il retrouve le centre 
        
        dist_depuis_center = center_path[0] #center_path[0] c'es' le point X qui représente le décalage (gauche/droite) par rapport au centre
        
        correction = dist_depuis_center * 0.5 #On calcule une correction proportionnelle à la distance 0.5 est un bon compromit => dose la force du coup de volant (pas trop mou, pas trop violent)
        
        return np.clip(correction, -1.0, 1.0) #np.clip (=barrière de sécurité) sécurise pour que le res ne depasse pas l'intervalle (= les limites physiques du volant, car un volant ne tourne pas infiniment)
    
  
    def anticipeVirage(self):

        nodes_path = obs["paths_start"] #liste des neoud de la piste
        nb_nodes = len(nodes_path)
        path_lookahead = 5

        virages = [] #liste resultat pour stocker les virages detectes

        for i in range (nb_nodes - path_lookahead): #boucle pour le second (noeud loin=anticipation)

            curr_node = nodes_path[i] #le premier noeud quon rgd (noeud proche)
            lookahead_node = nodes_path[i+path_lookahead] #noeud loin
            self.path_lookahead = node_i + 1 # car indice commence a 0

            x1, z1 = current_node[0], current_node[2] #coordonnees pour angle
            x2, z2 = lookahead_node[0], lookahead_node[2]

            angle1 = np.arctan2(x1, z1)
            angle2 = np.arctan2(x2, z2)

            curvature = abs(angle2 - angle1)

            if curvature > 0.1:  # seuil à ajuster
                virages.append({ "index": i, "curvature": curvature })


        print("Virages détectés :", virages)

        return virage

    





    def choose_action(self, obs):
        if self.recovery_steps > 0:
            self.recovery_steps -= 1
            return {
                "acceleration": 0.0,
                "steer": 0.0,
                "brake": True,  
                "drift": False,
                "nitro": False,
                "rescue": False,
                "fire": False,
            }

        velocity = np.array(obs["velocity"])
        speed = np.linalg.norm(velocity)
        
        phase = obs.get("phase", 0) 
        
        if "paths_start" in obs:
            nodes_path = obs["paths_start"]
        else:
            nodes_path = [] 

        if phase > 2:  
            if speed < 0.2:  
                self.stuck_steps += 1
            else:
                self.stuck_steps = 0
               
        if self.stuck_steps > 7:
            self.recovery_steps = 15
            self.stuck_steps = 0

        angle = 0
        
        if len(nodes_path) > self.path_lookahead:
            target_node = nodes_path[self.path_lookahead]
            angle_target = np.arctan2(target_node[0], target_node[2])
            steering = np.clip(angle_target * 2, -1, 1)
            angle = angle_target 
        else:
            steering = 0
           
        # print(f"angle actuel: {angle:.3f} rad, {np.degrees(angle):.1f} deg") permet d afficher les angles à chaque frame 

        # CALCUL DE LA CORRECTION POUR RESTER AU CENTRE DE LA PISTE
        correction_piste = self.coorection_centrePiste(obs) # APPEL DE LA FONCTION DE MAINTIEN SUR PISTE

        # COMBINAISON DE LA DIRECTION DU CHEMIN ET DE LA CORRECTION DE PISTE
        final_steering = np.clip(steering + correction_piste, -1, 1) # ADDITION DES DEUX FORCES

        # ADAPTATION DE L'ACCELERATION SELON LE VIRAGE POUR NE PAS SORTIR DE LA PISTE
        acceleration = 0.8 if abs(final_steering) < 0.3 else 0.4 # RALENTIR SI ON TOURNE FORT

        action = {
            "acceleration": acceleration,
            "steer": final_steering,
            "brake": False, 
            "drift": False,  
            "nitro": False,  
            "rescue": False, 
            "fire": False
        }
        
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
