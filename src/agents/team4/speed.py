from omegaconf import DictConfig
import numpy as np
from utils.track_utils import compute_curvature

class SpeedController:
    
    """
    Module SpeedController : Gère la logique d'accélération
    """

    def __init__(self,config : DictConfig) -> None:
        """Initialise les variables d'instances de l'agent."""
        
        self.c = config
        """@private"""
        self.g = self.c.speed_gain
        """@private"""
        self.amax = self.c.acceleration_max
        """@private"""
        self.azero = self.c.acceleration_czero
        """@private"""
        self.alow = self.c.acceleration_low 
        """@private"""
        self.amid = self.c.acceleration_mid 
        """@private"""
        self.smax = self.c.seuil_decalage_max
        """@private"""
        self.smid = self.c.seuil_decalage_mid
        """"@private"""
        self.slow = self.c.seuil_decalage_low
        """@private"""
        self.smin = self.c.seuil_decalage_min
        """@private"""
    
    def reset(self) -> None:
        """Réinitialise les variables d'instances de l'agent expert"""
        pass
    
    def manage_speed(self,obs:dict) -> tuple[float,bool]:
        """
        Gère l'accélération.

        Args:
            
            obs(dict) : Les données fournies par le simulateur.
        
        Returns:
            
            float: Valeur représentant l'accélération.
            bool: Variable permettant d'activer ou non le brake.

        """
        points = obs.get("paths_start",[]) # On récupère la liste des points
        dx = points[3][0] #on prend le decalage latéral x du troisieme point devant l'agent

        a = abs(dx)
        #print("décal x = ",a)

        if a < 4.0:
            return 0.98, False
        return self.amax, False
        if a < self.slow :
            return self.amax, False

        if a > self.smax:
            return self.azero, True

        if (a > self.smin and a < self.smid):
            return self.amid, False

        if (a > self.smid and a < self.smax):
            return self.alow, True

        return self.amax, False
