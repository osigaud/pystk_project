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
DIST = 0.673833673012193
AJUST = 0.6386812473361506
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
        self.dist = DIST 
        self.ajust = AJUST 

    def path_ajust(self, act, obs):
        """
        Paramètres : obs, act (dict)
        Renvoie : act (dict), dictionnaire des actions du kart corrigé pour suivre le centre de la piste
        """
        steer = act["steer"]
        center = obs["paths_end"][2]
        if (center[2] > 20 and abs(obs["center_path_distance"]) < 3) : 
            steer = 0
        elif abs(center[0]) > self.dist : 
            steer += self.ajust * center[0]
        act["steer"] = np.clip(steer, -1, 1)
        return act
    
    def choose_action(self, obs):
        """
        Paramètres : obs
        Renvoie : act (dict), le dictionnaire d'action après correction
        """
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

    def __init__(self, env, path_lookahead=3): 
        super().__init__(env, path_lookahead)
        self.target_obstacle = None
        self.target_item = None

    def observation_next_item(self, obs, action) : 
        """
        Paramètres : obs, action (dict)
        Renvoie : action (dict), le dictionnaire d'actions corrigé après avoir pris en compte les items sur la piste
        """
        tab_bonus = [i for i in range(len(obs["items_type"])) if obs["items_type"][i] in BONUS]
        tab_obstacles = [i for i in range(len(obs["items_type"])) if obs["items_type"][i] in OBSTACLES]

        """
        for i in range(len(obs["items_type"])) :
            nextitem_type = obs["items_type"][i]
            #if nextitem_vector[2] < 17 and nextitem_vector[2] > 3 and abs(nextitem_vector[1]) < 10 : 
            if nextitem_type in BONUS : 
                action = self.take_bonus(obs, action)
            elif nextitem_type in OBSTACLES : 
                return action
                action = self.dodge_obstacle(obs, action)
        """
        for index in tab_obstacles :
            action = self.dodge_obstacle(obs, action, index)

        for index in tab_bonus : 
            action = self.take_bonus(obs, action, index)
        return action

    def dodge_obstacle(self, obs, action, index) : 
        """
        Paramètres : obs, action (dict), index
        Renvoie : action (dict), après avoir pris en compte le prochain obstacle (sauf si on a un SHIELD équipé)
        """
        if self.target_obstacle is None : 
            self.target_obstacle = index

        item_vector = obs["items_position"][index]
        if -1 < item_vector[2] < 1 or not ((abs(item_vector[0]) < 3.5) and (0 < item_vector[2] < 20) and (abs(item_vector[1]) < 10)): 
            self.target_obstacle = None

        if (self.target_obstacle == index):
            if (obs["attachment"] == 6 and obs["attachment_time_left"] > 2) : 
                #6 : BUBBLEGUM_SHIELD
                #à tester ici quand on aura un shield activé
                return action
    
            if item_vector[0] >= 0 : 
                action["steer"] = action["steer"] - 1
            else : 
                action["steer"] = action["steer"] + 1
        return action

    def take_bonus(self, obs, action, index) :
        """
        Paramètres : obs, action (dict), index
        Renvoie : action (dict), après avoir pris en compte le prochain bonus pour se diriger vers celui-ci
        """
        if self.target_item is None : 
            self.target_item = index

        item_vector = obs["items_position"][index]
        if item_vector[2] < 3 or not((abs(item_vector[0]) < 3) and (3 < item_vector[2] < 16) and (abs(item_vector[1]) < 10)) : 
            self.target_item = None

        next_node = obs["paths_end"][self.path_lookahead]
        node_item_gap_vector = next_node - item_vector #vecteur pour mesurer l'écart entre l'item et le prochain noeud
        #si l'écart est trop grand, on ne détourne pas du chemin de base

        if (self.target_item == index) and (node_item_gap_vector[2] <= (next_node[2] - 1)) and (self.target_obstacle is None) :
            next_node = obs["paths_end"][0]
            node_item_gap_vector = next_node - item_vector
            #if 0 < node_item_gap_vector[2] < next_node[2] : #optimisation ici ? 
            #if abs(item_vector[0] - action["steer"]) < 0.1 :
                #return action
            #else : 
            action["steer"] = item_vector[0]
        return action
        
    def choose_action(self, obs) : 
        """
        Paramètres : obs
        Renvoie : action (dict), dictionnaire d'actions corrigé après prise en compte des obstacles et bonus
        """
        action = super().choose_action(obs)
        action = self.observation_next_item(obs, action)
        return action

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
        attachment = obs["attachment"]
        if self.last_distance is None :
            self.last_distance = distance_down_track

        if abs(distance_down_track - self.last_distance) < 0.1 and distance_down_track > 5 and (obs["jumping"] == 0) and not (attachment == 2) :
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
                
        if self.block_counter > 18 :
            self.is_braking = True
            self.unblock_steps = 4
        if self.is_braking : 
            action = self.unblock_action(action)
        return action