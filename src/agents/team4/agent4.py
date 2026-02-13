import numpy as np
import random

from utils.track_utils import compute_curvature, compute_slope
from agents.kart_agent import KartAgent
from .steering import Steering
from .rescue import RescueManager
from .speed import SpeedController
from .nitrodrift import NitroDrift
from .banana_detection import Banana


class Agent4(KartAgent):
    def __init__(self, env, path_lookahead=3):
        super().__init__(env)
        self.path_lookahead = path_lookahead
        self.agent_positions = []
        self.obs = None
        self.isEnd = False
        self.name = "The Winners"
        self.steering = Steering()
        self.rescue = RescueManager()
        self.SpeedController=SpeedController()
        self.nitrodrift = NitroDrift()
        self.drift_cd = 0
        self.banana_dodge = Banana()
        self.dodge_side = 0
        self.dodge_timer = 10
        self.last_banana_z = float("inf")
        
        

    def reset(self):
        self.obs, _ = self.env.reset()
        self.agent_positions = []
        self.drift_cd = 0
        self.dodge_timer = 0
        self.dodge_side = 0
        self.last_banana_z = float("inf")

    def endOfTrack(self):
        return self.isEnd

    def choose_action(self, obs):
        
        points = obs.get("paths_start",[])
        if len(points) <= 2:
            return {
                "acceleration": 1.0,
                "steer": 0.0,
                "brake": False,
                "drift": False,
                "nitro": False,
                "rescue":False,
                "fire": False,
            }
        
        target = points[2]
        gx = target[0]
        gz = target[2]

        danger, b_x, b_z = self.banana_dodge.banana_detection(obs)

        if danger:

            print("Danger "+str(b_x))

            if b_x >=0:
                new_side = -1
            else:
                new_side = 1

            if self.dodge_timer == 0:
                self.dodge_timer = 10
                self.dodge_side = new_side
                self.last_banana_z = b_z
            else:
                if new_side != self.dodge_side and b_z < self.last_banana_z:
                    self.dodge_side = new_side
                    self.dodge_timer = 10
                    self.last_banana_z = b_z
        
        if self.dodge_timer >0:
            self.dodge_timer -= 1

            esquive = 2.0

            gx += esquive * self.dodge_side

            steering = self.steering.manage_pure_pursuit(gx,gz,4.0)

            return {
                "acceleration": 0.8,
                "steer": steering,
                "brake": False,
                "drift": False,
                "nitro": False,
                "rescue":False,
                "fire": False,
            }


        
        
        
        steering = self.steering.manage_pure_pursuit(gx,gz,6.0)
        distance = float(obs.get("distance_down_track", [0.0])[0])
        vel = obs.get("velocity", [0.0, 0.0, 0.0])
        speed = float(vel[2])
        energy = float(obs.get("energy", [0.0])[0])
        """if self.drift_cd > 0:
            drift = False
            self.drift_cd -= 1
        else:
            drift, steering = self.nitrodrift.manage_drift(steering, distance)
            if drift:
                self.drift_cd = 12"""
        brea = False
        acceleration, brea = self.SpeedController.manage_speed(steering,distance)



        nitro = self.nitrodrift.manage_nitro(steering, energy)
        """if (drift == True):
            nitro = False"""


        if(self.rescue.is_stuck(distance,speed)):
            return self.rescue.sortir_du_mur(steering)
        action = {
            "acceleration": acceleration,
            "steer": steering,
            "brake": brea,
            "drift": False,
            "nitro": nitro,
            "rescue":False,
            "fire": False,
        }
        return action
