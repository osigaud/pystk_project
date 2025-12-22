import time
from datetime import datetime

# Get the current timestamp
current_timestamp = datetime.now()

# Format it into a human-readable string
formatted_timestamp = current_timestamp.strftime("%Y-%m-%d %H:%M:%S")

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
                else:
                    avg_position, std_position = 1, 0
                fp.write(
                    f"""<td>{avg_position:.2f}</td>"""
                    f"""<td>{std_position:.2f}</td>"""
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

