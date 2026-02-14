class Nitro:
    
    def manage_nitro(self, steer, energy,obs):
        points = obs['paths_start']
        

        target_now = points[2][0]
        target_soon = points[3][0]
        target_late = points[4][0]
        
        
        nit = False
        if (energy > 0.5 and abs(steer) < 0.45 and abs(target_now)<=5 and abs(target_soon) <= 5 and target_late <= 7):
            nit = True
        return nit


    
