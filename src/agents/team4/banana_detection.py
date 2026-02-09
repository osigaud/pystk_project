class Banana:

    def banana_detection(self,obs):

        items_pos = obs['items_position']
        items_type = obs['items_type']

        for i in range(len(items_pos)):
            if items_type[i] == 1:
                pos_x = items_pos[i][0]
                pos_z = items_pos[i][2]
                if -2.5 <= pos_x <= 2.5 and 0.1 <= pos_z <= 8.0:
                    return True, pos_x
        return False,0