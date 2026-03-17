import numpy as np
import random
from utils.track_utils import compute_curvature, compute_slope
from agents.kart_agent import KartAgent
from omegaconf import OmegaConf 
from .steering_piste import SteeringPiste
from .react_items import ReactionItems
from .rival_attack import AttackRivals
from .kart_rescue import StuckControl
from .acceleration_kart import AccelerationControl

cfg = OmegaConf.load("../agents/team2/configDemoPilote.yaml")

class Agent2(KartAgent):
    def __init__(self, env, path_lookahead=3):
        super().__init__(env)
        self.path_lookahead = path_lookahead
        self.steering = SteeringPiste(cfg)
        self.items_steering = ReactionItems(cfg)
        self.attack_rival = AttackRivals()
        self.rescue_kart = StuckControl(cfg)
        self.acceleration = AccelerationControl(cfg)
        self.agent_positions = []
        self.obs = None
        self.isEnd = False
        self.name = "DemoPilote " 

        
    def reset(self):
        self.obs, _ = self.env.reset()
        self.agent_positions = []
        self.stuck_steps = 0
        self.recovery_steps = 0

    def endOfTrack(self):
        return self.isEnd

    def choose_action(self, obs):
        velocity = np.array(obs["velocity"])
        speed = np.linalg.norm(velocity)
        
        action_secours = self.rescue_kart.gerer_recul(obs, speed, self.steering)
        if action_secours is not None:
            return action_secours
            
        phase = obs.get("phase", 0) 
        
        if "paths_start" in obs:
            nodes_path = obs["paths_start"]
        else:
            nodes_path = [] 

        angle = 0
        
        if len(nodes_path) > self.path_lookahead:
            target_node = nodes_path[self.path_lookahead]
            angle_target = np.arctan2(target_node[0], target_node[2])
            steering = np.clip(angle_target * 2, -1, 1)
            angle = angle_target 
        else:
            steering = 0
        
        #eviter les murs/ revenir sur la piste si kart bloqué
        if abs(obs["center_path_distance"])> obs["paths_width"][0]/2:
            rescue=True
        else:
            rescue=False

        #utiliser les boost: (nitro->pour activer bouteille bleu, fire->pour activer les cadeaux)
        if obs["energy"][0]>0 and abs(steering) < 0.2:
            nitro=True
        else: 
            nitro=False
            
        #Calcul de la correction pour rester au centre de la piste
        correction_piste = self.steering.correction_centrePiste(obs) # appel de la fonction de maintien sur la piste

        # ADAPTATION DE L'ACCELERATION SELON LE VIRAGE POUR NE PAS SORTIR DE LA PISTE
        acceleration = self.acceleration.adapteAcceleration(obs)
        
        item_steering = self.items_steering.reaction_items(obs)

        final_steering = np.clip(item_steering+ correction_piste+ steering, -1, 1)

        has_item = obs.get("attachment", 0) != 0 #0 si il ne possede pas l'item
        fire = has_item and self.attack_rival.attack_rivals(obs) 

        action = {
            "acceleration": acceleration,
            "steer": final_steering,
            "brake": False, 
            "drift": False, 
            "nitro": nitro,  
            "rescue": rescue, 
            "fire": fire,
        }
        
        return action
