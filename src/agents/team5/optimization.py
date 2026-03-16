import optuna
import numpy as np
import os
import warnings
from omegaconf import OmegaConf
from pathlib import Path
from multi_track_race_display_team5 import main_loop

#Pour éviter les conflits avec python
os.environ["PYTHONWARNINGS"] = "ignore"
warnings.filterwarnings("ignore")


BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR / "config_opti.yaml"


def objective(trial):
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


    cfg = OmegaConf.load(CONFIG_PATH)
    for key, val in params.items():
        OmegaConf.update(cfg, key, val)
    OmegaConf.save(cfg, CONFIG_PATH)

    scores = main_loop()

    donkey_positions = scores.dict["Donkey Bombs"][0]
    mean_position = np.mean(donkey_positions)
    print(f"Position moyenne : {mean_position:.1f}")
    return mean_position

if __name__ == "__main__":
    study = optuna.create_study(direction="minimize")
    study.optimize(objective, n_trials=3, show_progress_bar=True)

    print(f"\nMeilleur score : {study.best_value:.3f}")
    print(f"Meilleurs paramètres : {study.best_params}")

    best_params = study.best_params
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

    
    cfg = OmegaConf.load(CONFIG_PATH)
    for key, val in mapping.items():
        OmegaConf.update(cfg, key, best_params[val])
    OmegaConf.save(cfg, CONFIG_PATH)
    print("config.yaml mis à jour avec les meilleurs paramètres.")
        

        
