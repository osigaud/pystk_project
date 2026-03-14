from agents.kart_agent import KartAgent
import numpy as np

class AgentSpeed(KartAgent):
    def __init__(self, env, conf, agent, path_lookahead=3):
        super().__init__(env)
        self.conf = conf
        self.agent = agent
        self.path_lookahead = path_lookahead

        self.ecartpetit = self.conf.ecartpetit #seuil a partir du quel on considere l'ecart comme petit (ligne droite)o
        self.ecartgrand = self.conf.ecartgrand #seuil a partir du quel on considere l'ecart comme grand (virage serré)
        self.msapetit = self.conf.msapetit  #seuil a partir duquel max steer angle ne permet pas de bien tourner le volant
        self.msagrand = self.conf.msagrand  #seuil a partir duquel max steer angle ne permet de bien tourner le volant
        self.accel_ligne_droite = self.conf.accel_ligne_droite
        self.frein_virage = self.conf.frein_virage
        self.accel_virage = self.conf.accel_virage
        self.dist_segment = self.conf.dist_segment
        
    def analyse(self, obs):
        virage_serre = False
        nbsegments = min(self.path_lookahead, len(obs["paths_start"]))
        for i in range(nbsegments):
            segdirection = obs["paths_end"][i] - obs["paths_start"][i]
            diff = segdirection - obs["front"]
            ecart = float(np.linalg.norm(diff))
            dist = abs(obs["paths_distance"][i][0] - obs["paths_distance"][0][0])
                
            if ecart >= self.ecartgrand and dist < self.dist_segment:
                virage_serre = True
      
        return virage_serre
        
    def reaction(self, virage_serre, act, obs):
        act["acceleration"] = max(act["acceleration"], 1)
        msa = obs["max_steer_angle"]

        # ligne droite
        if not virage_serre:
            act["acceleration"] = self.accel_ligne_droite

            segdirection = obs["paths_end"][0] - obs["paths_start"][0]
            if segdirection[1] > 0.05:
                act["acceleration"] = np.clip(act["acceleration"], 0.1, 1)      #self.limit(act["acceleration"] + 0.2)

            return act

        # virage serré
        if msa <= self.msapetit:
            accel = act["acceleration"] - self.frein_virage
            act["acceleration"] = np.clip(accel, 0.1, 1)

        elif msa >= self.msagrand:
            accel = act["acceleration"] + self.accel_virage
            act["acceleration"] = np.clip(accel, 0.1, 1)

        segdirection = obs["paths_end"][0] - obs["paths_start"][0]
        if segdirection[1] > 0.05:
            act["acceleration"] = np.clip(act["acceleration"], 0.1, 1) 

        return act
  
    def choose_action(self, obs):
        act = self.agent.choose_action(obs)
        virage_serre = self.analyse(obs)
        act_corr = self.reaction(virage_serre, act, obs)
        return act_corr

