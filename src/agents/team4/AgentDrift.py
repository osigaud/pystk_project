import numpy as np

class AgentDrift:    
    
    """Module Agent Expert Drift : Gère la logique d'activation du drift'"""
    
    def __init__(self):
        
        """Initialise les variables d'instances de l'agent expert"""
        
        self.timer = 0
        """@private"""
        self.cooldown = 0
        """@private"""

    def reset(self):
        
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

        x0 = points[0][0]
        x1 = points[1][0]
        x2 = points[2][0]
        x3 = points[3][0]
        x4 = points[4][0]

        speed = np.linalg.norm(vel)

        # Virage confirmé si les X progressent de façon monotone et dépassent un seuil minimal
        is_curve_right = x1 > x0 and x2 > x1 and x3 > x2 and x4 >x3 and x2 > 3.0
        is_curve_left  = x1 < x0 and x2 < x1 and x3 < x2 and x4 < x3 and x2 < -3.0

        if (is_curve_right or is_curve_left) and speed >= 12 and abs(steer) >= 0.5:
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

        trigger = self.must_drift(obs, steer, vel)
        
        if trigger and self.timer <= 0 and self.cooldown <= 0:
            self.timer = 15

        if self.timer > 0:
            adjusted_steer = steer * 0.6
            self.timer -= 1
            if self.timer == 0:
                self.cooldown = 15 
            return True, adjusted_steer
        
        if self.cooldown > 0:
            self.cooldown -= 1
            
        return False, steer