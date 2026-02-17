class NitroDrift:
    
    def manage_nitro(self, steer, energy):
        nit = False
        if (energy > 0.5 and abs(steer) < 0.45):
            nit = True
        return nit


    def manage_drift(self, steer, distance):
        if abs(steer) > 0.65 and distance > 5.0:
            if steer > 0:
                steer = steer + 0.10
            else:
                steer = steer - 0.10
    
            if steer > 1.0:
                steer = 1.0
            if steer < -1.0:
                steer = -1.0
    
            return True, steer
    
        return False, steer
    
