import numpy as np
from omegaconf import DictConfig

class AgentDrift:    
    
    """Module Agent Expert Drift : Gère la logique d'activation du drift"""
    
    def __init__(self,config : DictConfig) -> None:
        
        """Initialise les variables d'instances de l'agent expert"""
        
        self.timer = 0
        """@private"""
        self.cooldown = 0
        """@private"""
        self.c = config
        """@private"""

    def reset(self) -> None:
        
        """Réinitialise les variables d'instances de l'agent expert"""
        
        self.timer = 0
        self.cooldown = 0
    
    def must_drift(self,obs : dict,steer : float,vel : list) -> bool:

        """
        Renvoie l'autorisation de déclencher un drift.

        Args:
            
            obs(dict) : Les données de télémétrie fournies par le simulateur.
            steer(float) : Angle de braquage actuel des roues.
            vel(list) : Vecteurs 3D représentant la velocité de l'agent.
        
        Returns:
            
            bool : Variable permettant d'affirmer l'utilisation du drift.
        
        """
        
        points = obs.get("paths_start", [])
        if len(points) < 4:
            return False

        # On récupère le décalage latéral des 5 premiers points
        x0 = points[0][0]
        x1 = points[1][0]
        x2 = points[2][0]
        x3 = points[3][0]
        x4 = points[4][0]

        # Calcul de la norme du vecteur vitesse
        speed = np.linalg.norm(vel)

        # Virage confirmé si les X progressent de façon monotone et dépassent un seuil minimal
        is_curve_right = x1 > x0 and x2 > x1 and x3 > x2 and x4 >x3 and x2 > self.c.x_seuil
        is_curve_left  = x1 < x0 and x2 < x1 and x3 < x2 and x4 < x3 and x2 < -self.c.x_seuil

        # Si un virage est detecté, que la vitesse est assez grande et qu'on depasse un angle de braquage, on peut drift
        if (is_curve_right or is_curve_left) and speed >= self.c.speed_seuil and abs(steer) >= self.c.steer_seuil:
            return True

        return False

    def choose_action(self, obs : dict, steer : float, vel : list) -> tuple[bool,float]:

        """
        Gère la logique d'activation du drift

        Args:
            
            obs(dict) : Les données de télémétrie fournies par le simulateur.
            steer(float) : Angle de braquage actuel des roues.
            vel(list) : Vecteurs 3D représentant la velocité de l'agent.
        
        Returns:
            
            bool : Variable permettant d'affirmer l'utilisation du drift.
            float : Angle de braquage des roues modifié.
        
        """

        #Appel de la fonction qui affirme si le drift est possible
        trigger = self.must_drift(obs, steer, vel)
        
        if trigger and self.timer <= 0 and self.cooldown <= 0:
            self.timer = self.c.timer_start

        # Système de compteur qui permet de maintenir le drift sur x frames
        if self.timer > 0:
            adjusted_steer = steer * self.c.coefficient_steer
            self.timer -= 1
            if self.timer == 0:
                self.cooldown = self.c.cooldown_start 
            return True, adjusted_steer
        
        # Système de cooldown pour eviter d'enchainer les drifts
        if self.cooldown > 0:
            self.cooldown -= 1
            
        return False, steer