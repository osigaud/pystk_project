import numpy as np
from utils.TrackUtils import compute_curvature, compute_slope

class MedianAgent:
    def __init__(self, env, path_lookahead=3):
        self.env = env
        self.path_lookahead = path_lookahead
        self.agent_positions = []
        self.obs = None
        self.isEnd = False
        self.threshold = 40
        #print(self.env.current_track)
        

    def reset(self):
        self.obs, _ = self.env.reset()
        self.agent_positions = []

    def endOfTrack(self):
        return self.isEnd

    def calculate_action(self, obs):
        # Basic path-following based on the centerline.
        path_ends = obs["paths_end"][:self.path_lookahead]
        path_end = path_ends[-1]
        kart_front = obs["front"]
        curvature = compute_curvature(path_ends)
        slope = compute_slope(path_ends[:2])
        direction_to_target = path_end - kart_front
        
        # Basic control.
        steering = 0.2 * direction_to_target[0]
        acceleration = max(0.5, 1 - abs(curvature) + max(0, slope))
        use_drift = abs(curvature) > 40
        use_nitro = abs(curvature) < 0.02

        distance = np.linalg.norm(obs["paths_end"][self.path_lookahead] - path_end)
        if distance > self.threshold: 
            print("End of track detected.", distance)
            self.isEnd = True

        if self.isEnd:
            action = {
                "acceleration": 1,
                "steer": 0,
                "brake": False,
                "drift": False,
                "nitro": True,
                "rescue": True,
                "fire": False
            }
            return action

        action = {
            "acceleration": np.clip(acceleration, 0.5, 1),
            "steer": np.clip(steering, -1, 1),
            "brake": False,
            "drift": use_drift,
            "nitro": use_nitro,
            "rescue": True,
            "fire": False
        }
        # Apply overtaking strategy.
        action = self._apply_overtaking_strategy(obs, action)
        return action

    def _apply_overtaking_strategy(self, obs, action):
        """
        If opponent karts are ahead within a vision radius, adjust the action to
        overtake by increasing acceleration and using nitro.
        Opponents are taken from obs["karts_position"], which is assumed to contain
        positions relative to our kart in its local frame.
        """
        opponents = obs.get("karts_position", [])
        if len(opponents) == 0:
            return action

        opp_array = np.array(opponents)  # shape (n, 3)
        # Compute distances for each opponent.
        distances = np.linalg.norm(opp_array, axis=1)
        # Project onto the XZ-plane.
        xz = opp_array[:, [0, 2]]
        # Define the forward vector in XZ-plane.
        forward = np.array([0, 1])
        
        # Helper: compute angle between two 2D vectors.
        def angle_between(v1, v2):
            cos_theta = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-6)
            cos_theta = np.clip(cos_theta, -1.0, 1.0)
            return np.degrees(np.arccos(cos_theta))
        
        angles = np.array([angle_between(xz[i], forward) for i in range(xz.shape[0])])
        # Consider opponents that are ahead (in local frame, positive Z).
        ahead = opp_array[:, 2] > 0
        # Only consider opponents that are within 30 m and within 30°.
        mask = (distances < 30) & (angles < 30) & ahead

        if np.any(mask):
            if np.any(distances[mask] < 5):
                action["acceleration"] = 1.0
                action["nitro"] = True
                # print("Overtaking: very close opponent, accelerating and using nitro.")
            else:
                action["acceleration"] = max(action["acceleration"], 0.8)
                action["nitro"] = True
                # print("Overtaking: moderate opponent ahead, increasing acceleration and using nitro.")
        return action

    def step(self):
        action = self.calculate_action(self.obs)
        self.obs, reward, done, truncated, info = self.env.step(action)
        self.agent_positions.append(np.array(self.env.unwrapped.world.karts[0].location))
        return done

    def run(self, steps=10000):
        self.reset()
        for _ in range(steps):
            done = self.step()
            yield self.obs
            if done:
                break
        self.env.close()
