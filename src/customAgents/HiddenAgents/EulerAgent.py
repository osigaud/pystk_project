import numpy as np
from utils.TrackUtils import compute_slope

"""
A decorator that wraps an existing agent (here it decorates a MedianAgent) to add curvature-based adjustments.
"""

class EulerAgent:
    def __init__(self, wrapped_agent):
        self.agent = wrapped_agent
        self.env = wrapped_agent.env
        self.path_lookahead = wrapped_agent.path_lookahead
        self.agent_positions = wrapped_agent.agent_positions
        self.obs = None

    def reset(self):
        self.agent.reset()
        self.obs = self.agent.obs

    def endOfTrack(self):
        return self.agent.endOfTrack()

    def euler_spiral_curvature(self, path_ends):
        if len(path_ends) < 3:
            return 0.01
        p1 = np.array(path_ends[0])
        p2 = np.array(path_ends[len(path_ends) // 2])
        p3 = np.array(path_ends[-1])
        v1 = p2 - p1
        v2 = p3 - p2
        cross_norm = np.linalg.norm(np.cross(v1, v2))
        dot_product = np.dot(v1, v2)
        angle = np.arctan2(cross_norm, dot_product)
        distance = np.linalg.norm(v1) + np.linalg.norm(v2)
        curvature = abs(angle) / max(distance, 1e-6)
        curvature = np.clip(curvature * 2.0, 0.01, 1.0)
        return curvature

    ###def calculate_action(self, obs):
        # Get the base action from the wrapped agent.
        base_action = self.agent.calculate_action(obs)
        path_ends = obs["paths_end"][:self.path_lookahead]
        curvature = float(self.euler_spiral_curvature(path_ends))
        slope = float(compute_slope(path_ends[:2]))
        # Compute direction from kart front to target node.
        direction_to_target = obs["paths_end"][self.path_lookahead - 1] - obs["front"]
        # Adjust steering using Euler's formula.
        steering = 0.4 * direction_to_target[0] / (1.0 + abs(curvature) * 0.5)
        base_action["steer"] = np.clip(steering, -1, 1)
        base_action["acceleration"] = max(0.5, 1 - abs(curvature) + max(0, slope))
        base_action["nitro"] = (abs(curvature) < 0.05)
        return base_action
    ###
    def calculate_action(self, obs):
        base_action = self.agent.calculate_action(obs)
        if self.agent.endOfTrack():
            return base_action

        path_ends = obs["paths_end"][:self.path_lookahead]
        path_end = path_ends[-1]
        kart_front = obs["front"]

        curvature = float(self.euler_spiral_curvature(path_ends))
        slope = float(compute_slope(path_ends[:2]))

        acceleration = max(0.5, 1 - abs(curvature) + max(0, slope))
        direction_to_target = path_end - kart_front
        steering = 0.4 * direction_to_target[0] / (1.0 + abs(curvature) * 0.5)
        use_nitro = abs(curvature) < 0.05

        return {
            "acceleration": np.clip(acceleration, 0.5, 1),
            "steer": np.clip(steering, -1, 1),
            "brake": False,
            "drift": False,
            "nitro": use_nitro,
            "rescue": True,
            "fire": False
        }
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
