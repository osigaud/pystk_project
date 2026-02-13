import numpy as np
import random
import math
from omegaconf import OmegaConf

from utils.track_utils import compute_curvature, compute_slope
from agents.kart_agent import KartAgent

from pathlib import Path

#chemin du fichier de configuration
path_conf = Path(__file__).resolve().parent
path_conf = str(path_conf) + '/configFIleTastyCrousteam.yaml'
#importation du fichier de configuration
conf = OmegaConf.load(path_conf)

#définition des variables qui viennent du fichier de configuration
DIST = conf.dist
AJUST = conf.ajust
ECARTPETIT = conf.ecartpetit
ECARTGRAND = conf.ecartgrand
MSAPETIT = conf.msapetit
MSAGRAND = conf.msagrand

#autres variables qu'on utilise dans le code 
BONUS = [0, 2, 3]
OBSTACLES = [1, 4]

#template de base d'Agent, mouvements aléatoires, initialisation des variables
class AgentInit(KartAgent):
    #variables à définir dans le fichier de configuration : 
    #   - accélération par défaut
    def __init__(self, env, path_lookahead=3):
        super().__init__(env)
        self.path_lookahead = path_lookahead
        self.agent_positions = []
        self.obs = None
        self.isEnd = False
        self.name = "Tasty Crousteam"

    def reset(self):
        self.obs, _ = self.env.reset()
        self.agent_positions = []

    def endOfTrack(self):
        return self.isEnd

    def choose_action(self, obs):
        acceleration = random.random()
        steering = random.random()
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
class AgentCenter(AgentInit):
    def __init__(self, env, path_lookahead=3):
        super().__init__(env, path_lookahead)
        self.dist = DIST #écart max au centre de la piste qu'on accepte
        self.ajust = AJUST #la valeur que l'on veut addi/soustr à notre steer, qui sert d'ajustement de la trajectoire

    def path_ajust(self, act, obs):
        s = act["steer"]
        center = obs["paths_end"][2]
        """
        # gros ecart -> gros virage
        if center < -self.dist:
            s = s - self.ajust
        elif center > self.dist:
            s = s + self.ajust

        # petit ecart -> petit virage
        elif center < -self.dist / 2:
            s = s - self.ajust / 2
        elif center > self.dist / 2:
            s = s + self.ajust / 2
        """
        if (center[2] > 20 and abs(obs["center_path_distance"]) < 3) : 
            act["steer"] = 0
        else : 
            act["steer"] = center[0]
        return act
    
    def choose_action(self, obs):
        act = super().choose_action(obs)
        act_corr = self.path_ajust(act, obs)
        return act_corr
            
#Agent qui adapte la vitesse en fonction des virages
class AgentSpeed(AgentCenter):
    def __init__(self, env, path_lookahead=3):
        super().__init__(env, path_lookahead)
        self.ecartpetit = ECARTPETIT #seuil a partir du quel on considere l'ecart comme petit (ligne droite)o
        self.ecartgrand = ECARTGRAND #seuil a partir du quel on considere l'ecart comme grand (virage serré)
        self.msapetit = MSAPETIT
        self.msagrand = MSAGRAND
        
    def analyse(self, obs):
        s = []
       	nbsegments = min(self.path_lookahead, len(obs["paths_start"]))
       	for i in range(nbsegments):
       		segdirection = obs["paths_end"][i] - obs["paths_start"][i]
       		diff = segdirection - obs["front"]
       		ecart = float(np.linalg.norm(diff))
       		dist = abs(obs["paths_distance"][i][0] - obs["paths_distance"][0][0])
        		
        	if ecart >= self.ecartgrand and dist < 10:
        		s.append("virage serre")
       		elif ecart <= self.ecartpetit:
       			s.append("ligne droite") 
        	
       	react = "ligne droite"
       	if "virage serre" in s: 
       		react = "virage serre"
       		return react
       	else: 
       		return react

    def gap(self, acceleration) : 
        if acceleration >= 1 : 
            return 1
        if acceleration <= 0 : 
            return 0.1
        return acceleration
        		
    def reaction(self, react, act, obs):
        msa = obs["max_steer_angle"]
            
        if react == "ligne droite":
            act["acceleration"] = 1
            
            segdirection = obs["paths_end"][0] - obs["paths_start"][0]
            if segdirection[1] > 0.05:
            	act["acceleration"] = self.gap(act["acceleration"] + 0.2)
            	
            return act
                    
        if react == "virage serre":
            if msa <= self.msapetit: 
                accel = act["acceleration"]
                accel = accel - 0.45
                act["acceleration"] = self.gap(accel)
            elif self.msapetit < msa < self.msagrand:
            	return act
            elif msa >= self.msagrand:
                accel = act["acceleration"]
                accel = accel + 0.5
                act["acceleration"] = self.gap(accel)
                
            segdirection = obs["paths_end"][0] - obs["paths_start"][0]
            if segdirection[1] > 0.05:
            	act["acceleration"] = self.gap(act["acceleration"] + 0.2)
            	
            return act
  
    def choose_action(self, obs):
        act = super().choose_action(obs)
        react = self.analyse(obs)
        act_corr = self.reaction(react, act, obs)
        return act_corr

#Agent qui analyse les obstacles et bonus sur la course et corrige sa trajectoire en conséquences
class AgentObstacles(AgentCenter) : 

    def observation_next_item(self, obs, action) : 
        """
        Observe à quel point le prochain item est proche, appelle la méthode adaptée en fonction de son type
        """
        nextitem_type = obs["items_type"][0]
        nextitem_vector = obs["items_position"][0]

        if nextitem_vector[2] < 17 and nextitem_vector[2] > 3 and abs(nextitem_vector[1]) < 10 : 
            if nextitem_type in BONUS : 
                return self.dirige_bonus(obs, action)
            elif nextitem_type in OBSTACLES : 
                return self.evite_obstacle(obs, action)
        return action

    #Corrections à apporter sur cette méthode
    def evite_obstacle(self, obs, action) : 
        """
        Evite le prochain item, sauf si on a un shield équipé
        NE MARCHE PAS ! la méthode n'est jamais appelée par notre agent en attendant de la réparer
        """
        #if (obs["attachment"] == 6 and obs["attachment_time_left"] > 2) : 
        #    #6 : BUBBLEGUM_SHIELD
        #    print("j'évite pas car j'ai un shield")
        #    return action

        #vecitem = obs["items_position"][0] 
        #if abs(vecitem[0]) < 1.5 :
        #    action["steer"] = action["steer"] + 0.5
        return action

    def dirige_bonus(self, obs, action) :
        """
        Dirige vers le prochain item, qui est un bonus
        """
        item_vector = obs["items_position"][0]
        next_node = obs["paths_end"][0]
        node_item_gap_vector = next_node - item_vector
        if node_item_gap_vector[2] < next_node[2] and node_item_gap_vector[2] > 0 : 
            if abs(item_vector[0] - action["steer"]) < 0.2 :
                return action
            else : 
                action["steer"] = item_vector[0]
                return action
        return action
        
    def choose_action(self, obs) : 
        """
        Renvoie le dictionnaire d'action de notre agent, corrigé après avoir pris en compte les obstacles
        et bonus devant
        """
        action = super().choose_action(obs)
        action_corrigee = self.observation_next_item(obs, action)
        return action_corrigee

class AgentRescue(AgentObstacles) : 
    #Prendre le cas en compte où on est étourdi par un item dans is_blocked
    def __init__(self, env, path_lookahead=3): 
        super().__init__(env, path_lookahead)  
        self.last_distance = None
        self.block_counter = 0
        self.unblock_steps = 0
        self.is_braking = False

    def is_blocked(self, obs):
        """
        Paramètres : obs
        Incrémente self.block_counter si le kart n'a pas bougé
        """
        distance_down_track = obs["distance_down_track"][0]
        if self.last_distance is None :
            self.last_distance = distance_down_track

        if abs(distance_down_track - self.last_distance) < 0.1 and distance_down_track > 5 and (obs["jumping"] == 0) :
            self.block_counter += 1
        else:
            self.block_counter = 0
            self.last_distance = distance_down_track

    def unblock_action(self, act):
        """
        Paramètres : act (dict)
        Renvoie : act (dict), modifié si on doit reculer
        """
        if self.unblock_steps > 0 : 
            self.unblock_steps -= 1
            return {
                "acceleration" : 0, 
                "steer" : 0, 
                "brake" : True,
                "drift" : False,
                "nitro" : False,
                "rescue" : False,
                "fire" : False,
            }
        else : 
            self.is_braking = False
            return act
    
    def choose_action(self, obs):
        """
        Paramètres : obs
        Renvoie : action (dict), le dictionnaire d'actions de notre kart
        """
        self.is_blocked(obs)
        action = super().choose_action(obs)   
                
        if self.block_counter > 10 :
            self.is_braking = True
            self.unblock_steps = 4
        if self.is_braking : 
            action = self.unblock_action(action)
        return action