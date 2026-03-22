DemoPilote

Installation de doxygen:
     
    ....


    Ouvrir un fichier doxifile:


        ....

Utilisation du fichier de configuration dans un wrapper ou dans agent2:
    Prerequis:

        from omegaconf import OmegaConf
        cfg = OmegaConf.load("../agents/team2/configDemoPilote.yaml")

    Appel de variable:

        cfg.<nom_variable>
