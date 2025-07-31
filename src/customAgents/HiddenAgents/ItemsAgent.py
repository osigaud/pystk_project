import numpy as np

# Mapping of obstacle item type codes to names (for debug output)
ITEM_TYPE_NAMES = {
    0: "BONUS_BOX",
    1: "BANANA",
    2: "NITRO_BIG",
    3: "NITRO_SMALL",
    4: "BUBBLEGUM",
    6: "EASTER_EGG"
}

# Mapping of powerup types.
# According to the STK documentation,
# Powerups:
#   'NOTHING': 0,
#   'BUBBLEGUM': 1,
#   'CAKE': 2,
#   'BOWLING': 3,
#   'ZIPPER': 4,
#   'PLUNGER': 5,
#   'SWITCH': 6,
#   'SWATTER': 7,
#   'RUBBERBALL': 8,
#   'PARACHUTE': 9,
#   'ANVIL': 10
# For our strategic usage, we assume that:
#   - Speed boost powerups (nitro-like) are represented by ZIPPER (4)
#   - Weapon-type powerups are represented by BOWLING (3), PLUNGER (5), and SWATTER (7)
#   - Other powerups we use immediately if held.
SPEED_BOOST_POWERUPS = [4]
WEAPON_POWERUPS = [3, 5, 7]

class ItemsAgent:
    """
    An agent that decorates an existing agent (e.g., EulerAgent or MedianAgent) to add
    item-based decision making and strategic powerup usage.
    
    This agent obtains a base action from the wrapped agent, then adjusts its steering
    based on enriched item observations (which include keys such as:
        - target_item_position (3D vector)
        - target_item_distance (scalar)
        - target_item_angle (in degrees)
        - target_item_type (integer code)
    ), and finally applies a powerup usage strategy.
    """
    def __init__(self, wrapped_agent):
        self.agent = wrapped_agent  # Wrapped agent (e.g., EulerAgent)
        self.env = wrapped_agent.env
        self.path_lookahead = wrapped_agent.path_lookahead
        self.agent_positions = wrapped_agent.agent_positions
        self.obs = None

    def reset(self):
        self.agent.reset()
        self.obs = self.agent.obs

    def endOfTrack(self):
        return self.agent.endOfTrack()

    def _get_base_action(self, obs):
        """Get the base action from the wrapped agent."""
        return self.agent.calculate_action(obs)

    def _adjust_for_item(self, obs, action):
        """
        Adjust the steering based on enriched item observation.
        Expects the following keys in obs:
            - target_item_position: 3D vector of target item.
            - target_item_distance: scalar distance to target item.
            - target_item_angle: angle in degrees.
            - target_item_type: integer code.
        """
        target_distance = obs.get("target_item_distance", np.array([np.inf]))[0]
        target_angle = obs.get("target_item_angle", np.array([0]))[0]
        target_type = obs.get("target_item_type", 0)
        # Get human-readable name for debugging.
        item_name = ITEM_TYPE_NAMES.get(target_type, "UNKNOWN")
        # print(f"Item target: {item_name}, distance {target_distance:.2f}, angle {target_angle:.2f}")
        
        # Define which items (by type code) are considered good and which bad.
        good_types = [0, 2, 3, 6]  # e.g., BONUS_BOX, NITRO_BIG, NITRO_SMALL, EASTER_EGG
        bad_types = [1, 4]         # e.g., BANANA, BUBBLEGUM
        
        if target_distance < 10:
            target_item_pos = obs.get("target_item_position", np.array([0, 0, 0]))
            if target_type in good_types:
                action["steer"] += 0.1 * target_item_pos[0]
                # print("Approaching good item.")
            elif target_type in bad_types:
                action["steer"] -= 0.1 * target_item_pos[0]
                # print("Avoiding bad item.")
        # else:
        #    print("No target item in close range; following base path.")
        return action

    def _apply_powerup_strategy(self, obs, action):
        """
        Applies strategic powerup usage based on the current powerup in the observation.
        
        Expected observation: obs["powerup"] holds an integer code.
            - If the powerup is a speed boost (in SPEED_BOOST_POWERUPS), use it only on straight segments.
            - If it is a weapon (in WEAPON_POWERUPS), check for nearby opponents (from obs["karts_position"]) and use it if any is close.
            - Otherwise, if any other powerup is held, use it immediately.
        """
        powerup = obs.get("powerup", 0)
        fire = False

        # Compute a simple curvature from the path endpoints.
        path_ends = obs["paths_end"][:self.path_lookahead]
        if len(path_ends) >= 3:
            p1 = np.array(path_ends[0])
            p2 = np.array(path_ends[len(path_ends)//2])
            p3 = np.array(path_ends[-1])
            v1 = p2 - p1
            v2 = p3 - p2
            cross_norm = np.linalg.norm(np.cross(v1, v2))
            dot_product = np.dot(v1, v2)
            angle = np.arctan2(cross_norm, dot_product)
            distance = np.linalg.norm(v1) + np.linalg.norm(v2)
            curvature = abs(angle) / max(distance, 1e-6)
        else:
            curvature = 0.1
        
        # Strategic decision:
        if powerup in SPEED_BOOST_POWERUPS:
            # Use speed boost only when the track is nearly straight.
            if curvature < 0.05:
                fire = True
                # print("Using speed boost powerup on a straight line.")
        elif powerup in WEAPON_POWERUPS:
            # For weapon-type powerups, check for opponents.
            opponents = obs.get("karts_position", [])
            for opp in opponents:
                opp = np.array(opp)
                opp_distance = np.linalg.norm(opp)
                if opp_distance < 10 and opp[2] > 0:
                    fire = True
                    # print("Using weapon powerup on a nearby opponent.")
                    break
        elif powerup != 0:
            # For other powerups, use them immediately.
            fire = True
            # print("Using miscellaneous powerup.")

        action["fire"] = fire
        return action

    def calculate_action(self, obs):
        """
        Computes the final action by combining:
            1. The base action from the wrapped agent.
            2. Adjustments based on item observation.
            3. Strategic powerup usage.
        """
        action = self._get_base_action(obs)
        if not self.agent.endOfTrack():
            action = self._adjust_for_item(obs, action)
            action = self._apply_powerup_strategy(obs, action)
            action["steer"] = np.clip(action["steer"], -1, 1)
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
