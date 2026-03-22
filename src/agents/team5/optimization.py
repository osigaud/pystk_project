import optuna
import numpy as np
import os
import warnings
from omegaconf import OmegaConf
from pathlib import Path

# On importe la fonction qui permet de lancer des courses dans le fichier multi_track afin de récupérer et d'extraire les scores de notre kart
from multi_track_race_display_team5 import main_loop

#Pour éviter les conflits avec python
os.environ["PYTHONWARNINGS"] = "ignore"
warnings.filterwarnings("ignore")

# Paths de nos deux fichiers config. 
BASE_DIR = Path(__file__).resolve().parent
BASE_CONFIG_PATH = BASE_DIR / "config.yaml"
OUTPUT_CONFIG_PATH = BASE_DIR / "config_opti.yaml"

def objective(trial, nb_courses, coeurs_course):
    params = {
        # Brain
        "pilot.brain.kp":trial.suggest_float("kp", 2.0, 12.0),
        "pilot.brain.kd":trial.suggest_float("kd", 0.5, 8.0),

        # Navigation
        "pilot.navigation.lookahead_meters":trial.suggest_float("lookahead_meters", 3.0, 12.0),
        "pilot.navigation.lookahead_max":trial.suggest_float("lookahead_max", 8.0, 20.0),
        "pilot.navigation.min_dist_safety":trial.suggest_float("min_dist_safety", 0.5, 3.0),
        "pilot.navigation.lookahead_speed_factor":trial.suggest_float("lookahead_speed_factor", 0.05, 0.6),

        # Speed control
        "pilot.speed_control.cornering_accel":trial.suggest_float("cornering_accel", 0.1, 0.8),
        "pilot.speed_control.steering_threshold":trial.suggest_float("steering_threshold", 0.3, 0.9),
        "pilot.speed_control.hairpin_threshold":trial.suggest_float("hairpin_threshold", 0.6, 1.0),
        "pilot.speed_control.hairpin_accel":trial.suggest_float("hairpin_accel", 0.1, 0.7),
        "pilot.speed_control.hairpin_brake_speed":trial.suggest_float("hairpin_brake_speed", 8.0, 25.0),

        # Banana detection
        "banana.detection.max_distance":trial.suggest_float("max_distance", 5.0, 20.0),
        "banana.detection.safety_width":trial.suggest_float("safety_width", 0.8, 3),

        # Banana avoidance
        "banana.avoidance.steering_force":trial.suggest_float("steering_force", 0.3, 1.0),
        "banana.avoidance.acceleration":trial.suggest_float("banana_acceleration", 0.1, 0.8),

        # Banana edge safety
        "banana.edge_safety.max_center_dist":trial.suggest_float("max_center_dist", 2.0, 14.0),
        "banana.edge_safety.steering_correction":trial.suggest_float("steering_correction", 0.2, 1.0),
        "banana.edge_safety.correction_accel":trial.suggest_float("correction_accel", 0.3, 1.0),

        # Nitro
        "nitro.detection.steering_threshold_nitro":trial.suggest_float("steering_threshold_nitro", 0.05, 0.5),
        "nitro.detection.min_acceleration":trial.suggest_float("min_acceleration", 0.5, 1.0),

        # Drift
        "drift.drift_steer_angle":trial.suggest_float("drift_steer_angle", 0.3, 1.0),
        "drift.far_lookahead":trial.suggest_float("far_lookahead", 6.0, 20.0),
        "drift.near_lookahead":trial.suggest_float("near_lookahead", 2.0, 8.0),
        "drift.far_target_threshold":trial.suggest_float("far_target_threshold", 1.0, 8.0),
        "drift.steer_trigger":trial.suggest_float("steer_trigger", 0.2, 0.9),
        "drift.confirmation_frames":trial.suggest_int("confirmation_frames", 1, 10),
        "drift.min_speed":trial.suggest_float("min_speed", 5.0, 18.0),
        "drift.max_dist_center":trial.suggest_float("max_dist_center", 2.0, 7.0),
        "drift.exit_target_threshold":trial.suggest_float("exit_target_threshold", 0.3, 3.0),
        "drift.cooldown_frames":trial.suggest_int("cooldown_frames", 5, 10),
        "drift.drift_accel":trial.suggest_float("drift_accel", 0.5, 1.0)
    }


    # On charge en mémoire le fichier config de base "config.yaml"
    cfg = OmegaConf.load(BASE_CONFIG_PATH)
    for key, val in params.items():
        # On applique les paramètres de la recherche actuelle à notre fichier config.yaml chargé en mémoire. 
        # On ne modifie pas le fichier config.yaml sur disque mais uniquement en mémoire, uniquement pour la recherche
        # La sauvegarde se fera à la fin de toutes les recherches (en sauvegardant les meilleurs paramètres) dans un autre fichier ("config_opti.yaml")
        OmegaConf.update(cfg, key, val)   

    # On lance une course et on récupère les dicitonnaire, contenant les infos de chaque team sur toutes les courses lancées
    # race_jobs permet de spécifier le nombre de coeurs utilisés pour paralléliser les courses lancées quand on éxécute le main_loop()
    # En tout, en parallélise les recherches ET les courses lancées.
    # Note : Soyez raisonables avec les valeurs de race_jobs et de n_jobs (tout en bas, pour la recherche avec optuna) pour éviter les crasher lors des recherches.
    scores = main_loop(cfg, nb_courses = nb_courses, race_jobs=coeurs_course)

    # On récupère la liste des scores sur différentes courses de notre kart.
    # Cette liste des scores se situe dans une liste qui est elle même une valeur du dictionnaire "scores"
    donkey_positions = scores.dict["Donkey Bombs"][0]  
    # écart-type moyen inter-course. C'est l'écart-type décrivant les variations de places entre les courses
    donkey_std_between_races = np.std(donkey_positions)
    
    mean_position = np.mean(donkey_positions)   # On calcule la position moyenne de notre kart sur les NB_RACES lancées dans multi_track_race
    mean_std = np.mean(donkey_std_between_races) 

    print(f"Position moyenne : {mean_position:.1f}")
    print(f"Variance moyenne : {mean_std:.1f}")

    alpha = 1
    beta = 0.5
    return alpha * mean_position + beta * mean_std

if __name__ == "__main__":

    nb_trials = int(input("Entrez le nb de recherches à effectuer : "))
    nb_coeurs_recherche = int(input("Entrez le nb de coeurs pour la recherche (n_jobs) : "))
    nb_course_par_recherche = int(input("Entrez le nb de courses pour chaque recherche : "))
    nb_coeurs_par_course = int(input("Entres le nb de coeurs pour les courses : "))

    function = lambda trial: objective(trial, nb_courses=nb_course_par_recherche, coeurs_course=nb_coeurs_par_course)

    # On crée une étude/recherche
    study = optuna.create_study(direction="minimize")

    # Puis on lance cette recherche
    # n_trials : nombre de recherches à lancer. Chaque recherche s'accompagne de son lot de paramètres à évaluer sur le multi_track_race.
    study.optimize(function, n_trials=nb_trials, show_progress_bar=True, n_jobs=nb_coeurs_recherche)

    print(f"\nMeilleur score : {study.best_value:.3f}")
    print(f"Meilleurs paramètres : {study.best_params}")

    best_params = study.best_params  # On récupère le groupe de paramètres
    mapping = {
        # Brain
        "pilot.brain.kp": "kp",
        "pilot.brain.kd": "kd",

        # Navigation
        "pilot.navigation.lookahead_meters": "lookahead_meters",
        "pilot.navigation.lookahead_max": "lookahead_max",
        "pilot.navigation.min_dist_safety": "min_dist_safety",
        "pilot.navigation.lookahead_speed_factor": "lookahead_speed_factor",

        # Speed control
        "pilot.speed_control.cornering_accel": "cornering_accel",
        "pilot.speed_control.steering_threshold": "steering_threshold",
        "pilot.speed_control.hairpin_threshold": "hairpin_threshold",
        "pilot.speed_control.hairpin_accel": "hairpin_accel",
        "pilot.speed_control.hairpin_brake_speed": "hairpin_brake_speed",

        # Banana detection
        "banana.detection.max_distance": "max_distance",
        "banana.detection.safety_width": "safety_width",

        # Banana avoidance
        "banana.avoidance.steering_force": "steering_force",
        "banana.avoidance.acceleration": "banana_acceleration",

        # Banana edge safety
        "banana.edge_safety.max_center_dist": "max_center_dist",
        "banana.edge_safety.steering_correction": "steering_correction",
        "banana.edge_safety.correction_accel": "correction_accel",

        # Nitro
        "nitro.detection.steering_threshold_nitro": "steering_threshold_nitro",
        "nitro.detection.min_acceleration": "min_acceleration",

        # Drift
        "drift.drift_steer_angle": "drift_steer_angle",
        "drift.far_lookahead": "far_lookahead",
        "drift.near_lookahead": "near_lookahead",
        "drift.far_target_threshold": "far_target_threshold",
        "drift.steer_trigger": "steer_trigger",
        "drift.confirmation_frames": "confirmation_frames",
        "drift.min_speed": "min_speed",
        "drift.max_dist_center": "max_dist_center",
        "drift.exit_target_threshold": "exit_target_threshold",
        "drift.cooldown_frames": "cooldown_frames",
        "drift.drift_accel": "drift_accel"
    }

    
    # On écrit dans le fichier config_opti.yaml les meilleurs paramètres.
    cfg = OmegaConf.load(BASE_CONFIG_PATH)
    for key, val in mapping.items():
        OmegaConf.update(cfg, key, best_params[val])

    # On enregistre dans le fichier config_opti.yaml les meilleurs paramètres.
    OmegaConf.save(cfg, OUTPUT_CONFIG_PATH)

    # On demande à l'utilisateur s'il veut enregistrer les paramètres obtenus dans le fichier config.yaml
    reponse = input("Voulez vous enregistrer ces paramètres dans le fichier config.yaml ? [o/n]: ")
    if reponse == 'o':
        OmegaConf.save(cfg, BASE_CONFIG_PATH)
        print(f"{BASE_CONFIG_PATH.name} mis à jour avec les meilleurs paramètres.")

    print(f"{OUTPUT_CONFIG_PATH.name} mis à jour avec les meilleurs paramètres.")        

        
