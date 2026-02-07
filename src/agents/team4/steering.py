import math
import numpy as np

class Steering:
    def manage_pure_pursuit(self,obs):
        
        points = obs.get("paths_start",(0,0,0))
        if(len(points)>2): 
            target = points[2]
            gx = target[0]
            gz = target[2]
            l2 = gx**2 + gz**2
            rayon = l2/(2*gx)

            L = 2.5 # On simule un empattement

            steer = math.atan2(L,rayon)

            return np.clip(steer*4.5,-1,1)
        else:
            return 0.0

        





