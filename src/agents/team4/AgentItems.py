from .steering import Steering
from omegaconf import DictConfig
from .ItemType import ItemType

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
        
        item_type = ItemType(obs.get("powerup_type", 0))
        item_count = obs.get("powerup_count", 0)
    
        #1 bubblegum
        #2 cake
        #3 bowling ball
        #4 zipper (boost speed)
        #5 plunger
        #6 switch bonus <-> banana
        #7 swapper
        if item_count < 1 :
            return False, steer #cas où nous n'avons pas d'item
        
        karts = obs.get("karts_position", [])

        # Bubblegum Cake Switch
        if item_type in (ItemType.BUBBLEGUM, ItemType.CAKE, ItemType.SWITCH):
            #return False, steer
            return True, steer
    
        # Zipper
        if item_type == ItemType.ZIPPER:
            if (abs(steer) < self.c.steer_allow_zipper):
                #return False, steer
                return True, steer
    
        # Swatter
        if item_type == ItemType.SWATTER:
            for kart in karts:
                x, z = float(kart[0]), float(kart[2])
                if -self.c.radar_xswatter <= x <= self.c.radar_xswatter and self.c.radar_zmin_swatter <= z <= self.c.radar_zmax_swatter:
                    #return False, steer
                    return True, steer
                return False, steer
    
        # Bowling Ball, Plunger, RubberBall
        if item_type in (ItemType.BOWLING, ItemType.PLUNGER, ItemType.RUBBERBALL):
            for kart in karts:
                x, z = float(kart[0]), float(kart[2])
                if -self.c.radar_xball <= x <= self.c.radar_xball and self.c.radar_zmin_ball <= z <= self.c.radar_zmax_ball:
                    target = self.steerer.manage_pure_pursuit(x, z, self.c.gain_steer)
                    new_steer = float(self.c.rate_steer * steer + self.c.rate_target * target)
                    #return False, steer
                    return True, new_steer
            return False, steer
        return False, steer
            
