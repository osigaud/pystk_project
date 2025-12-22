# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "numpy",
# ]
# ///
from dataclasses import asdict, dataclass, field, fields
from functools import cached_property
import logging
import argparse
import json
from pathlib import Path
from csv import DictReader
import re
import subprocess
import sys
from typing import Iterable, List, Optional
from urllib.parse import urlparse
import numpy as np
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import tempfile
import shutil
import queue

from race_utils.docker import run_docker_race, acquire_lock
from race_utils.output import display_statistics, output_html

# Maximum number of karts on a circuit
MAX_KARTS = 10

@dataclass
class KartError:
    when: str
    message: str
    traceback: str


@dataclass
class TeamResult:
    positions: List[float] = field(default_factory=list)

@dataclass
class Project:
    team_id: str
    error: Optional[KartError] = field(default=None)

    #: number of completed runs
    runs: int = field(default=0)

    #: number of times selected for a race (including in-progress races)
    selection_count: int = field(default=0)

    #: results
    results: TeamResult = field(default_factory=TeamResult)

if __name__ == "__main__":  # noqa: C901
    base_path = Path(__file__).parent

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--runs",
        default=10,
        type=int,
        help="Number of runs per team",
    )
    parser.add_argument(
        "--regenerate",
        action="store_true",
        default=False,
        help="Just regenerate the HTML file",
    )
    parser.add_argument(
        "--debug", action="store_true", default=False, help="Log debug statements"
    )
    parser.add_argument(
        "--force", action="store_true", default=False, help="Force runnning"
    )
    parser.add_argument(
        "--no-fetch", action="store_true", default=False, help="Do not fetch"
    )
    parser.add_argument(
        "--ignore-fetch-errors", action="store_true", default=False, help="Ignore fetch errors"
    )
    parser.add_argument(
        "--results",
        default=base_path / "results.json",
        type=Path,
        help="File containing the current results",
    )
    parser.add_argument(
        "--html",
        default=base_path / "results.html",
        type=Path,
        help="HTML file for the results",
    )
    parser.add_argument(
        "--parallel",
        default=1,
        type=int,
        help="Number of parallel docker processes",
    )
    parser.add_argument(
        "--mock-project",
        type=Path,
        help="Use this project path for all teams instead of cloning repos (for testing)",
    )
    parser.add_argument(
        "--temp-dir",
        type=Path,
        help="Directory to use for temporary race files (default: system temp directory)",
    )
    args = parser.parse_args()
    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    # Acquire lock to prevent concurrent executions
    lock_file = args.repositories / ".compare.lock"
    acquire_lock(lock_file)

    # --- Reading projects and checkout
    logging.info("Reading projects")
    projects: dict[str, Project] = {}
    errors = False
    git_paths = []

    if args.mock_project:
        logging.info("Using mock project: %s", args.mock_project)
        if not args.mock_project.is_dir():
            logging.error("Mock project path does not exist: %s", args.mock_project)
            sys.exit(1)
        if not (args.mock_project / "stk_actor").is_dir():
            logging.error(
                "Mock project does not have stk_actor folder: %s", args.mock_project
            )
            sys.exit(1)

            # to be integrated
            project = Project(team_id=team_id, repo_url=repo_url)
            projects[project.team_id] = project

            project.error = KartError(
                "Checking out the project", "No stk_actor subfolder", []
            )

                except subprocess.CalledProcessError as e:
                    logging.error(
                        f"Exception when refreshing/cloning repository: {e.stderr}"
                    )
                    error = e.stderr if e.stderr else str(e)
                    if "branch evaluate not found" in error or "evaluation" in error:
                        error = "No 'evaluation' branch in repository"
                    elif "Could not read from remote repository" in error:
                        error = "No access to repository"

                    project.error = KartError("Checking out the project", error, [])
                    errors = True
                except subprocess.TimeoutExpired:
                    logging.error("Timeout when refreshing/cloning repository")
                    project.error = KartError(
                        "Checking out the project", "Git operation timed out", []
                    )
                    errors = True

    # --- Loading state
    if args.results.is_file():
        try:
            changed = False
            with args.results.open("rt") as fp:
                results = json.load(fp)
                for team_id, project in projects.items():
                    team_results = results.get(team_id, {})

                    # Load past results
                    if r := team_results.get("results", None):
                        logging.info("Got results for team %s", team_id)
                        project.results = TeamResult(**r)

                    # If new commit and no error while pulling...
                    if not project.error:
                        if team_results.get("ref", None) != project.current_ref:
                            # OK, start afresh
                            logging.info("New commit for team %s", team_id)
                            changed = True
                            project.error = None
                        else:
                            # If we had an error before, just stick to it
                            if error := team_results.get("error", None):
                                logging.info("Got error for team %s", team_id)
                                project.error = KartError(**error)

                                logging.info(
                                    "Team %s did not changed and an error: not evaluating",
                                    team_id,
                                )
            if args.regenerate:
                if not errors:
                    output_html(args.html, list(projects.values()))
                    sys.exit(0)

            if (not changed) and (not args.force):
                logging.info("No change in projects: do not run the evaluation")
                output_html(args.html, list(projects.values()))
                sys.exit(0)

        except Exception:
            logging.exception("Could not load last results file, re-evaluating...")
            changed = True

    if args.regenerate:
        logging.error("No results file to generate results from")
        sys.exit(1)

    # --- Runs n experiments

    # Cleanup logs and results directories
    logs_dir = args.repositories / "logs"
    results_dir = args.repositories / "results"

    if logs_dir.exists():
        logging.info("Cleaning up logs directory")
        shutil.rmtree(logs_dir)
    logs_dir.mkdir(exist_ok=True)

    if results_dir.exists():
        logging.info("Cleaning up results directory")
        shutil.rmtree(results_dir)
    results_dir.mkdir(exist_ok=True)

    # Cleanup results
    for project in projects.values():
        project.results = TeamResult()

    run_ix = 1
    valid = {
        project.team_id: project
        for project in projects.values()
        if project.error is None
    }

    # Lock for thread-safe operations
    results_lock = threading.Lock()

    def generate_race(race_counter: List[int]) -> Optional[tuple[int, List[Project]]]:
        """Generate a new race with remaining candidates. Returns (race_id, selected) or None if done."""
        candidates: list[Project] = [
            project for project in valid.values() if project.runs < args.runs
        ]

        if len(candidates) == 0:
            return None

        # Try to fill in other karts
        if len(candidates) < MAX_KARTS:
            selected = candidates.copy()
            remaining = [
                project for project in valid.values() if project.runs >= args.runs
            ]

            if len(remaining) > 0:
                selected += list(
                    np.random.choice(
                        remaining,
                        min(MAX_KARTS - len(selected), len(remaining)),
                        replace=False,
                    )
                )
        else:
            # Sample with probability inversely proportional to selection count
            # Teams with fewer selections have higher probability of being selected
            selection_counts = np.array([p.selection_count for p in candidates])
            # Use inverse of (selection_count + 1) to avoid division by zero and give preference to less-selected teams
            weights = 1.0 / (selection_counts + 1)
            probabilities = weights / weights.sum()

            selected: List[Project] = list(
                np.random.choice(
                    candidates,
                    min(MAX_KARTS, len(candidates)),
                    replace=False,
                    p=probabilities,
                )
            )
            np.random.shuffle(selected)

        # Increment selection count for all selected projects
        for project in selected:
            project.selection_count += 1

        race_id = race_counter[0]
        race_counter[0] += 1
        return (race_id, selected)

    # Initialize executor and futures tracking
    with ThreadPoolExecutor(max_workers=args.parallel) as executor:
        futures = {}
        race_counter = [run_ix]

        # Submit initial batch of races
        for _ in range(args.parallel):
            race = generate_race(race_counter)
            if race:
                race_id, selected = race
                future = executor.submit(
                    run_docker_race,
                    race_id,
                    selected,
                    args.repositories,
                    f"_{race_id}" if args.parallel > 1 else "",
                    args.mock_project,
                    args.temp_dir,
                )
                futures[future] = (race_id, selected)

        # Process completed races and submit new ones
        while futures:
            for future in as_completed(futures):
                race_id, data, selected = future.result()
                del futures[future]

                with results_lock:
                    if data is None:
                        logging.error("Race %d failed with no data", race_id)
                        # Decrement selection count for failed race
                        for project in selected:
                            project.selection_count -= 1
                    elif data.get("type", "") == "results":
                        if len(data["results"]) == len(selected):
                            for results, team in zip(data["results"], selected):
                                team.results.positions.append(results["position"])
                                team.results.action_times.append(
                                    results.get("avg_action_time", 0)
                                )
                                team.runs += 1
                            logging.info("Race %d completed successfully", race_id)

                            # Display statistics for all teams after race completion
                            display_statistics(valid, args.runs)
                        else:
                            logging.error(
                                "Race %d: Got %d results vs %d selected",
                                race_id,
                                len(data["results"]),
                                len(selected),
                            )
                            logging.error(
                                "  Teams in race: %s",
                                ", ".join([p.team_id for p in selected]),
                            )
                            # Decrement selection count for failed race
                            for project in selected:
                                project.selection_count -= 1
                    else:
                        # Error in one of the karts - remove from future races
                        selected[data["key"]].error = KartError(
                            **{
                                field.name: data[field.name]
                                for field in fields(KartError)
                            }
                        )
                        error_team = selected[data["key"]].team_id
                        logging.error(
                            "Race %d: Got an error for player %s, removing from future races",
                            race_id,
                            error_team,
                        )
                        logging.error(
                            "  Teams in race: %s",
                            ", ".join([p.team_id for p in selected]),
                        )
                        if error_team in valid:
                            del valid[error_team]
                        # Decrement selection count for failed race
                        for project in selected:
                            project.selection_count -= 1

                    # Try to generate and submit a new race
                    if len(valid) > 1:  # Need at least 2 valid teams to continue
                        race = generate_race(race_counter)
                        if race:
                            race_id, selected = race
                            future = executor.submit(
                                run_docker_race,
                                race_id,
                                selected,
                                args.repositories,
                                f"_{race_id}" if args.parallel > 1 else "",
                                args.mock_project,
                                args.temp_dir,
                            )
                            futures[future] = (race_id, selected)

        run_ix = race_counter[0]

    # --- Write new results
    with args.results.open("wt") as fp:
        data = {
            team_id: {
                "ref": project.current_ref,
                "error": asdict(project.error) if project.error else None,
                "results": asdict(project.results),
            }
            for team_id, project in projects.items()
        }
        json.dump(data, fp)

    # --- Output HTML
    output_html(args.html, list(projects.values()))
