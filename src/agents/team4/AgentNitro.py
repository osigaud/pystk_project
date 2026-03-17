from omegaconf import DictConfig

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
    
    def manage_nitro(self,obs : dict,steer : float,energy : float) -> bool:

        """
        Gère l'activation du nitro

        Args:
            
            obs(dict) : Les données fournies par le simulateur.
            steer(float) : Angle de braquage des roues.
            energy(float) : Mesure donnant le taux restant de nitro.
        
        Returns:
            
            bool : Variable permettant d'affirmer ou non l'utilisation du nitro.
        """
        
        points = obs['paths_start'] # Récupération des points 
        
        target_now = points[2][0] # Récuperation du decalage lateral du point d'indice 2
        target_soon = points[3][0] # Récuperation du decalage lateral du point d'indice 3
        target_late = points[4][0] # Récuperation du decalage lateral du point d'indice 4
        
        
        nit = False
        # On active le nitro si on s'est assure qu'aucun virage serre n'arrive
        if (energy > self.c.seuil_energy and abs(steer) < self.c.seuil_steer and abs(target_now)<= self.c.seuil_target_now and abs(target_soon) <= self.c.seuil_target_soon and target_late <= self.c.seuil_target_late):
            nit = True
        return nit


    
