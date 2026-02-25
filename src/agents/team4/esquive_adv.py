class EsquiveAdv:

    """
    Module EsquiveAdv : Gère la logique de détection d'adversaires
    """
    
    def esquive_adv(self,obs):
        """
        Détecte Les Adversaires 

        Args:
            obs(dict) : Les données fournies par le simulateur.
        
        Returns:
            bool : Variable permettant d'affirmer la présence d'un adversaire.
            float : Position latéral de l'adversaire.
            float : Profondeur de l'adversaire.
        """


        kart_pos = obs.get('karts_position', []) 
        if len(kart_pos) == 0:
            return False, 0.0, 0.0

        adv=kart_pos[0]
        devant=False
        if -0.8 <= adv[0] <=0.8 and  0.1<= adv[2]<=1.3:
            devant=True

        return devant,adv[0],adv[2]
    
