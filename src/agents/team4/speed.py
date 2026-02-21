class SpeedController:
    
    """
    Module SpeedController : Gère la logique d'accélération
    """
    
    def manage_speed(self, steer, speed, drift):
        """
        Gère l'accélération

        Args:
            steer(float)
            speed(float)
            drift(bool)
        
        Returns:
            bool : Variable permettant d'activer ou non le brake
            float : Valeur représentant l'accélération
        """
        
        
        a = abs(steer)

        if drift:
            if a > 0.95 and speed > 20.0:
                return 0.98, False
            return 1.0, False

        if a > 0.95 and speed > 20.0:
            return 0.22, True

        if a > 0.90 and speed > 18.0:
            return 0.85, False

        if a > 0.75 and speed > 19.0:
            return 0.95, False

        return 1.0, False