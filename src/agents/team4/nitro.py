class Nitro:

    """
    Module Nitro : Gère la logique d'activation du nitro
    """
    
    def manage_nitro(self,steer,energy,obs):

        """
        Gère l'activation du nitro

        Args:
            obs(dict)
            steer(float)
            energy(float)
        
        Returns:
            bool : Variable permettant d'affirmer ou non l'utilisation du nitro
        """
        
        points = obs['paths_start'] # Récupération des points 
        
        target_now = points[2][0] # Récuperation du decalage lateral du point d'indice 2
        target_soon = points[3][0] # Récuperation du decalage lateral du point d'indice 3
        target_late = points[4][0] # Récuperation du decalage lateral du point d'indice 4
        
        
        nit = False
        # On active le nitro si on s'est assure qu'aucun virage serre n'arrive
        if (energy > 0.5 and abs(steer) < 0.45 and abs(target_now)<=5 and abs(target_soon) <= 5 and target_late <= 7):
            nit = True
        return nit


    
