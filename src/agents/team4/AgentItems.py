from .steering import Steering
from omegaconf import DictConfig

class AgentItems:
    
    """Module Agent Expert Item : Gère la logique d'utilisation des différents items"""
    
    def __init__(self,config : DictConfig ,config_pilote : DictConfig) -> None:
        
        """Initialise les variables d'instances de l'agent expert"""
        
        self.steerer = Steering(config_pilote)
        """@private"""
        self.c = config
        """@private"""
    
    def reset(self):

        """Réinitialise les variables d'instances de l'agent expert"""
        
        self.steerer.reset()
    
    def use_items(self, obs : dict, steer : float) -> tuple[bool,float]:
        
        """
        
        Gère la logique d'utilisation d'items

        Args:
                
            obs(dict) : Les données de télémétrie fournies par le simulateur.
            steer(float) : Angle de braquage actuel des roues.

        Returns:
            
            bool : Autorise l'utilisation d'items.
            float : Angle de braquage des roues modifié.
        
        """
        
        item = int(obs.get("powerup_type", 0))

        # Bubblegum Cake Switch
        if item in (1, 2, 6):
            return True, steer

        # Zipper
        if item == 4:
            if (abs(steer) < self.c.steer_allow_zipper):
                return True, steer

        # Swatter
        if item == 7:
            for kart in obs.get("karts_position", []):
                x, z = float(kart[0]), float(kart[2])
                if -self.c.radar_xswatter <= x <= self.c.radar_xswatter and self.c.radar_zmin_swatter <= z <= self.c.radar_zmax_swatter:
                    return True, steer

        # Bowling Ball, Plunger, RubberBall, Parachute, Anvil
        if item in (3, 5, 8, 9, 10):
            for kart in obs.get("karts_position", []):
                x, z = float(kart[0]), float(kart[2])
                if -self.c.radar_xball <= x <= self.c.radar_xball and self.c.radar_zmin_ball <= z <= self.c.radar_zmax_ball:
                    target = self.steerer.manage_pure_pursuit(x, z, self.c.gain_steer)
                    new_steer = float(self.c.rate_steer * steer + self.c.rate_target * target)
                    return True, new_steer

        # Nothing
        return False, steer
