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
    correction = trial.suggest_float("correction", 0.1, 1.0)
    curvature  = trial.suggest_float("curvature",  0.1, 0.8)

    chemin_yaml = "configDemoPilote.yaml"

    # lecture du fichier de configuration existant
    with open(chemin_yaml, 'r') as fichier:
        config = yaml.safe_load(fichier)

    # remplacement des valeurs par celles proposées par Optuna
    config['correction'] = correction
    config['curvature']  = curvature

    # écriture du fichier mis à jour
    with open(chemin_yaml, 'w') as fichier:
        yaml.dump(config, fichier)

    # lancement de la course dans un sous-processus
    # capture_output=True récupère tout ce qui est affiché dans le terminal
    resultat = subprocess.run(
        ["uv", "run", "multi_track_race_display.py"],
        capture_output=True,
        text=True,
        cwd="../../main"
    )

    # valeur par défaut si le temps n'est pas trouvé dans la sortie
    temps_course = 300.0

    # on cherche la ligne contenant "Time" dans la sortie standard
    lignes_du_terminal = resultat.stdout.split('\n')
    for ligne in lignes_du_terminal:
        if "Time" in ligne:       # ligne contenant le temps de course
            mots         = ligne.split()
            temps_course = float(mots[-1])  # le temps est le dernier mot de la ligne
            break

    return temps_course


## @brief   Point d'entrée : lance l'étude Optuna et affiche les meilleurs paramètres.
#
#  Crée une étude en mode minimisation et lance 10 essais.
#  Affiche à la fin le meilleur temps obtenu et les valeurs de paramètres
#  correspondantes.
if __name__ == "__main__":
    # direction="minimize" : on cherche le temps de course le plus court
    etude = optuna.create_study(direction="minimize")
    etude.optimize(objective, n_trials=10)

    print("Le meilleur temps obtenu est :", etude.best_value)
    print(" Les meilleurs réglages pour ton YAML sont :")
    for cle, valeur in etude.best_params.items():
        print(f"  - {cle}: {valeur}")