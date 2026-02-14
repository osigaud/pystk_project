class Drift:    
    
    def manage_drift(self, steer, distance):
        if abs(steer) > 0.80 and distance > 5.0:
            if steer > 0:
                steer = steer + 0.12
            else:
                steer = steer - 0.12
    
            if steer > 1.0:
                steer = 1.0
            if steer < -1.0:
                steer = -1.0
    
            return True, steer
    
        return False, steer
    