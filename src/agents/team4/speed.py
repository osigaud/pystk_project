class SpeedController:
    def manage_speed(self, steer, speed, drift):
        a = abs(steer)

        if drift:
            if a > 0.95 and speed > 20.0:
                return 0.98, False
            return 1.0, False

        if a > 0.95 and speed > 20.0:
            return 0.22, True

        if a > 0.90 and speed > 18.0:
            return 0.85, False

        if a > 0.75 and speed > 19.0:
            return 0.95, False

        return 1.0, False
