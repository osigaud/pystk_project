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
        self.rescue_kart = StuckControl()
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
        """ 
        permet de creer un dictionnaire pour faciliter la detection des differents types de virages à partir de deux noeuds 
        """
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

            curvature = abs(angle1 - angle2)

            if curvature > cfg.curvature :  # seuil à ajuster
                virages.append({ "index": i, "curvature": curvature })

        return virages

    def adapteAcceleration(self,obs):
        """le but va etre d'adpater l'acclération dans diverses situations dont notamment 
        les virages serrés, les virages moyens et les lignes droites --> cette fonction a fait appel à detectViragz """
        
        liste_virage=self.detectVirage(obs)
        acceleration= 1.0
        if len(liste_virage) < 1 :  # s'il n'y a pas de virage 
            acceleration = cfg.acceleration.sans_virage  # conduite normale on pourrait augmenter légèrement l'accélération -> à décider 
        else : 
            proche_virage = liste_virage[0]
            curvature = abs(proche_virage["curvature"])
            if curvature > cfg.virages.drift:
                #0.27
                acceleration = acceleration - 0.20
            elif curvature > cfg.virages.serrer.i1 and curvature <=cfg.virages.serrer.i2: # virage serré 
                #0.10
                acceleration= acceleration - 0.05
            elif curvature > cfg.virages.moyen.i1 and curvature <= cfg.virages.moyen.i2:  #virage moyen 
                #0.05
                acceleration = acceleration - 0.02
            else :
                #0.02
                acceleration = acceleration - 0.01
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
