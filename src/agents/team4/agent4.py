from agents.kart_agent import KartAgent
from .AgentRescue import AgentRescue
from .AgentBanana import AgentBanana
from .AgentEsquiveAdv import AgentEsquiveAdv
from .AgentPilot import AgentPilot
from omegaconf import OmegaConf
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent # On obtient le chemin absolu vers notre fichier agent4
CONFIG_PATH = BASE_DIR / "configuration.yaml" # On dit que notre fichier de config se trouve aussi ici

# kart_skin = ['adiumy', 'sara_the_racer', 'amanda', 'tux', 'beastie', 'emule', 'gavroche', 'gnu', 'hexley', 'kiki', 'konqi', 'nolok', 'pidgin', 'puffy', 'sara_the_wizard', 'suzanne', 'wilber', 'xue']

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
        self.expert_rescue = AgentRescue(self.conf.rescue)
        """@private"""
        self.expert_esquive_adv = AgentEsquiveAdv(self.conf.opponent, self.conf.steering, self.conf.speed,self.path_lookahead)
        """@private"""
        self.expert_banana_dodge = AgentBanana(self.conf.banana, self.conf.steering, self.conf.speed,self.path_lookahead)
        """@private"""
        self.expert_pilot = AgentPilot(self.conf.pilot,self.conf.steering,self.conf.speed,self.conf.powerup_type,self.conf.nitro,self.path_lookahead)
        """@private"""
        self.skin = 'tux'
        """@private"""        
        
    def reset(self) -> None:
        """Réinitialise les variables d'instances de l'agent en début de course."""
        self.obs, _ = self.env.reset()
        self.isEnd = False
        self.expert_rescue.reset()
        self.expert_banana_dodge.reset()
        self.expert_esquive_adv.reset()
        self.expert_pilot.reset()
        
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
        
        points = obs.get("paths_start",[])

        if len(points) <= self.conf.pilot.seuil_lenpoints:
            return self.expert_pilot.choose_action(obs)
        
        steering = self.expert_pilot.get_steering(obs)
        
        # Appel en priorité de la fonction rescue
        is_stuck, action_stuck = self.expert_rescue.choose_action(obs,steering)
        if is_stuck and obs['distance_down_track'] >= self.c.seuil_distance_stuck:
            self.expert_banana_dodge.reset()
            self.expert_esquive_adv.reset()
            return action_stuck
        
        # Appel de la fonction esquive banane
        danger_banane, action_banane = self.expert_banana_dodge.choose_action(obs)
        if danger_banane:
            self.expert_esquive_adv.reset()
            return action_banane
        
        # Appel de la fonction esquive adversaire
        danger_adv, action_adv = self.expert_esquive_adv.choose_action(obs)
        if danger_adv:
            return action_adv
        
        return self.expert_pilot.choose_action(obs)