class SpeedController:
    def vitesse(self, steering_angle):
        if abs(steering_angle) > 0.5:
            return 0.3
        else:
            return 1.0