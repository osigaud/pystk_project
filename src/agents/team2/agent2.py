import numpy as np
import random
from utils.track_utils import compute_curvature, compute_slope
from agents.kart_agent import KartAgent
from omegaconf import OmegaConf #ajouté S4


config= OmegaConf.load("../agents/team2/configDemoPilote.yaml")

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
        
    
    def correction_centrePiste(self, obs):
        """
        Calcule la correction nécessaire pour rester au centre de la piste.
        """
        #center_path contient le vecteur vers le centre de la route
        center_path = obs.get('path_start', np.array([0, 0, 0])) #si il y a 'path_start' alors center_path='path_start' sinon center_path est un vecteur par défaut mit a [0,0,0] jusqu'à qu'il retrouve le centre 
        
        dist_depuis_center = center_path[0] #center_path[0] c'est le point X qui représente le décalage (gauche/droite) par rapport au centre
        
        correction = dist_depuis_center * config.correction #On calcule une correction proportionnelle à la distance 0.5 est un bon compromit => dose la force du coup de volant (pas trop mou, pas trop violent)
        
        return np.clip(correction, -1.0, 1.0) #np.clip (=barrière de sécurité) sécurise pour que le res ne dépasse pas l'intervalle (= les limites physiques du volant, car un volant ne tourne pas infiniment)
    

    def detectVirage(self,obs):

        nodes_path = obs["paths_start"] #liste des neoud de la piste
        nb_nodes = len(nodes_path)
        path_lookahead = 5

        virages = [] #liste resultat pour stocker les virages detectes

        for i in range (nb_nodes - path_lookahead): #boucle pour le second (noeud loin=anticipation)

            curr_node = nodes_path[i] #le premier noeud qu'on rgd (noeud proche)
            lookahead_node = nodes_path[i+path_lookahead] #noeud loin

            x1, z1 = curr_node[0], curr_node[2] #coordonnees pour angle
            x2, z2 = lookahead_node[0], lookahead_node[2]

            angle1 = np.arctan2(x1, z1)
            angle2 = np.arctan2(x2, z2)

            curvature = abs(angle2 - angle1)

            if curvature > config.curvature :  # seuil à ajuster
                virages.append({ "index": i, "curvature": curvature })



        return virages

    def adapteAcceleration(self,obs):
        #le but va etre d'adpater l'acclération dans diverses situations dont notamment 
        #les virages serrés, les lignes droites ou une legere curvature 
        liste_virage=self.detectVirage(obs)
        acceleration= 1.0
        if len(liste_virage) < 1 :  # s'il n'y a pas de virage 
            acceleration = config.acceleration.sans_virage  # conduite normale on pourrait augmenter légèrement l'accélération -> à décider 
        else : 
            proche_virage = liste_virage[0]
            curvature = proche_virage["curvature"]
            #print (curvature) # permet d afficher la variation des angles pour determiner les courbures 
            if curvature > config.virages.drift:
                #drift = True
                acceleration = acceleration - 0.27
            elif curvature > config.virages.serrer.i1 and curvature <=config.virages.serrer.i2: # virage serré 
                acceleration= acceleration - 0.10
                #drift = False 
            elif curvature > config.virages.moyen.i1 and curvature <= config.virages.moyen.i2:  #virage moyen 
                acceleration = acceleration - 0.05
                #drift = False
            else :
                acceleration = acceleration - 0.02
                #drift = False
        return acceleration #drift 
    #on travaillera sur les drifts apres depuis cette fonction 

    def reaction_items(self, obs):
        items_pos = obs.get('items_position', [])            
        items_type = obs.get('items_type', [])
        steering_adjustment = 0.0

        GOOD_ITEM_IDS = [0, 2, 3, 6]  # BONUS_BOX, NITRO_BIG, NITRO_SMALL, EASTER_EGG
        best_good_dist = 1000.0 # tres grand nombre qui sert comme point de base

        angle_evite = 0.0
        dist_min_evite = 15.0

        for i, pos in enumerate(items_pos):#le sert à faire le lien entre la position de l'item qu'on regarde et son type
            pos = np.array(pos)
            dist = np.linalg.norm(pos)

            # items derriere ou trop loin => ignorer
            if pos[2] < 0 or dist > 25.0:
                continue

            item_type = items_type[i] if i < len(items_type) else None

            # prendre le meilleur "good" item le plus proche
            if item_type in GOOD_ITEM_IDS:
                if dist < best_good_dist:
                    best_good_dist = dist
                    angle = np.arctan2(pos[0], pos[2])
                    steering_adjustment = float(np.clip(angle * 2, -0.5, 0.5))#adapter cette partie aux differentes pistes
            else:
                # éviter les bad items proches
                if dist < dist_min_evite:
                    angle_evite = -0.61 if pos[0] > 0 else 0.61

        if abs(angle_evite) > 0:
            return angle_evite
        return steering_adjustment



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


        if phase > 3:  
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


        # Calcul de la correctio pour rester au centre de la piste
        correction_piste = self.correction_centrePiste(obs) # appel de la fonction de maintien sur la piste

        # ADAPTATION DE L'ACCELERATION SELON LE VIRAGE POUR NE PAS SORTIR DE LA PISTE
        acceleration = self.adapteAcceleration(obs)
        
        item_steering = self.reaction_items(obs)

        final_steering = np.clip(item_steering+ correction_piste+ steering, -1, 1)

        action = {
            "acceleration": acceleration,
            "steer": final_steering,
            "brake": False, 
            "drift": False, 
            "nitro": False,  
            "rescue": False, 
            "fire": False,
        }
        #print(obs["phase"])
        return action
