from .steering import Steering
from omegaconf import DictConfig

class AgentEsquiveAdv:

    """
    Module Agent Expert Esquive Adversaire : Gère la logique de détection d'adversaires et de dépassement
    """
    
    def __init__(self,config : DictConfig ,config_pilote : DictConfig) -> None:
        
        """Initialise les variables d'instances de l'agent expert"""
        
        self.c = config
        """@private"""
        self.pilotage = Steering(config_pilote)
        """@private"""
    
    def reset(self) -> None:

        """Réinitialise les variables d'instances de l'agent expert"""
        self.pilotage.reset()
        
    def esquive_adv(self,obs : dict) -> tuple[bool,float,float]:
        """
        Détecte Les Adversaires.

        Args:
            
            obs(dict) : Les données de télémétrie fournies par le simulateur.
        
        Returns:
            
            bool : Variable permettant d'affirmer la présence d'un adversaire.
            float : Position latéral de l'adversaire.
            float : Profondeur de l'adversaire.
        """


        kart_pos = obs.get('karts_position', []) 
        if len(kart_pos) == 0:
            return False, 0.0, 0.0

        adv=kart_pos[0]
        devant=False
        if -self.c.radar_x <= adv[0] <=self.c.radar_x and  self.c.radar_zmin<= adv[2]<=self.c.radar_zmax:
            devant=True

        return devant,adv[0],adv[2]
    

    def choose_action(self,obs : dict,gx : float,gz : float,acceleration : float) -> tuple[bool,dict]:

        """
        
        Gère la logique de réaction à la détection d'un adversaire

        Args:
                
            obs(dict) : Les données de télémétrie fournies par le simulateur.
            gx(float) : Décalage latéral actuel de la cible.
            gz(float) : Profondeur actuel de la cible.
            acceleration(float) : Accéleration de l'agent.

        Returns:
            
            bool : Permet de confirmer la présence d'un adversaire et la nécessité de le dépasser.
            dict : Le dictionnaire d'actions à réaliser pour esquiver un adversaire.
        
        """
        
        danger_adv, a_x,a_z = self.esquive_adv(obs)
            
        if danger_adv:
            if a_x >= 0:
                gx -= self.c.decalage_lateral # On se décale à gauche 
            else:
                gx += self.c.decalage_lateral # On se décale à droite
            
            gain_volant = self.c.default_gain
            steering = self.pilotage.manage_pure_pursuit(gx,gz,gain_volant)
            action = {
            "acceleration": acceleration,
            "steer": steering,
            "brake": False,
            "drift": False,
            "nitro": False,
            "rescue":False,
            "fire": False,
            }
            return True, action
        
        return False, {}