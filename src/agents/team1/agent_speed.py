from .agent_center import AgentCenter

class AgentSpeed(AgentCenter):
    def __init__(self, env, path_lookahead=3):
        super().__init__(env, path_lookahead)
        self.ecartpetit = ECARTPETIT #seuil a partir du quel on considere l'ecart comme petit (ligne droite)o
        self.ecartgrand = ECARTGRAND #seuil a partir du quel on considere l'ecart comme grand (virage serré)
        self.msapetit = MSAPETIT  
        self.msagrand = MSAGRAND
        
    def analyse(self, obs):
        virage_serre = False
        nbsegments = min(self.path_lookahead, len(obs["paths_start"]))
        for i in range(nbsegments):
       		segdirection = obs["paths_end"][i] - obs["paths_start"][i]
       		diff = segdirection - obs["front"]
       		ecart = float(np.linalg.norm(diff))
       		dist = abs(obs["paths_distance"][i][0] - obs["paths_distance"][0][0])
        		
        	if ecart >= self.ecartgrand and dist < 10:
        		virage_serre = True
      
        
        return virage_serre
        

    def limit(self, acceleration) : 
        if acceleration >= 1 : 
            return 1
        if acceleration <= 0 : 
            return 0.1
        return acceleration
        		
    def reaction(self, virage_serre, act, obs):
		msa = obs["max_steer_angle"]

		# ligne droite
		if not virage_serre:
		    act["acceleration"] = 1

		    segdirection = obs["paths_end"][0] - obs["paths_start"][0]
		    if segdirection[1] > 0.05:
		        act["acceleration"] = self.limit(act["acceleration"] + 0.2)

		    return act

		# virage serré
		if msa <= self.msapetit:
		    accel = act["acceleration"] - 0.45
		    act["acceleration"] = self.limit(accel)

		elif msa >= self.msagrand:
		    accel = act["acceleration"] + 0.5
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
