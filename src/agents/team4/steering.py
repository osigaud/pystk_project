import math
import numpy as np

class Steering:
    def manage_pure_pursuit(self,obs):
        
        points = obs.get("paths_start",[])
        if len(points) > 2: 
            target = points[2]
            gx = target[0]
            gz = target[2]
            l2 = gx**2 + gz**2
            
            if l2 < 0.01 : return 0.0
            
            L = 2.5 # On simule un empattement

            steer = math.atan2(2 * L * gx,l2)

            return np.clip(steer*4.5,-1,1)
        else:
            return 0.0

        





