from .steering import Steering

class useItems:
    def __init__(self):
        self.steerer = Steering()
    def use_items(self, obs, steer):
        item = int(obs.get("powerup", 0))

        # Bubblegum Cake Switch
        if item in (1, 2, 6):
            return True, steer

        # Zipper
        if item == 4:
            if (abs(steer) < 0.4):
                return True, steer

        # Swatter
        if item == 7:
            for kart in obs.get("karts_position", []):
                x, z = float(kart[0]), float(kart[2])
                if -0.4 <= x <= 0.4 and 2.0 <= z <= 5.0:
                    return True, steer

        # Bowling Ball, Plunger, RubberBall, Parachute, Anvil
        if item in (3, 5, 8, 9, 10):
            for kart in obs.get("karts_position", []):
                x, z = float(kart[0]), float(kart[2])
                if -0.8 <= x <= 0.8 and 2.0 <= z <= 25.0:
                    target = self.steerer.manage_pure_pursuit(x, z, 0.7)
                    new_steer = float(0.8 * steer + 0.2 * target)
                    return True, new_steer

        # Nothing
        return False, steer
