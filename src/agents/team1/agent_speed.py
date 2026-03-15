from agents.kart_agent import KartAgent
import numpy as np

class AgentSpeed(KartAgent):
    def __init__(self, env, conf, agent, path_lookahead=3):
        super().__init__(env)
        self.conf = conf
        self.agent = agent
        self.path_lookahead = path_lookahead
        
    def detecter_virage(self, obs):
        virage_serre = False
        nbsegments = min(self.path_lookahead, len(obs["paths_start"]))
        for i in range(nbsegments):
            direction_segment = obs["paths_end"][i] - obs["paths_start"][i]
            diff_direction = direction_segment - obs["front"]
            ecart_direction = float(np.linalg.norm(diff_direction))
            distance_segment = abs(obs["paths_distance"][i][0] - obs["paths_distance"][0][0])
                
            if ecart_direction >= self.conf.ecartgrand and distance_segment < self.conf.dist_segment:
                virage_serre = True
      
        return virage_serre
        
    def ajuster_acceleration(self, virage_serre, act, obs):
        act["acceleration"] = max(act["acceleration"], 1)
        max_steer_angle = obs["max_steer_angle"]

        # ligne droite
        if not virage_serre:
            act["acceleration"] = self.conf.accel_ligne_droite

            direction_segment = obs["paths_end"][0] - obs["paths_start"][0]
            if direction_segment[1] > 0.05:
                act["acceleration"] = np.clip(act["acceleration"], 0.1, 1)      #self.limit(act["acceleration"] + 0.2)
            return act

        # virage serré
        if max_steer_angle <= self.conf.max_steer_angle_petit:
            acceleration_freinee = act["acceleration"] - self.conf.frein_virage
            act["acceleration"] = np.clip(acceleration_freinee, 0.1, 1)

        elif max_steer_angle >= self.conf.max_steer_angle_grand:
            acceleration_boostee = act["acceleration"] + self.conf.accel_virage
            act["acceleration"] = np.clip(acceleration_boostee, 0.1, 1)

        direction_segment = obs["paths_end"][0] - obs["paths_start"][0]
        if direction_segment[1] > 0.05:
            act["acceleration"] = np.clip(act["acceleration"], 0.1, 1) 

        return act
  
    def choose_action(self, obs):
        act = self.agent.choose_action(obs)
        virage_serre = self.detecter_virage(obs)
        action_ajustee = self.ajuster_acceleration(virage_serre, act, obs)
        return action_ajustee

