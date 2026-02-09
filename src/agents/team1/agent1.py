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
    def __init__(self, env, path_lookahead=3):
        super().__init__(env, path_lookahead)

    def choose_action(self, obs):
        action = {
            "acceleration": 0.7, 
            "steer": 0, 
            "brake": False, 
            "drift": False, 
            "nitro": False, 
            "rescue": False, 
            "fire": False, 
        }
        return action

#Agent qui suit le centre de la piste

#A CORRIGER : plein de zigzag, attendre mardi pour voir avec Wiam 
class AgentCenter(AgentStraight):
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
class AgentTurn(AgentCenter):
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
       		ecart = math.sqrt(diff[0]**2 + diff[1]**2 + diff[2]**2)
        		
        	if ecart >= self.ecartgrand:
        		s.append("virage serre")
       		elif self.ecartgrand > ecart > self.ecartpetit:
       			s.append("virage leger")
       		elif ecart <= self.ecartpetit:
       			s.append("ligne droite") 
        	
       	react = "ligne droite"
       	if "virage serre" in s: 
       		react = "virage serre"
       		return react
        elif "virage leger" in s: 
        	react = "virage leger"
        	return react
       	else: 
       		return react

    def gap(self, acceleration) : 
        if acceleration >= 1 : 
            return 0.9
        if acceleration <= 0 : 
            return 0.1
        return acceleration
        		
    def reaction(self, react, act, obs):
        msa = obs["max_steer_angle"]
            
        if react == "ligne droite":
            act["acceleration"] = 0.7
            return act
                
        if react == "virage leger":
            if msa <= self.msapetit: 
                accel = act["acceleration"]
                accel = accel + 0.2
                act["acceleration"] = self.gap(accel)
                return act
            elif self.msapetit < msa < self.msagrand:
                return act
            elif msa >= self.msagrand:
                accel = act["acceleration"]
                accel = accel - 0.2
                act["acceleration"] = self.gap(accel)
                return act
                    
        if react == "virage serre":
            if msa <= self.msapetit: 
                accel = act["acceleration"]
                accel = accel - 0.3
                act["acceleration"] = self.gap(accel)
                return act
            elif self.msapetit < msa < self.msagrand:
                return act
            elif msa >= self.msagrand:
                accel = act["acceleration"]
                accel = accel + 0.3
                act["acceleration"] = self.gap(accel)
                return act
  
    def choose_action(self, obs):
        act = super().choose_action(obs)
        react = self.analyse(obs)
        act_corr = self.reaction(react, act, obs)
        print("nextitem :", obs["items_position"][0])
        return act_corr

#Agent qui analyse les obstacles et bonus sur la course et corrige sa trajectoire en conséquences
class AgentObstacles(AgentCenter) : 
    def __init__(self, env, path_lookahead=3) : 
        super().__init__(env, path_lookahead)

    def obs_next_item(self, obs, action) : 
        nextitem = obs["items_type"][0]
        vecitem = obs["items_position"][0]
        if vecitem[2] < 8 and vecitem[2] > 2 : 
            if nextitem in BONUS : 
                return self.dirige_bonus(obs, action)
            elif nextitem in OBSTACLES : 
                return self.evite_obstacle(obs, action)
        return action

    def evite_obstacle(self, obs, action) : 
        if (obs["attachment"] == 6 and obs["attachment_time_left"] > 2) : 
            #6 : BUBBLEGUM_SHIELD
            return action
        vecitem = obs["items_position"][0] 
        if vecitem[0] < 0.2 :
            action["steer"] = action["steer"] + 0.3
        return action

    def dirige_bonus(self, obs, action) :
        vecitem = obs["items_position"][0]
        if abs(vecitem[0] - action["steer"]) < 0.2 :
            return action
        else : 
            action["steer"] = vecitem[0]
        return action
        
    def choose_action(self, obs) : 
        action = super().choose_action(obs)
        action_corr = self.obs_next_item(obs, action)
        return action_corr

#AGENT FINAL :
class Agent1(AgentCenter):
    def __init__(self, env, path_lookahead=3): 
        super().__init__(env,path_lookahead)

        #Anti-block state   
        self.last_distance = None
        self.block_counter = 0
        self.unblock_steps = 0

    def is_bloqued(self, obs):
        """Observer si il est bloque """
        dist = obs["distance_down_track"][0]

        if self.last_distance is None:
            self.last_distance = dist
            return False

        #si la distance ne change pas -> bloque
        if abs(dist - self.last_distance) < 0.01:
            self.block_counter += 1
        else:
            self.block_counter = 0
        
        self.last_distance = 0

        #Bloque dans 10 steps
        return self.block_counter > 10

    def unblock_action(self):
        """Action utilisee pour debloquer le kart: reverse +slight steering"""
        return {
            "acceleration" : -0.6,                  # reculer
            "steer" : random.choice([-0.4,0.4]),    # tourner pour se degager
            "brake" : False,
            "drift" : False,
            "nitro" : False,
            "rescue" : False,
            "fire" : False,
        }
    
    def choose_action(self, obs):
        # 1. si on est en phase de debloquage
        if self.unblock_steps > 0:
            self.unblock_steps -= 1
            return self.unblock_action()
        
        # 2. debloque
        if self.is_bloqued(obs):
            #print(" Agent bloque -> Recul automatique ")
            self.unblock_steps = 15   # ~0.5s de recul
            return self.unblock_action()

        # 3. lancer normalement si il n'est pas bloque
        return super().choose_action(obs)