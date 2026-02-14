class Nitro:
    
    def manage_nitro(self, steer, energy):
        nit = False
        if (energy > 0.5 and abs(steer) < 0.45):
            nit = True
        return nit


    
