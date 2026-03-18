import numpy as np
from agents.kart_agent import KartAgent


class Agent5NitroTracker(KartAgent):
    def __init__(self, env, pilot_agent, conf, path_lookahead=3):
        super().__init__(env)
        self.path_lookahead = path_lookahead
        self.pilot = pilot_agent
        self.name = "Donkey Bombs NitroTracker"
        self.conf = conf

    def reset(self):
        self.pilot.reset()

    def choose_action(self, obs):
        action = self.pilot.choose_action(obs)

        # Si le pilote est en drift ou rescue, on ne touche à rien
        if action.get("drift", False) or action.get("rescue", False):
            return action

        items_pos = np.array(obs["items_position"])
        items_type = obs["items_type"]

        if items_type is None or len(items_type) == 0:
            return action

        # On filtre les nitros devant le kart (types 2 et 3)
        nitros = [
            (items_pos[i][0], items_pos[i][2])
            for i, t in enumerate(items_type)
            if t in (2, 3) and 0 < items_pos[i][2] < self.conf.nitro_tracker.max_distance
        ]

        if not nitros:
            return action

        # On prend le nitro le plus proche
        nx, nz = min(nitros, key=lambda n: np.hypot(n[0], n[1]))

        # On calcule un steering d'attraction et on le mélange avec celui du pilote
        attraction = float(np.clip(nx / max(nz, 0.1), -1.0, 1.0))
        alpha = self.conf.nitro_tracker.blend_factor  # ex: 0.3
        action["steer"] = float(np.clip(
            (1.0 - alpha) * action["steer"] + alpha * attraction,
            -1.0, 1.0
        ))

        return action