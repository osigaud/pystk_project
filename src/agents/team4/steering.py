import math
import numpy as np

class Steering:
    def manage_pure_pursuit(self,obs):
        points = obs.get("paths_start",(0,0,0))
        target = points[2]




