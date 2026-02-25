class Banana:

    """
    Module Banana : Gère la logique de détection de bananes et de chewing-gum
    """
    
    def banana_detection(self,obs,limit_path,center_path):
        """
        Gère la détection des bananes et de chewing-gum

        Args:
            obs(dict) : Les données fournies par le simulateur.
            limit_path(float) : Limite calculée de la piste.
            center_path(float) : Centre de la piste par rapport à la situation de notre agent.
        
        Returns:
            str : Variable donnant le mode d'esquive auquel on est confronté.
            float : Valeur représentant un décalage latéral ou la position de la banane (LIGNE / SINGLE).
            list : Liste contenant les bananes.
        """

        items_pos = obs['items_position'] # Récupération des positions des items
        items_type = obs['items_type'] # Récupération des types des items

        banana = [] # Liste qui va accueillir nos bananes

        for i in range(len(items_pos)):
            if items_type[i] == 1 or items_type[i] == 4: # Si c'est une banane ou une chewing-gum
                pos_x = items_pos[i][0] # On récupère le décalage latéral 
                pos_z = items_pos[i][2] # On récupère la profondeur

                dist_obj_centre= abs(center_path+pos_x) #Calcul de la distance absolu de l'objet

                if dist_obj_centre > limit_path: # Si l'objet est hors des limites de la piste, on ne le prend pas en compte
                    continue

                if -2.0 <= pos_x <= 2.0 and 0.0 <= pos_z <= 17.0: # Si la banana est dans notre radar, on l'ajoute dans notre liste
                    banana.append((pos_x,pos_z))

        banana.sort(key=lambda x: x[1]) # On trie la liste par ordre croissant selon la profondeur

        if len(banana) == 0: # Rien à signaler
            return "CLEAR",None,None
        
        first = banana[0] # On récupère la banane la plus proche
        first_x = first[0]
        first_z = first[1]

        if len(banana) >=2: #Si on a plus de deux bananes dans notre liste
            second = banana[1] # On récupère la seconde
            x = second[0]
            z = second[1]
            if abs(z-first_z) <= 2.0: # Si les bananes forment une ligne (un barrage)
                gap_x = (x+first_x)/2.0
                return "LIGNE", gap_x, banana
            else:
                return "SINGLE", first_x,banana # On revient sur le cas de la banane seule
        else:
            return "SINGLE",first_x,banana # Cas d'une seule banane