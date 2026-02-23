class SpeedController:
    
    """
    Module SpeedController : Gère la logique d'accélération
    """
    
    def manage_speed(self, steer, speed, drift, conf):
        """
        Gère l'accélération

        Args:
            steer(float) : Angle de braquage des roues.
            speed(float) : Vitesse de l'agent.
            drift(bool) : Booléen disant si l'agent drift ou non.
        
        Returns:
            bool : Variable permettant d'activer ou non le brake.
            float : Valeur représentant l'accélération.
        """
        
        
        a = abs(steer)

        if drift:
            if a > 0.95 and speed > conf.vitesse_seuil:
                return 0.98, False
            return 1.0, False

        if a > 0.95 and speed > conf.vitesse_seuil:
            return 0.22, True

        if a > 0.90 and speed > (conf.vitesse_seuil - 2):
            return 0.85, False

        if a > 0.75 and speed > (conf.vitesse_seuil - 1):
            return 0.95, False

        return 1.0, False