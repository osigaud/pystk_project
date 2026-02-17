import numpy as np
import random

from utils.track_utils import compute_curvature, compute_slope
from agents.kart_agent import KartAgent
from .steering import Steering
from .rescue import RescueManager
from .speed import SpeedController
from .nitrodrift import NitroDrift


class Agent4(KartAgent):
    def __init__(self, env, path_lookahead=5):
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
        self.during_drift = 0

    def reset(self):
        self.obs, _ = self.env.reset()
        self.agent_positions = []
        self.drift_cd = 0

    def endOfTrack(self):
        return self.isEnd

    def choose_action(self, obs):
        
        steering = self.steering.manage_pure_pursuit(obs)
        distance = float(obs.get("distance_down_track", [0.0])[0])
        v = obs.get("velocity", [0.0, 0.0, 0.0])
        speed = float((v[0]*v[0] + v[2]*v[2]) ** 0.5)
        energy = float(obs.get("energy", [0.0])[0])

        if self.drift_cd > 0:
            drift = False
            self.drift_cd -= 1
        else:
            drift, steering = self.nitrodrift.manage_drift(steering, distance)
            if drift:
                self.during_drift += 1
            else :
                self.during_drift = 0
            
            if self.during_drift > 3:
                self.drift_cd = 7
                self.during_drift = 0
        brea = False
        acceleration, brea = self.SpeedController.manage_speed(steering,speed,drift)
        #print("The winners : ", speed)

        nitro = self.nitrodrift.manage_nitro(steering, energy)
        if (drift == True):
            nitro = False


        if(self.rescue.is_stuck(distance,speed)):
            return self.rescue.sortir_du_mur(steering)
        action = {
            "acceleration": acceleration,
            "steer": steering,
            "brake": brea,
            "drift": drift,
            "nitro": nitro,
            "rescue":False,
            "fire": False,
        }
        return action
