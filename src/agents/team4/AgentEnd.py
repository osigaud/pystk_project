from omegaconf import DictConfig

class AgentEnd:    
    """
    Module Agent Expert End : Gère la logique de fin de course
    """
    def __init__(self,config : DictConfig) -> None:
        
        """Initialise les variables d'instances de l'agent expert"""
        
        self.c = config
    
    def reset(self) -> None:
        """Réinitialise les variables d'instances de l'agent expert"""
        pass

    def choose_action(self, obs : dict) -> tuple[bool,dict]:
        
        """
        Gère la fin de course

        Args:
            
            obs(dict) : Les données fournies par le simulateur.
        
        Returns:
            
            bool : Permet de confirmer la détection de fin de course.
            dict : Dictionnaire d'actions à effectué pour la fin de course.
        """
        
        points = obs.get("paths_start",[]) 
        
        if len(points) <= self.c.seuil_lenpoints: # Si la longueur de la liste est inferieur à 2, on accèlère à fond (ligne d'arrivée proche)
            action = {
                "acceleration": 1.0,
                "steer": 0.0,
                "brake": False,
                "drift": False,
                "nitro": True,
                "rescue":False,
                "fire": False,
            }
            return True, action
        return False, {}