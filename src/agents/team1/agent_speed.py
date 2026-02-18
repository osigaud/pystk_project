from .agent_center import AgentCenter
from .agent_base import ECARTPETIT, ECARTGRAND, MSAPETIT, MSAGRAND, ACCEL_LIGNE_DROITE, FREIN_VIRAGE, ACCEL_VIRAGE, DIST_SEGMENT
import numpy as np


class AgentSpeed(AgentCenter):
    def __init__(self, env, path_lookahead=3):
        super().__init__(env, path_lookahead)
        self.ecartpetit = ECARTPETIT #seuil a partir du quel on considere l'ecart comme petit (ligne droite)o
        self.ecartgrand = ECARTGRAND #seuil a partir du quel on considere l'ecart comme grand (virage serré)
        self.msapetit = MSAPETIT  #seuil a partir duquel max steer angle ne permet pas de bien tourner le volant
        self.msagrand = MSAGRAND  #seuil a partir duquel max steer angle ne permet de bien tourner le volant
        self.accel_ligne_droite = ACCEL_LIGNE_DROITE
        self.frein_virage = FREIN_VIRAGE
        self.accel_virage = ACCEL_VIRAGE
        self.dist_segment = DIST_SEGMENT
        
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
        

    def limit(self, acceleration):
        if acceleration >= 1:
            return 1
        if acceleration <= 0:
            return 0.1
        return acceleration

    def reaction(self, virage_serre, act, obs):
        act["acceleration"] = max(act["acceleration"], 1)
        msa = obs["max_steer_angle"]

        # ligne droite
        if not virage_serre:
            act["acceleration"] = self.accel_ligne_droite

            segdirection = obs["paths_end"][0] - obs["paths_start"][0]
            if segdirection[1] > 0.05:
                act["acceleration"] = self.limit(act["acceleration"] + 0.2)

            return act

        # virage serré
        if msa <= self.msapetit:
            accel = act["acceleration"] - self.frein_virage
            act["acceleration"] = self.limit(accel)

        elif msa >= self.msagrand:
            accel = act["acceleration"] + self.accel_virage
            act["acceleration"] = self.limit(accel)

        segdirection = obs["paths_end"][0] - obs["paths_start"][0]
        if segdirection[1] > 0.05:
            act["acceleration"] = self.limit(act["acceleration"] + 0.2)

        return act
  
    def choose_action(self, obs):
        act = super().choose_action(obs)
        virage_serre = self.analyse(obs)
        act_corr = self.reaction(virage_serre, act, obs)
        return act_corr

