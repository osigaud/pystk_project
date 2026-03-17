import optuna 
import yaml 
import subprocess


def objective(trial):
    correction = trial.suggest_float("correction", 0.1, 1.0)
    curvature = trial.suggest_float("curvature", 0.1, 0.8)

    chemin_yaml = "configDemoPilote.yaml"

    #ouverture de notre fichier de configuration 
    with open(chemin_yaml, 'r') as fichier:
        config = yaml.safe_load(fichier)

    #Changement des valeurs par les ce qui sont inventes par optuna 
    config['correction'] = correction
    config['curvature'] = curvature

    with open(chemin_yaml, 'w') as fichier:
        yaml.dump(config, fichier)


    #le lancement automatique du jeu 

    resultat = subprocess.run(
        ["uv", "run", "multi_track_race_display.py"], 
        capture_output=True, #Ça capture tout le texte que le jeu affiche à la fin
        text=True,
        cwd="../../main"
        
    )


    

    
    #on met un chrono de base de 300
    temps_course = 300.0 
    
    

    # On lit chaque ligne une par une jusqu'à trouver celle du temps
    lignes_du_terminal = resultat.stdout.split('\n')
    for ligne in lignes_du_terminal:
        if "Time" in ligne: #Si le mot Time est dans la phrase
            mots = ligne.split()        #On coupe la phrase en mots
            temps_course = float(mots[-1]) #On prend le tout dernier mot 
            break #On a trouvé le temps, on arrête de chercher 

    return temps_course


#programme principale pour voir les valeurs prises par optuna 

if __name__ == "__main__":
    etude = optuna.create_study(direction="minimize") #le but absolu c'est de trouver le resultat le plus petit possible 
    #on lance 10 essais (trial)
    etude.optimize(objective, n_trials=10)
    print("Le meilleur temps obtenu est :", etude.best_value)
    print(" Les meilleurs réglages pour ton YAML sont :")
    for cle, valeur in etude.best_params.items():
        print(f"  - {cle}: {valeur}")
