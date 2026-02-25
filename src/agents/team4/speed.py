class SpeedController:
    
    """
    Module SpeedController : Gère la logique d'accélération
    """
    
    def manage_speed(self,speed,drift,conf,obs):
        """
        Gère l'accélération

        Args:
            speed(float) : Vitesse de l'agent.
            drift(bool) : Booléen disant si l'agent drift ou non.
            conf(float) : Valeur representant un seuil de vitesse.
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
            if a < 4.0 and speed > conf.vitesse_seuil:
                return 0.98, False
            return 1.0, False
        if a < 6.0 and speed > conf.vitesse_seuil:
            return 1.0, False
        
        if a > 10.0 and speed > conf.vitesse_seuil:
            return 0.05, True

        if (a > 5.0 and a < 8.0) and speed > (conf.vitesse_seuil - 2):
            return 0.55, False

        if (a > 8.0 and a < 10.0) and speed > (conf.vitesse_seuil - 1):
            return 0.3, True

        return 1.0, False
