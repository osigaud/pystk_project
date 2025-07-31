import numpy as np
import gymnasium as gym

"""
ItemObservationWrapper: An observation wrapper that enriches the observation
- inspired from Nazim Bendib and Nassim Boudjenah's work on item-based decision making.
"""

class ItemObservationWrapper(gym.ObservationWrapper):
    """
    Enriches the observation with computed item-related variables.
    New keys added:
    - target_item_position: the position (3D vector) of the chosen target item (good or bad)
    - target_item_distance: the Euclidean distance to that item
    - target_item_angle: the angle (in degrees) between the kart's forward direction and the item
    - target_item_type: the type of the target item (integer code)
    """
    def __init__(self, env: gym.Env):
        super().__init__(env)
        from gymnasium import spaces
        # Add new keys to the observation space.
        # (Adjust the bounds if necessary.)
        self.observation_space.spaces['target_item_position'] = spaces.Box(-np.inf, np.inf, (3,), dtype=np.float32)
        self.observation_space.spaces['target_item_distance'] = spaces.Box(0, np.inf, (1,), dtype=np.float32)
        self.observation_space.spaces['target_item_angle'] = spaces.Box(-np.inf, np.inf, (1,), dtype=np.float32)
        # Assume a maximum of 10 different item types.
        self.observation_space.spaces['target_item_type'] = spaces.Discrete(10)

    def observation(self, obs):
        items_pos = np.array(obs.get('items_position', []))
        items_type = np.array(obs.get('items_type', []))
        # We assume the observation already transformed to the kart's local frame,
        # where the forward direction is along positive Z.
        # If not, you would need to perform a transformation using the kart's front vector.
        if items_pos.size == 0:
            # No items; set defaults.
            obs['target_item_position'] = np.zeros(3, dtype=np.float32)
            obs['target_item_distance'] = np.array([np.inf], dtype=np.float32)
            obs['target_item_angle'] = np.array([0], dtype=np.float32)
            obs['target_item_type'] = 0
            return obs

        # Ensure items_pos is (N,3)
        if len(items_pos.shape) == 1:
            items_pos = np.expand_dims(items_pos, axis=0)
        N = items_pos.shape[0]
        # Compute Euclidean distance for each item
        distances = np.linalg.norm(items_pos, axis=1)
        # Compute angle in the XZ plane: angle between [0,0,1] and the projection of item vector on XZ.
        angles = np.degrees(np.arctan2(items_pos[:,0], items_pos[:,2]))
        # Define which types are “good” and which are “bad”
        # (For example, assume: BONUS_BOX (0), NITRO_BIG (2), NITRO_SMALL (3) and EASTER_EGG (6) are good;
        #  BANANA (1) and BUBBLEGUM (4) are bad.)
        good_types = [0, 2, 3, 6]
        bad_types = [1, 4]
        # We only consider items that are ahead (positive Z) and reasonably close.
        ahead_mask = items_pos[:,2] > 0
        valid_mask = ahead_mask & (distances < 10) & (np.abs(angles) < 30)
        target_index = None
        # Prefer good items if available.
        if np.any(valid_mask & np.isin(items_type, good_types)):
            idx = np.where(valid_mask & np.isin(items_type, good_types))[0]
            target_index = idx[np.argmin(distances[idx])]
        elif np.any(valid_mask & np.isin(items_type, bad_types)):
            idx = np.where(valid_mask & np.isin(items_type, bad_types))[0]
            target_index = idx[np.argmin(distances[idx])]
        elif np.any(valid_mask):
            idx = np.where(valid_mask)[0]
            target_index = idx[np.argmin(distances[idx])]

        if target_index is not None:
            target_position = items_pos[target_index]
            target_distance = distances[target_index]
            target_angle = angles[target_index]
            target_type = int(items_type[target_index])
        else:
            target_position = np.zeros(3, dtype=np.float32)
            target_distance = np.inf
            target_angle = 0
            target_type = 0

        obs['target_item_position'] = target_position.astype(np.float32)
        obs['target_item_distance'] = np.array([target_distance], dtype=np.float32)
        obs['target_item_angle'] = np.array([target_angle], dtype=np.float32)
        obs['target_item_type'] = target_type
        return obs
