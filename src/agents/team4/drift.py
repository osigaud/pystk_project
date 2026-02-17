class Drift:    
    
    def manage_drift(self, steer, distance):
        if abs(steer) > 0.65 and distance > 5.0:
            
    
            if steer > 1.0:
                steer = 1.0
            if steer < -1.0:
                steer = -1.0
    
            return True, steer
    
        return False, steer
    