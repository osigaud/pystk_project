from pathlib import Path
import fcntl
import atexit

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

    
