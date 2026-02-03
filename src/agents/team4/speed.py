class SpeedController:
    def vitesse(self, steering_angle):
        if abs(steering_angle) > 0.5:
            return 0.3
        else:
            return 1.0
    
    def vitesse2(self, steering):
        accel = 1.0 - (abs(steering) * 0.8)
    
    # Sécurité : on ne descend jamais sous 0.1 pour ne pas s'arrêter
        return max(0.1, accel)