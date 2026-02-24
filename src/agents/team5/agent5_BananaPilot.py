import numpy as np
import random
from utils.track_utils import compute_curvature, compute_slope
from agents.kart_agent import KartAgent


class Agent5Banana(KartAgent):
    def __init__(self, env, pilot_agent, conf, path_lookahead=3):
        super().__init__(env)
        self.path_lookahead = path_lookahead
        self.pilot = pilot_agent
        self.name = "Donkey Bombs Banana"
        self.conf = conf

    def reset(self):
        self.pilot.reset()

    def detect_banana(self, obs):
        items_pos = np.array(obs["items_position"])
        items_type = obs["items_type"]

        if items_type is None or len(items_type) == 0:
            return False, 0.0, 1.0, False

        index_bananas = [i for i, j in enumerate(items_type) if j == 1]
        bananas = items_pos[index_bananas]

        if len(index_bananas) == 0:
            return False, 0.0, 1.0, False


        for b in bananas:
            x = b[0]
            z = b[2]

            if 0 < z < self.conf.banana.detection.max_distance and abs(x) < self.conf.banana.detection.safety_width:
                # Évitement
                if x < 0:
                    steering = self.conf.banana.avoidance.steering_force
                else :
                    steering = -self.conf.banana.avoidance.steering_force
                accel = self.conf.banana.avoidance.acceleration
                brake = False

                return True, steering, accel, brake

        return False, 0.0, 1.0, False

    def choose_action(self, obs):
        danger, steer, accel, brake = self.detect_banana(obs)
        if danger:
            return {
                "acceleration": accel,
                "steer": steer,
                "brake": brake,
                "drift": False, "nitro": False, "rescue": False, "fire": False
            }
        return self.pilot.choose_action(obs)