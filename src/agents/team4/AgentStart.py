from omegaconf import DictConfig

class AgentStart:    
    """
    Module Agent Expert Start : Gère la logique de début de course
    """
    def __init__(self,config : DictConfig) -> None:
        
        """Initialise les variables d'instances de l'agent expert"""
        
        self.c = config
    
    def reset(self) -> None:
        """Réinitialise les variables d'instances de l'agent expert"""
        pass

    def choose_action(self, obs : dict) -> tuple[bool,dict]:
        
        """
        Gère le début de course

        Args:
            
            obs(dict) : Les données fournies par le simulateur.
        
        Returns:
            
            bool : Permet de confirmer la détection de début de course.
            dict : Dictionnaire d'actions à effectué pour le début de course.
        """
        
        # Au depart on avance tout droit pour eviter de se cogner contre les adversaires
        if obs['distance_down_track'] <= self.c.seuil_distance:
            steering = 0.0
            acceleration = 1.0
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