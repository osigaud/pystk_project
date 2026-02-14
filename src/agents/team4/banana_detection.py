class Banana:

    def banana_detection(self,obs):

        items_pos = obs['items_position'] # Récupération des positions des items
        items_type = obs['items_type'] # Récupération des types des items

        clo_banana_z = float("inf") # Variable pour detecter la variable la plus proche sur l'axe z
        clo_banana_x = 0.0 # Variable pour detecter la variable la plus proche sur l'axe x
        trouve = False  # Variable permettant de dire si une banane, sous certaines conditions, a été trouvée

        for i in range(len(items_pos)): #Boucle pour parcourir la liste entière des items
            if items_type[i] == 1: #Si c'est une banane 
                pos_x = items_pos[i][0] # On récupère le décalage latéral
                pos_z = items_pos[i][2] # On récupère la profondeur
                if -2.5 <= pos_x <= 2.5 and 0.0 <= pos_z <= 20.0:
                    if pos_z < clo_banana_z: # Si la banane trouvée est plus proche que celle déjà trouvée
                        clo_banana_z = pos_z
                        clo_banana_x = pos_x
                        trouve = True
        
        return trouve, clo_banana_x, clo_banana_z