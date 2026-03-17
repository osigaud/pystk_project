from omegaconf import DictConfig

class SpeedController:
    
    """
    Module SpeedController : Gère la logique d'accélération
    """

    def __init__(self,config : DictConfig) -> None:
        """Initialise les variables d'instances de l'agent."""
        
        self.c = config
        """@private"""
    
    def reset(self) -> None:
        """Réinitialise les variables d'instances de l'agent expert"""
        pass
    
    def manage_speed(self,speed:float,drift:bool,obs:dict) -> tuple[float,bool]:
        """
        Gère l'accélération.

        Args:
            
            speed(float) : Vitesse de l'agent.
            drift(bool) : Booléen disant si l'agent drift ou non.
            obs(dict) : Les données fournies par le simulateur.
        
        Returns:
            
            float: Valeur représentant l'accélération.
            bool: Variable permettant d'activer ou non le brake.

        """
        points = obs.get("paths_start",[]) # On récupère la liste des points
        dx = points[3][0] #on prend le decalage latéral x du troisieme point devant l'agent
        
        a = abs(dx)
        #print("décal x = ",a)
        
        if drift:
            return self.c.acceleration_drift, False
        
        if a < self.c.seuil_decalage_low and speed > self.c.vitesse_seuil:
            return self.c.acceleration_max, False
        
        if a > self.c.seuil_decalage_max and speed > self.c.vitesse_seuil:
            return self.c.acceleration_czero, True

        if (a > self.c.seuil_decalage_min and a < self.c.seuil_decalage_mid) and speed > (self.c.vitesse_seuil - 2):
            return self.c.acceleration_mid, False

        if (a > self.c.seuil_decalage_mid and a < self.c.seuil_decalage_max) and speed > (self.c.vitesse_seuil - 1):
            return self.c.acceleration_low, True

        return self.c.acceleration_max, False
