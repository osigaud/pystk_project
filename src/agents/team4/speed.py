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

        k = abs(compute_curvature(points[1:5][:3]))

        v_test = np.clip(self.amax/np.sqrt(1+k),0, self.amax)

        return np.clip(v_test*self.g,0,self.amax), False #on ajoute un gain 
        
