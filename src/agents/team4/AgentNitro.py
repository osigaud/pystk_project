from omegaconf import DictConfig
from utils.track_utils import compute_curvature


class AgentNitro:

    """
    Module Agent Expert Nitro : Gère la logique d'activation du nitro
    """
    
    def __init__(self,config : DictConfig) -> None:
        """Initialise les variables d'instances de l'agent."""
        
        self.c = config
        """@private"""

    def reset(self) -> None:
        """Réinitialise les variables d'instances de l'agent expert"""
        pass
    
    def manage_nitro(self,obs : dict,steer : float) -> bool:

        """
        Gère l'activation du nitro

        Args:
            
            obs(dict) : Les données fournies par le simulateur.
            steer(float) : Angle de braquage des roues.
            
        Returns:
            
            bool : Variable permettant d'affirmer ou non l'utilisation du nitro.
        """
        
        energy = float(obs.get("energy", [0.0])[0])
        
        points = obs['paths_start'] # Récupération des points 

        courbe = compute_curvature(points[self.c.nb_min_points:self.c.nb_max_points]) # Calcul de la courbe
        nit = False
        # On active le nitro si on s'est assure qu'aucun virage serre n'arrive
        if (energy > self.c.seuil_energy and abs(steer) < self.c.seuil_steer and abs(courbe)<self.c.max_curvature_for_nitro):
            nit = True
        return nit


    
