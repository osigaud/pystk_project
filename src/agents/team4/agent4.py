from utils.track_utils import compute_curvature, compute_slope
from agents.kart_agent import KartAgent
from .steering import Steering
from .AgentRescue import AgentRescue
from .speed import SpeedController
from .AgentNitro import AgentNitro
from .AgentBanana import AgentBanana
from .AgentEsquiveAdv import AgentEsquiveAdv
from .AgentDrift import AgentDrift
from omegaconf import OmegaConf
from pathlib import Path
from .useItems import useItems

BASE_DIR = Path(__file__).resolve().parent # On obtient le chemin absolu vers notre fichier agent4
CONFIG_PATH = BASE_DIR / "configuration.yaml" # On dit que notre fichier de config se trouve aussi ici

conf = OmegaConf.load(str(CONFIG_PATH)) # On charge le fichier de config

__all__ = ["Agent4"]

class Agent4(KartAgent):
    """
    Module Agent4 : Agent coordinateur faisant appel aux différents agents experts pour gérer la logique générale de pilotage
    """

    def __init__(self, env, path_lookahead=2):
        """Initialise les variables d'instances de l'agent."""
        
        super().__init__(env)
        self.path_lookahead = 2
        """@private"""
        self.obs = None
        """@private"""
        self.isEnd = False
        """@private"""
        self.name = "The Winners"
        """@private"""
        self.steering = Steering()
        """@private"""
        self.expert_rescue = AgentRescue()
        """@private"""
        self.speedcontroller=SpeedController()
        """@private"""
        self.expert_nitro = AgentNitro()
        """@private"""
        self.expert_esquive_adv = AgentEsquiveAdv()
        """@private"""
        self.expert_banana_dodge = AgentBanana()
        """@private"""
        self.expert_drift = AgentDrift()
        """@private"""
        self.use_items = useItems()
        """@private"""
        #print(OmegaConf.to_yaml(conf))
        
        
    def reset(self) -> None:
        """Réinitialise les variables d'instances de l'agent en début de course."""
        self.obs, _ = self.env.reset()
        self.isEnd = False
        self.expert_rescue.reset()
        self.expert_banana_dodge.reset()
        self.steering.reset()
        self.speedcontroller.reset()
        self.expert_nitro.reset()
        self.expert_esquive_adv.reset()
        self.expert_drift.reset()
        
    def endOfTrack(self) -> bool:
        """Indique si la course est fini."""
        return self.isEnd

    def choose_action(self,obs : dict) -> dict:
        """
        Renvoie les différentes actions à réaliser

        Args:
            
            obs(dict) : Les données de télémétrie fournies par le simulateur.

        Returns:
            
            dict : Le dictionnaire d'actions (accélération, direction, nitro, etc.).
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
        
        target = points[self.path_lookahead] # On récupère le x-ème point de la liste defini par la variable de classe
        gx = target[0] # On récupère x, le décalage latéral
        gz = target[2] # On récupère z, la profondeur

        distance = float(obs.get("distance_down_track", [0.0])[0])
        vel = obs.get("velocity", [0.0, 0.0, 0.0])
        speed = float(vel[2])
        energy = float(obs.get("energy", [0.0])[0])

        drift = False
        gain_volant = 7.0  #Gain par défaut
        steering = self.steering.manage_pure_pursuit(gx,gz,gain_volant)
        drift, modified_steer = self.expert_drift.choose_action(obs,steering,vel)
        acceleration, brake = self.speedcontroller.manage_speed(speed,drift,conf,obs) # Appel à la fonction gerer_vitesse
        nitro = self.expert_nitro.manage_nitro(obs,steering,energy) # Appel à la fonction manage_nitro
        
        # Au depart on avance tout droit pour eviter de se cogner contre les adversaires
        if obs['distance_down_track'] <= 2:
            steering = 0.0
            acceleration = 1.0
            action = {
            "acceleration": acceleration,
            "steer": steering,
            "brake": False,
            "drift": False,
            "nitro": False,
            "rescue":False,
            "fire": False,
            }
            return action

        # Appel en priorité de la fonction rescue
        is_stuck, action_stuck = self.expert_rescue.choose_action(steering,speed,distance)
        if is_stuck and obs['distance_down_track'] >= 3:
            return action_stuck
        
        # Appel de la fonction esquive banane
        danger_banane, action_banane = self.expert_banana_dodge.choose_action(obs,gx,gz,acceleration)
        if danger_banane:
            return action_banane
        
        # Appel de la fonction esquive adversaire
        danger_adv, action_adv = self.expert_esquive_adv.choose_action(obs,gx,gz,acceleration)
        if danger_adv:
            return action_adv
        
        # Mécanisme Anti Vibration
        epsilon = 0.05
        road_straight = abs(points[2][0]) < 0.8
        if road_straight and abs(steering) <= epsilon:
            steering = 0.0

        fire, steering = self.use_items.use_items(obs, steering)
        action = {
            "acceleration": acceleration,
            "steer": modified_steer,
            "brake": brake,
            "drift": False,
            "nitro": nitro,
            "rescue":False,
            "fire": fire,
        }
        return action
