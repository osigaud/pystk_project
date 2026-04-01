DemoPilote

Installation de doxygen: 
Il faut s'assurer d'etre bien sur la branche demoPilote/src/agents/team2
et on utilise la commande:
    doxygen -g Doxyfile


    pour generer la documentation du doxyfile:
         doxygen Doxyfile


        

Utilisation du fichier de configuration dans un wrapper ou dans agent2:
    Prerequis:

        from omegaconf import OmegaConf
        cfg = OmegaConf.load("../agents/team2/configDemoPilote.yaml")

    Appel de variable:

        cfg.<nom_variable>
