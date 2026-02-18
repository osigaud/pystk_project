import math
import numpy as np

from utils.track_utils import compute_curvature, compute_slope

from omegaconf import OmegaConf

cfg = OmegaConf.load("../agents/team3/config.yml")


class Pilot():
    
    def choose_action(self, obs):

        velocity = obs["velocity"][2]
        idx = int((velocity/10)+1.0)
        target_ctr_x = (obs["paths_start"][idx][0] + obs["paths_end"][idx][0]) / 2.0
        target_ctr_z = (obs["paths_start"][idx][2] + obs["paths_end"][idx][2]) / 2.0
        offset_force = 0.0
        items_type = np.array(obs["items_type"])
        items_pos = np.array(obs["items_position"])
        closest_baditems_dist = 20.0
        closest_baditems_x = 0.0
        danger = False
        for i in range(len(items_type)):
            if items_type[i] in [1, 4]: 
                baditems_x = items_pos[i][0]
                baditems_z = items_pos[i][2]
                if 0 < baditems_z < closest_baditems_dist and abs(baditems_x) < 3.5:
                    closest_baditems_dist = baditems_z
                    closest_baditems_x = baditems_x
                    danger = True
        if danger:
            avoid_force = (20.0 - closest_baditems_dist) / 2.0
            if closest_baditems_x > 0:
                offset_force = -avoid_force 
            else:
                offset_force = avoid_force 
        target_ctr_x += offset_force
        err = math.atan2(target_ctr_x, target_ctr_z)
        p_k = 1.2
        d_k = 0.5
        drv = err - self.prev_err
        self.prev_err = err
        ctrl_pd = p_k * err + d_k * drv
        steer = ctrl_pd
        if steer > 1.0:
            steer = 1.0
        elif steer < -1.0:
            steer = -1.0
        acceleration = 1.0
        speed = math.sqrt(obs["velocity"][0]**2 + obs["velocity"][2]**2)
        brake = False
        nitro = False
        rescue = False
        if abs(steer) > 0.4 and speed > 22.0:
            acceleration = 0.5 
        if abs(err) > 1.0 and speed > 15.0:
            acceleration = 0.0
            brake = True
        if abs(steer) < 0.2 and speed > 10.0 and obs["energy"] >= 2.0:
            nitro = True

        #Blocage
        if (speed < 5.0):
            self.time_blocked += 1 
            if (self.time_blocked > 10):
                acceleration = 0.0
                brake = True
                steer = -steer
            elif self.time_blocked >= 20: 
                rescue = True
        if (self.time_blocked == 25):
            self.time_blocked = 0

        action = {
            "acceleration": acceleration,
            "steer": steer,
            "brake": brake,
            "drift": False,
            "nitro": nitro,
            "rescue": rescue,
            "fire": fire
        }
        return action
