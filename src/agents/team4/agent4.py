from utils.track_utils import compute_curvature, compute_slope
from agents.kart_agent import KartAgent
from .steering import Steering
from .rescue import RescueManager
from .speed import SpeedController
from .nitro import Nitro
from .banana_detection import Banana
from .esquive_adv import EsquiveAdv
from omegaconf import OmegaConf
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent # On obtient le chemin absolu vers notre fichier agent4
CONFIG_PATH = BASE_DIR / "configuration.yaml" # On dit que notre fichier de config se trouve aussi ici

conf = OmegaConf.load(str(CONFIG_PATH)) # On charge le fichier de config


class Agent4(KartAgent):
    """
    Module Agent4 : Gère la logique général de pilotage de l'agent
    """

    def __init__(self, env, path_lookahead=3):
        """Initialise les variables d'instances de l'agent."""
        super().__init__(env)
        self.path_lookahead = path_lookahead
        self.agent_positions = []
        self.obs = None
        self.isEnd = False
        self.name = "The Winners"
        self.steering = Steering()
        self.rescue = RescueManager()
        self.SpeedController=SpeedController()
        self.nitro = Nitro()
        self.esquive_adv = EsquiveAdv()
        self.banana_dodge = Banana()
        self.dodge_side = 0
        self.dodge_timer = 0
        self.lock_mode = None
        self.locked_gx = 0.
        print(OmegaConf.to_yaml(conf))
        
        
    def reset(self):
        """Réinitialise les variables d'instances de l'agent en début de course."""
        self.obs, _ = self.env.reset()
        self.agent_positions = []
        self.dodge_timer = 0
        self.dodge_side = 0
        self.lock_mode = None
        self.locked_gx = 0.0
        self.rescue = RescueManager()

    def endOfTrack(self):
        """Indique si la course est fini"""
        return self.isEnd

    def choose_action(self, obs):
        """
        Calcule les différentes actions à réaliser en fonction des observations
        et des conditions reçues.
        
        Args:
            obs (dict): Les données fournies par le simulateur.
            
        Returns:
            dict: Le dictionnaire d'actions pour le moteur physique.
        """
        
        
        points = obs.get("paths_start",[]) # On récupère la liste des points
        
        if len(points) <= 2: # Si la longueur de la liste est inferieur à 2, on accèlère à fond (ligne d'arrivée proche)
            return {
                "acceleration": 1.0,
                "steer": 0.0,
                "brake": False,
                "drift": False,
                "nitro": True,
                "rescue":False,
                "fire": False,
            }
        
        target = points[2] # On récupère le deuxième point de la liste
        gx = target[0] # On récupère x, le décalage latéral
        gz = target[2] # On récupère z, la profondeur

        paths_width = obs.get("paths_width",0.0)
        center_path_distance = obs.get("center_path_distance",0.0)
        limit_path = paths_width[0]/2
        #print(center_path_distance)

        gain_volant = 7.0  #Gain par défaut
        
        mode, b_x, banana_list = self.banana_dodge.banana_detection(obs,limit_path,center_path_distance) # Appel de la fonction de detection

        if mode == "SINGLE" and self.lock_mode != "LIGNE": # Si on a capte un cas d'une banane seule et qu'on était pas déjà dans une situation d'esquive de barrage

            #Sécurité pour éviter de sortir de la piste
            if (limit_path - abs(center_path_distance)) <= 1.5 :
                print("choix par limite de bord")
                #print(limit_path, center_path_distance)
                
                # ATTENTION LOGIQUE INVERSEE POUR CENTER PATH, si > 0 l'agent se situe à droite de la piste
                if center_path_distance >= 0:
                    new_side = -1
                else:
                    new_side = 1
            else:   
                print("choix normal")
                if b_x>=0:
                    new_side = -1
                    
                else:
                    new_side = 1
            
            # Utilisation d'un compteur pour maintenir le cap d'esquive sur x frames
            if self.dodge_timer == 0 or (self.lock_mode == "SINGLE" and self.dodge_side != new_side):
                self.lock_mode = "SINGLE"
                self.dodge_timer = 10
                self.dodge_side = new_side

        elif mode == "LIGNE": #Si on a capte un mode ligne
            self.lock_mode = "LIGNE"
            self.dodge_timer = 0
            self.locked_gx = b_x
            #print(banana_list)
            #print("Esquive Ligne")

        if self.dodge_timer >0: # On est dans le mode Single
            self.dodge_timer -= 1 # On decremente le compteur
            gx += 3.0 * self.dodge_side # On cree le decalage pour le cas single
            
        elif (mode == "SINGLE" or mode == "LIGNE") and self.lock_mode == "LIGNE":
            gx = self.locked_gx # On vise le gap calculé pour le mode ligne
            gain_volant = 6.0 # Ajustement du gain pour le mode ligne
        
        else:
            self.lock_mode = None
            danger_adv, a_x,a_z = self.esquive_adv.esquive_adv(obs)
            
            if danger_adv:
                if a_x >= 0:
                    gx -= 2.0 # On se décale à gauche 
                else:
                    gx += 2.0 # On se décale à droite
            
            
        steering = self.steering.manage_pure_pursuit(gx,gz,gain_volant) # Appel à la fonction pure_pursuit en condition normale (pas de danger detecté)
        
        epsilon = 0.05
        
        road_straight = abs(points[2][0]) < 0.8

        # Pour eviter les vibrations, si on est sur une ligne droite et dans aucun cas d'esquive, on met le steering à 0
        if road_straight and abs(steering) <= epsilon and self.lock_mode == None and not danger_adv:
            steering = 0.0
        
        distance = float(obs.get("distance_down_track", [0.0])[0])
        vel = obs.get("velocity", [0.0, 0.0, 0.0])
        speed = float(vel[2])
        energy = float(obs.get("energy", [0.0])[0])
    
        drift = False
        brake = False
        acceleration, brake = self.SpeedController.manage_speed(steering,speed,drift,conf) # Appel à la fonction gerer_vitesse
        #print("speed_out:", self.SpeedController.manage_speed(steering, obs))
        
        nitro = False
        nitro = self.nitro.manage_nitro(steering,energy,obs) # Appel à la fonction gerer_nitro
       
        if(self.rescue.is_stuck(distance,speed)): # Si on est bloque, on appelle la fonction rescue
            return self.rescue.sortir_du_mur(steering)

        # Au depart on avance tout droit pour eviter de se cogner contre les adversaires
        if obs['distance_down_track'] <= 2:
            steering = 0.0
            acceleration = 1.0
             
        if self.lock_mode != None: # Si on est en train d'esquiver
            
            drift = False       # Pas de drift
            nitro = False       # Pas de nitro
            
        fire_items = False
        karts_pos = obs.get("karts_position",[])
        #attachment_id = obs.get("attachment",0)
        if len(karts_pos)>0:
            for ennemis in karts_pos:
                e_x = ennemis[0]
                e_z = ennemis[2]
                seuil = 1 + (e_z/15.0)      # item comme la balle de bowling pour lancer le mieux possible sur l'adversaire selon la distance qui nous le sépare
                if 2.0 < e_z < 15.0 and abs(e_x) < seuil:
                    #print(attachment_id)
                    fire_items = True
                    break
                elif -15.0 < e_z < -2.0:
                    #print(attachment_id)
                    fire_items = True
                    break

        
        action = {
            "acceleration": acceleration,
            "steer": steering,
            "brake": brake,
            "drift": False,
            "nitro": nitro,
            "rescue":False,
            "fire": fire_items,
        }
        return action
