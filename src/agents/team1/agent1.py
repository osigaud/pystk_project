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
            "acceleration": 0.2, 
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
            
#Agent qui adapte la vitesse en fonction des virages
class AgentTurn(AgentCenter):
    def __init__(self, env, dist, ajust, ecartpetit, ecartgrand, longpetite, longgrande, msapetit, msagrand):
        super().__init__(env, dist, ajust)
        self.ecartpetit = ecartpetit #seuil a partir du quel on considere l'ecart comme petit (ligne droite)o
        self.ecartgrand = ecartgrand #seuil a partir du quel on considere l'ecart comme grand (virage serré)
        self.longpetite = longpetite #seuil a partir du quel on considere le segment comme court
        self.longgrande = longgrande #seuil a partir du quel on considere le segment comme long
        self.msapetit = msapetit
        self.msagrand = msagrand
        
    def analyse(self, obs):
        s = []
       	nbsegments = min(self.path_lookahead, len(obs["paths_start"]))
       	for i in range(nbsegments):
       		segdirection = obs["paths_end"][i] - obs["paths_start"][i]
       		diff = segdirection - obs["front"]
       		ecart = math.sqrt(diff[0]**2 + diff[1]**2 + diff[2]**2)
       		seglong = obs["paths_distance"][i][1] - obs["paths_distance"][i][0]
        		
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
        		
    def reaction(self, react, act, obs):
		msa = obs["max_steer_angle"]
		
		if react == "ligne droite":
			act["acceleration"] = 1
			return act
			
		if react == "virage leger":
			
			if msa <= self.msapetit: 
				accel = act["acceleration"]
				accel = accel - 0.2
				act["acceleration"] = accel
				return act
			elif self.msapetit < msa < self.msagrand:
				return act
			elif msa >= self.msagrand:
				accel = act["acceleration"]
				accel = accel + 0.4
				act["acceleration"] = accel
				return act
				
		if react == "virage serre":
			
			if msa <= self.msapetit: 
				accel = act["acceleration"]
				accel = accel - 0.4
				act["acceleration"] = accel
				return act
			elif self.msapetit < msa < self.msagrand:
				return act
			elif msa >= self.msagrand:
				accel = act["acceleration"]
				accel = accel + 0.2
				act["acceleration"] = accel
				return act
				
    def choose_action(self, obs):
		act = super().choose_action(obs)
		react = self.analyse(obs)
		act_corr = self.reaction(react, act, obs)
		return act_corr

#AGENT FINAL :
class Agent1(AgentCenter):
    def __init__(self, env, path_lookahead=3): 
    	ecartgrand = 3
    	ecartpetit = 1
    	msagrand = 0.7
    	msapetit = 0.2
        dist = 0.5
        ajust = 0.25      
        super().__init__(env, dist, ajust)
