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
import fcntl
import time
import atexit

# Get the current timestamp
current_timestamp = datetime.now()

# Format it into a human-readable string
formatted_timestamp = current_timestamp.strftime("%Y-%m-%d %H:%M:%S")

# Maximum number of karts on a circuit
MAX_KARTS = 10


def acquire_lock(lock_file: Path):
    """
    Acquire an exclusive lock to prevent concurrent executions.

    Args:
        lock_file: Path to the lock file

    This function will wait if another instance is already running.
    The lock is automatically released when the process exits.
    """
    lock_file.parent.mkdir(parents=True, exist_ok=True)
    lock_fd = open(lock_file, "w")

    logging.info("Attempting to acquire lock on %s", lock_file.parent)

    try:
        # Try to acquire lock without blocking
        fcntl.flock(lock_fd.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        logging.info("Lock acquired")
    except IOError:
        # Another instance is running, wait for lock
        logging.warning("Another instance is running, waiting for lock...")
        start_wait = time.time()
        fcntl.flock(lock_fd.fileno(), fcntl.LOCK_EX)
        logging.info(
            "Lock acquired after waiting %.1f seconds", time.time() - start_wait
        )

    # Register cleanup to release lock on exit
    def release_lock():
        try:
            fcntl.flock(lock_fd.fileno(), fcntl.LOCK_UN)
            lock_fd.close()
            logging.info("Lock released")
        except Exception:
            pass

    atexit.register(release_lock)


@dataclass
class KartError:
    when: str
    message: str
    traceback: str


@dataclass
class TeamResult:
    rewards: List[float] = field(default_factory=list)
    positions: List[float] = field(default_factory=list)
    action_times: List[float] = field(default_factory=list)


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

def display_statistics(projects: dict[str, Project], target_runs: int):
    """
    Display current race statistics for all teams.

    Args:
        projects: Dictionary of team_id to Project
        target_runs: Target number of runs per team
    """
    # Separate teams into those with runs and those with errors
    teams_with_runs = []
    teams_with_errors = []

    for project in projects.values():
        if project.error:
            teams_with_errors.append(project)
        elif project.runs > 0:
            teams_with_runs.append(project)

    # Sort teams with runs by mean position (ascending - lower position is better)
    sorted_teams = sorted(teams_with_runs, key=lambda t: np.mean(t.results.positions))

    logging.info("=" * 80)
    logging.info("Current Statistics:")
    logging.info("-" * 80)

    # Display teams with runs
    for team in sorted_teams:
        avg_position = np.mean(team.results.positions)
        logging.info(
            "  %s: %d/%d races | Avg Position: %.2f",
            team.team_id[:30].ljust(30),
            team.runs,
            target_runs,
            avg_position,
        )

    # Display teams with errors at the end
    for team in teams_with_errors:
        logging.info(
            "  %s: error detected",
            team.team_id[:30].ljust(30),
        )
    logging.info("=" * 80)


def output_html(output: Path, projects: Iterable[Project]):
    # Use https://github.com/tofsjonas/sortable?tab=readme-ov-file#1-link-to-jsdelivr
    with output.open("wt") as fp:
        fp.write(
            f"""<html><head>
<title>RLD: STK Race results</title>
<link href="https://cdn.jsdelivr.net/gh/tofsjonas/sortable@latest/dist/sortable.min.css" rel="stylesheet" />
<script src="https://cdn.jsdelivr.net/gh/tofsjonas/sortable@latest/dist/sortable.min.js"></script>
<body>
<h1>Team evaluation on SuperTuxKart</h1><div style="margin: 10px; font-weight: bold">Timestamp: {formatted_timestamp}</div>
<table class="sortable n-last asc">
  <thead>
    <tr>
      <th class="no-sort">Name</th>
      <th class="no-sort">commit</th>
      <th class="no-sort"># races</th>
      <th id="position">Avg. position</th>
      <th class="no-sort">±</th>
      <th>Avg. action time</th>
      <th class="no-sort">±</th>
    </tr>
  </thead>
  <tbody>"""
        )

        for team in projects:
            fp.write(f"""<tr><td>{team.team_id}</td><td>{team.current_ref[:8]}</td>""")
            if not team.error:
                n_runs = len(team.results.rewards)
                if n_runs > 0:
                    avg_position, std_position = np.mean(
                        team.results.positions
                    ), np.std(team.results.positions)
                    avg_action_time, std_action_time = np.mean(
                        team.results.action_times
                    ), np.std(team.results.action_times)
                else:
                    avg_position, std_position = 1, 0
                    avg_action_time, std_action_time = 0, 0
                fp.write(
                    f"""<td>{avg_position:.2f}</td>"""
                    f"""<td>{std_position:.2f}</td>"""
                    f"""<td>{avg_action_time:.4f}</td>"""
                    f"""<td>{std_action_time:.4f}</td>"""
                    "</tr>"
                )
            else:
                fp.write(
                    f"""<td style="color: red"><a href="#error_{team.team_id}">error</a></td>"""
                    "<td></td><td></td><td></td><td></td><td></td><td></td></tr>"
                )

        fp.write(
            """<script>
  window.addEventListener('load', function () {
    const el = document.getElementById('position')
    if (el) {
      el.click()
    }
  })
</script>
"""
        )
        fp.write("""</tbody></table><h1>Error details</h1>""")
        for team in projects:
            if team.error:
                fp.write(
                    f"""<a id="error_{team.team_id}"></a><h2>{team.team_id}</h2>"""
                )
                fp.write(
                    f"<div>{team.error.when}</div><div><code>{team.error.message}</code></div>"
                )
                for s in team.error.traceback:
                    fp.write(f"<div><code>{s}</code></div>")
        fp.write("""</body>""")


def run_docker_race(
    run_id: int,
    selected: List[Project],
    repositories: Path,
    output_suffix: str = "",
    mock_project: Optional[Path] = None,
    temp_dir_base: Optional[Path] = None,
) -> tuple[int, Optional[dict], List[Project]]:
    """
    Run a single docker race process in an isolated temporary directory.

    Args:
        run_id: Identifier for this run
        selected: List of selected projects for this race
        repositories: Path to main repositories directory (used to copy stk_actor)
        output_suffix: Suffix for output file to avoid conflicts in parallel mode
        mock_project: Optional mock project path to use instead of individual repos
        temp_dir_base: Optional base directory for temporary files (default: system temp)

    Returns:
        Tuple of (run_id, data, selected) where data is the race results or None on error
    """
    output_file = f"results{output_suffix}.json"

    # Create temporary directory for this race
    with tempfile.TemporaryDirectory(dir=temp_dir_base) as temp_dir:
        temp_path = Path(temp_dir)
        logging.info("[Race %d] Running in %s", run_id, temp_path)
        # Copy project directories (excluding .git) for each selected project and build actor paths
        actor_paths = []
        for project in selected:
            if mock_project:
                src = mock_project
            else:
                src = repositories / project.path

            # Always use normalized team_id as directory name to avoid path issues
            # Normalize team_id: replace non-alphanumeric chars with underscores
            normalized_id = re.sub(r"[^A-Za-z0-9_-]", "_", project.team_id)
            dst = temp_path / normalized_id

            if src.exists() and (src / "stk_actor").exists():
                logging.debug(
                    "[Race %d] Copying %s to temp directory", run_id, project.team_id
                )
                dst.mkdir(parents=True, exist_ok=True)
                # Copy entire project directory but exclude .git
                shutil.copytree(
                    src,
                    dst,
                    dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns(".git"),
                )
            else:
                logging.warning(
                    "[Race %d] Warning: stk_actor not found for %s",
                    run_id,
                    project.team_id,
                )

            # Add to actor paths for docker command
            actor_paths.append(f"/workspace/{normalized_id}@:{project.team_id}")

        command = [
            "docker",
            "run",
            "--rm",
            "--platform",
            "linux/amd64",
            "-v",
            f"{temp_path}:/workspace",
            "osigaud/stk-race",
            "master-mind",
            "rl",
            "stk-race",
            "--no-check",
            "--hide",
            "--max-paths",
            "20",
            "--interaction",
            "none",
            "--action-timeout",
            "2",
            "--error-handling",
            "--num-karts",
            str(len(selected)),
            "--output",
            f"/workspace/{output_file}",
            *actor_paths,
        ]

        logging.info("[Race %d] Running command: %s", run_id, " ".join(command))

        # Create logs and results directories if they don't exist
        logs_dir = repositories / "logs"
        logs_dir.mkdir(exist_ok=True)
        results_dir = repositories / "results"
        results_dir.mkdir(exist_ok=True)

        log_file = logs_dir / f"docker-{run_id:03d}.log"

        try:
            with open(log_file, "w") as log_fp:
                subprocess.check_call(command, stdout=log_fp, stderr=subprocess.STDOUT)

            with open(temp_path / output_file, "rt") as fp:
                data = json.load(fp)

            # Copy results file to results directory
            results_log_file = results_dir / f"results-{run_id:03d}.json"
            shutil.copy2(temp_path / output_file, results_log_file)

            return (run_id, data, selected)
        except Exception as e:
            logging.error(
                "[Race %d] Error running docker: %s (see %s)", run_id, e, log_file
            )
            return (run_id, None, selected)


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
