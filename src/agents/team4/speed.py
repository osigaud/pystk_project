class SpeedController:
    
    def manage_speed(self, steer, distance):
        if distance < 5.0:
            return 1.0, False
        a = abs(steer)
        if a > 0.85:
            return 0.35, True
        if a > 0.65:
            return 0.65, False
        if a > 0.45:
            return 0.85, False
        return 1.0, False