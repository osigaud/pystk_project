class EsquiveAdv:
    
    def esquive_adv(self,obs):

        kart_pos = obs.get('karts_position', []) 
        if len(kart_pos) == 0:
            return False, 0.0, 0.0

        adv=kart_pos[0]
        devant=False
        if -0.8 <= adv[0] <=0.8 and  0.1<= adv[2]<=1.3:
            devant=True

        return devant,adv[0],adv[2]
    
