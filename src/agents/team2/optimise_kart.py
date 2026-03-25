## @file    optimise_kart.py

#  @brief   Optimisation automatique des paramètres du pilote via Optuna.

#  @author  Équipe 2 DemoPilote: Mariam Abd El Moneim, Sokhna Oumou Diouf, Ayse Koseoglu, Leon Mantani, Selma Moumou et Maty Niang

#  @date    20-01-2026


import optuna

import yaml

import subprocess



## @brief   Fonction objectif évaluée par Optuna à chaque essai.

#

#  À chaque appel, Optuna propose de nouvelles valeurs pour "correction"

#  et "curvature", les écrit dans configDemoPilote.yaml, lance une course

#  complète via subprocess et récupère le temps de course dans la sortie

#  standard. Optuna cherche à minimiser ce temps.

#

#  @param   trial  Objet Optuna représentant un essai d'optimisation.

#                  Fournit les méthodes suggest_* pour proposer des valeurs.

#  @return  float : temps de course en secondes.

#                   Retourne 300.0 (valeur par défaut) si le temps n'est pas

#                   trouvé dans la sortie du programme.

def objective(trial):

    # optuna propose des valeurs dans les intervalles définis

    #correction = trial.suggest_float("correction", 0.1, 1.0)

    curvature  = trial.suggest_float("curvature",  0.1, 0.8)

    

    #parametre pour l'acceleration dans les differents virages 

    accel_tres_serre = trial.suggest_float("accel_tres_serre", 0.5, 0.85)

    accel_serre      = trial.suggest_float("accel_serre", accel_tres_serre, 0.90)

    accel_moyen      = trial.suggest_float("accel_moyen", accel_serre, 0.98)

    #en ligne droite 

    accel_virage     = trial.suggest_float("accel_virage", accel_moyen, 1.0)



    #parametre d'evitement 

    angle_evite_p = trial.suggest_float("angle_evite_p", 0.3, 0.9)


    

    #parametre des virages 

    frontiere_moyen_serrer = trial.suggest_float("frontiere_moyen_serrer", 0.02, 0.08)

    frontiere_serrer_drift = trial.suggest_float("frontiere_serrer_drift", frontiere_moyen_serrer + 0.01, 0.2)



    #parametre de gestion du recul 

    vitesse  = trial.suggest_float("vitesse", 0.1, 0.5)

    #steps    = trial.suggest_int("steps", 3, 10)

    recovery = trial.suggest_int("recovery", 10, 30)

    braquage = trial.suggest_float("braquage", 0.5, 1.0)



    #parametre du champ de vision pour l'attack 

    vision_dist  = trial.suggest_float("vision_dist", 20.0, 60.0)

    vision_angle = trial.suggest_float("vision_angle", 5.0, 30.0)







    chemin_yaml = "configDemoPilote.yaml"


    # lecture du fichier de configuration existant

    with open(chemin_yaml, 'r') as fichier:

        config = yaml.safe_load(fichier)


    # remplacement des valeurs par celles proposées par Optuna

    #config['correction'] = correction

    config['curvature']  = curvature


    config['angle_evite_p'] = angle_evite_p

    config['angle_evite_n'] = -angle_evite_p


    config['vitesse'] = vitesse

   # config['steps'] = steps

    config['recovery'] = recovery

    config['braquage'] = braquage


    config['acceleration']['virage_tres_serre'] = accel_tres_serre

    config['acceleration']['virage_serre'] = accel_serre

    config['acceleration']['virage_moyen'] = accel_moyen

    config['acceleration']['virage'] = accel_virage


    config['champs_vision']['dist'] = vision_dist

    config['champs_vision']['angle'] = vision_angle


    config['virages']['moyen']['i1'] = 0.0

    config['virages']['moyen']['i2'] = frontiere_moyen_serrer

    config['virages']['serrer']['i1'] = frontiere_moyen_serrer

    config['virages']['serrer']['i2'] = frontiere_serrer_drift

    config['virages']['drift'] = frontiere_serrer_drift


    # écriture du fichier mis à jour

    with open(chemin_yaml, 'w') as fichier:

        yaml.dump(config, fichier)


    # lancement de la course dans un sous-processus

    # capture_output=True récupère tout ce qui est affiché dans le terminal

    resultat = subprocess.run(

        ["python", "multi_track_race_display.py"],

        capture_output=True,

        text=True,

        cwd="../../main"

    )

    


    score_final = 10000.0  

    total_steps = 0.0

    courses_terminees = 0


    lignes_du_terminal = resultat.stdout.split('\n')

    for ligne in lignes_du_terminal:

        # On cherche la ligne qui indique qu'on a fini

        if "DemoPilote" in ligne and "finished" in ligne:

            mots = ligne.split()        

            steps_course = float(mots[-1]) 

            

            total_steps += steps_course

            courses_terminees += 1


    # On retourne le total des steps si au moins une course a réussi

    if courses_terminees > 0:

        return total_steps

    else:

        return score_final



## @brief   Point d'entrée : lance l'étude Optuna et affiche les meilleurs paramètres.

#

#  Crée une étude en mode minimisation et lance 10 essais.

#  Affiche à la fin le meilleur temps obtenu et les valeurs de paramètres

#  correspondantes.

if __name__ == "__main__":

    # direction="minimize" : on cherche le temps de course le plus court

    etude = optuna.create_study(direction="minimize")

    etude.optimize(objective, n_trials=2)


    print("Le meilleur temps obtenu est :", etude.best_value)

    print(" Les meilleurs réglages pour ton YAML sont :")

    for cle, valeur in etude.best_params.items():

        print(f"  - {cle}: {valeur}")
