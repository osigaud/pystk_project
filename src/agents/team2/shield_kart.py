## @file    shield_kart.py
#  @brief   Gestion de l'activation du shield et des items offensifs.
#  @author  Équipe 2 DemoPilote: Mariam Abd El Moneim, Sokhna Oumou Diouf, Ayse Koseoglu, Leon Mantani, Selma Moumou et Maty Niang
#  @date    20-01-2026

import numpy as np

## @class   ActiveShield
#  @brief   Décide d'utiliser l'item en possession selon la situation de course.
#
#  Utilise AttackRivals pour détecter la présence d'un adversaire devant
#  le kart, puis décide si l'item courant doit être activé.
#  Le bubblegum est posé derrière (item défensif), les autres items
#  sont tirés vers l'avant (items offensifs).
#
#  @see AttackRivals

class ActiveShield:
    def __init__(self):
        #détection autour du kart 
        self.proximite= 10.0 

    def fire_shield(self, obs):
        """
        Gère l'activation du shield en fonction de la proximité des rivaux.
        """
        #récupère le chiffre qui correspond au type de l'item 
        p_type = obs.get("powerup_type")
        karts_pos = obs.get('karts_position', [])
        
        for pos in karts_pos:
            #calcul de la distance entre notre kart et l'adversaire
            dist = np.linalg.norm(pos)
            z = pos[2] 

            # Si un kart est dans notre cercle de proximité
            if dist < self.proximite:
                
                #si c'est un Bubblegum (type 1) -> le lâcher que si le kart est derrière nous (z < 0)
                if p_type == 1:
                    if z < 0:
                        return True
                
                #pour tous les autres types d'items (bouclier, gateau, ventouse...)
                else:
                    return True #activation peu importe z
                    
        return False
