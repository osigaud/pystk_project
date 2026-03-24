from utils.track_utils import compute_curvature, compute_slope
from agents.kart_agent import KartAgent
from .steering import Steering
from .AgentRescue import AgentRescue
from .speed import SpeedController
from .AgentNitro import AgentNitro
from .AgentBanana import AgentBanana
from .AgentEsquiveAdv import AgentEsquiveAdv
from .AgentDrift import AgentDrift
from .AgentItems import AgentItems
from .AgentEdge import AgentEdge
from omegaconf import OmegaConf
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent # On obtient le chemin absolu vers notre fichier agent4
CONFIG_PATH = BASE_DIR / "configuration.yaml" # On dit que notre fichier de config se trouve aussi ici

__all__ = ["Agent4"]

class Agent4(KartAgent):
    """
    Module Agent4 : Agent coordinateur faisant appel aux différents agents experts pour gérer la logique générale de pilotage
    """

    def __init__(self, env, path_lookahead=2):
        """Initialise les variables d'instances de l'agent."""
        
        super().__init__(env)

        self.conf = OmegaConf.load(str(CONFIG_PATH)) # On charge le fichier de config
        """@private"""
        self.c = self.conf.main_agent
        """@private"""
        self.path_lookahead = self.c.path_lookahead
        """@private"""
        self.obs = None
        """@private"""
        self.isEnd = False
        """@private"""
        self.name = "The Winners"
        """@private"""
        self.steering = Steering(self.conf.steering)
        """@private"""
        self.expert_rescue = AgentRescue(self.conf.rescue)
        """@private"""
        self.speedcontroller=SpeedController(self.conf.speed)
        """@private"""
        self.expert_nitro = AgentNitro(self.conf.nitro)
        """@private"""
        self.expert_esquive_adv = AgentEsquiveAdv(self.conf.opponent, self.conf.steering)
        """@private"""
        self.expert_banana_dodge = AgentBanana(self.conf.banana, self.conf.steering)
        """@private"""
        self.expert_drift = AgentDrift(self.conf.drift)
        """@private"""
        self.expert_items = AgentItems(self.conf.powerup_type, self.conf.steering)
        """@private"""
        self.expert_edge = AgentEdge(self.conf.edge,self.conf.steering)
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
        self.expert_items.reset()
        self.expert_edge.reset()
        
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
        #points_end = obs.get("paths_end",[])
        
        if len(points) <= self.c.seuil_lenpoints: # Si la longueur de la liste est inferieur à 2, on accèlère à fond (ligne d'arrivée proche)
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
        gain_volant = self.c.default_gain  #Gain par défaut
        steering = self.steering.manage_pure_pursuit(gx,gz,gain_volant)
        #drift, modified_steer = self.expert_drift.choose_action(obs,steering,vel)
        acceleration, brake = self.speedcontroller.manage_speed(obs) # Appel à la fonction gerer_vitesse
        nitro = self.expert_nitro.manage_nitro(obs,steering,energy) # Appel à la fonction manage_nitro
        
        # Au depart on avance tout droit pour eviter de se cogner contre les adversaires
        if obs['distance_down_track'] <= self.c.seuil_distance:
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
        if is_stuck and obs['distance_down_track'] >= self.c.seuil_distance_stuck:
            return action_stuck
        
        # Appel de la fonction edge
        edge, action_edge = self.expert_edge.choose_action(obs, gx, gz)
        if edge:
            self.expert_esquive_adv.reset()
            self.expert_banana_dodge.reset()
            print("Danger Limite Piste")
            return action_edge
        
        # Appel de la fonction esquive banane
        danger_banane, action_banane = self.expert_banana_dodge.choose_action(obs,gx,gz,acceleration)
        if danger_banane:
            self.expert_esquive_adv.reset()
            return action_banane
        
        # Appel de la fonction esquive adversaire
        danger_adv, action_adv = self.expert_esquive_adv.choose_action(obs,gx,gz,acceleration)
        if danger_adv:
            return action_adv
        
        # Mécanisme Anti Vibration
        epsilon = self.c.epsilon
        road_straight = abs(points[2][0]) < self.c.seuil_road_straight
        if road_straight and abs(steering) <= epsilon:
            steering = 0.0

        fire, steering = self.expert_items.use_items(obs, steering)
        action = {
            "acceleration": acceleration,
            "steer": steering,
            "brake": brake,
            "drift": drift,
            "nitro": nitro,
            "rescue":False,
            "fire": fire,
        }
        return action