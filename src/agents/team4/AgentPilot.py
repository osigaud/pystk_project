from .steering import Steering
from .speed import SpeedController
from .AgentItems import AgentItems
from .AgentNitro import AgentNitro
from omegaconf import DictConfig

class AgentPilot:

    """
    Module Agent Expert Pilote : Gère la logique de pilotage de base en utilisant les différents modules (nitro, items etc.)
    """
    
    def __init__(self, config : DictConfig, config_steering : DictConfig, config_speed : DictConfig, config_items : DictConfig, config_nitro : DictConfig, path_lookahead : int) -> None:
        
        """Initialise les variables d'instances de l'agent expert"""
        
        self.c = config
        """@private"""
        self.steering = Steering(config_steering)
        """@private"""
        self.speedcontroller = SpeedController(config_speed)
        """@private"""
        self.expert_items = AgentItems(config_items,config_steering)
        """@private"""
        self.path_lookahead = path_lookahead
        """@private"""
        self.expert_nitro = AgentNitro(config_nitro)
        """@private"""

    def reset(self) -> None:
        
        """Réinitialise les variables d'instances de l'agent expert"""
        
        self.steering.reset()
        self.speedcontroller.reset()
        self.expert_items.reset()
        self.expert_nitro.reset()

    
    def get_steering(self,obs : dict) -> float:
        
        """
        
        Renvoie le steering calculé avec le pure pursuit

        Args:
                
            obs(dict) : Les données de télémétrie fournies par le simulateur.
            
        Returns:
            
            float : Angle de braquage des roues.
        
        """
        
        points = obs.get("paths_start",[]) # Récupération des points
        target = points[self.path_lookahead] # On récupère le x-ème point de la liste defini par la variable de classe
        gx = target[0] # On récupère x, le décalage latéral
        gz = target[2] # On récupère z, la profondeur
        gain_volant = self.c.default_gain
        steering = self.steering.manage_pure_pursuit(gx,gz,gain_volant) # Calcul du steering

        return steering

    def choose_action(self,obs : dict) -> dict:

        """
        
        Gère la logique de pilotage

        Args:
                
            obs(dict) : Les données de télémétrie fournies par le simulateur.
            
        Returns:
            
            dict : Le dictionnaire d'actions à réaliser pour piloter.
        
        """
        
        points = obs.get("paths_start",[]) # On récupère la liste des points

        # Si on est en début de course, on avance tout droit en accélérant à fond.
        if obs['distance_down_track'] <= self.c.seuil_distance:
            action = {
            "acceleration": 1.0,
            "steer": 0.0,
            "brake": False,
            "drift": False,
            "nitro": False,
            "rescue":False,
            "fire": False,
            }
            return action
        
        # Si la longueur de la liste est inferieur à 2, on accèlère à fond (ligne d'arrivée proche)
        if len(points) <= self.c.seuil_lenpoints: 
            action = {
                "acceleration": 1.0,
                "steer": 0.0,
                "brake": False,
                "drift": False,
                "nitro": True,
                "rescue":False,
                "fire": False,
            }
            return action
        

        steering = self.get_steering(obs) # Récupération du steering
        acceleration, brake = self.speedcontroller.manage_speed(obs) # Appel à la fonction gerer_vitesse
        nitro = self.expert_nitro.manage_nitro(obs,steering) # Appel à la fonction manage_nitro

        # Mécanisme anti-vibration
        epsilon = self.c.epsilon
        road_straight = abs(points[2][0]) < self.c.seuil_road_straight
        if road_straight and abs(steering) <= epsilon:
            steering = 0.0

        # Appel de la fonction item
        fire, steering = self.expert_items.use_items(obs, steering)
        
        action = {
            "acceleration": acceleration,
            "steer": steering,
            "brake": brake,
            "drift": False,
            "nitro": nitro,
            "rescue":False,
            "fire": fire,
        }
        return action