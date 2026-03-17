import numpy as np
import random
from utils.track_utils import compute_curvature, compute_slope
from agents.kart_agent import KartAgent
from omegaconf import OmegaConf #ajouté S4
from .steering_piste import SteeringPiste
from .react_items import ReactionItems
from .rival_attack import AttackRivals
from .kart_rescue import StuckControl


cfg = OmegaConf.load("../agents/team2/configDemoPilote.yaml")

class Agent2(KartAgent):
    def __init__(self, env, path_lookahead=3):
        super().__init__(env)
        self.path_lookahead = path_lookahead
        self.steering = SteeringPiste(cfg)
        self.items_steering = ReactionItems(cfg)
        self.attack_rival = AttackRivals()
        self.rescue_kart = StuckControl(cfg)
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

    def detectVirage(self,obs):
        """ le but est de calculer l'angle qui definit les virages devant le kart
            ->la fonction renvoie un angle en radian 
        """
        noeuds_piste= obs["paths_start"]
        path_lookahead = 5
        noeud_cour= noeuds_piste[0]
        noeud_loin= noeuds_piste[path_lookahead]

        x1, z1 = noeud_cour[0], noeud_cour[2] #coordonnees pour angle
        x2, z2 = noeud_loin[0], noeud_loin[2]

        dx = x2 - x1 #coordonnées vecteur
        dz = z2 - z1

        angle= np.arctan2(dx,dz) #angle entre les vecteurs dx et dz en radian
        #print("angle:",angle)

        return angle

    def adapteAcceleration(self,obs):
        """
        le but va etre d'adpater l'acclération dans diverses situations dont notamment 
        les virages serrés, les virages moyens et les lignes droites --> cette fonction a fait appel à detectVirage() 
        """
        
        acceleration = 1.0
        curvature=abs(self.detectVirage(obs))

        if curvature > cfg.virages.drift:
                #0.27
            acceleration = 0.80
        elif curvature > cfg.virages.serrer.i1 and curvature <=cfg.virages.serrer.i2: # virage serré 
                #0.10
            acceleration= 0.85
        elif curvature > cfg.virages.moyen.i1 and curvature <= cfg.virages.moyen.i2:  #virage moyen 
                #0.05
            acceleration = 0.95
        else :
                #0.02
            acceleration = 1.0
        return acceleration 
    

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
        if obs["energy"][0]>0 and abs(steering) < 0.4:
            nitro=True
        else: 
            nitro=False
            
        #utiliser les cadeaux attrapés
        #if obs["items_type"][0]==0:
            #fire=True
        #else:
            #fire=False

        #Calcul de la correction pour rester au centre de la piste
        correction_piste = self.steering.correction_centrePiste(obs) # appel de la fonction de maintien sur la piste

        # ADAPTATION DE L'ACCELERATION SELON LE VIRAGE POUR NE PAS SORTIR DE LA PISTE
        acceleration = self.adapteAcceleration(obs)
        
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
