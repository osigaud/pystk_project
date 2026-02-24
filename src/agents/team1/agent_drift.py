from .agent_speed import AgentSpeed
import numpy as np

#Agent qui derape quand la courbe est serree (virage serre)
class AgentDrift(AgentRescue)  :
    def __init__(self, env, path_lookahead = 3):
        super().__init__(env,path_lookahead)

    def drift_control(self, obs, action) :
        virage_serre = self.analyse(obs)
        speed = np.linalg.norm(obs["velocity"])

        if virage_serre and abs(action["steer"]) >= 0.5 and speed > 6:
            action["drift"] = True
        else :
            action["drift"] = False

        return action

    def choose_action(self, obs) :
        action = super().choose_action(obs)
        action = self.drift_control(obs, action)
        return action
