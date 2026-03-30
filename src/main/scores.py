import sys, os
import numpy as np
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass

# Get the current timestamp
current_timestamp = datetime.now()

# Format it into a human-readable string
formatted_timestamp = current_timestamp.strftime("%Y-%m-%d %H:%M:%S")

@dataclass
class Scores:
    def __init__(self):
        self.dict = {}
    
    def init(self, name):
        self.dict[name] = [[], [], [], [], []]

    def append(self, name, pos, pos_std, steps, wins, blocked):
        self.dict[name][0].append(pos)
        self.dict[name][1].append(pos_std)
        self.dict[name][2].append(steps)
        self.dict[name][3].append(wins)
        self.dict[name][4].append(blocked)

    def display(self):
        print(self.dict)

    def display_mean(self):
        for k in self.dict:
            print(f"{k}: {np.array(self.dict[k][0]).mean()}, {np.array(self.dict[k][1]).mean()}, {np.array(self.dict[k][2]).mean()}, {np.array(self.dict[k][2]).std()}, {np.array(self.dict[k][3]).sum()}, {np.array(self.dict[k][4]).sum()}")

    def display_html(self, fp):
        for k in self.dict:
            fp.write(f"""<tr><td>{k}</td>""")
            fp.write(
                    f"""<td>{np.array(self.dict[k][0]).mean():.2f}</td>"""
                    f"""<td>{np.array(self.dict[k][1]).mean():.2f}</td>"""
                    f"""<td>{np.array(self.dict[k][2]).mean():.2f}</td>"""
                    f"""<td>{np.array(self.dict[k][2]).std():.2f}</td>"""
                    f"""<td>{np.array(self.dict[k][3]).sum()}</td>"""
                    f"""<td>{np.array(self.dict[k][4]).sum()}</td>"""
                    "</tr>"
                )
            

def output_html(output: Path, scores: Scores):
    # Use https://github.com/tofsjonas/sortable?tab=readme-ov-file#1-link-to-jsdelivr
    with output.open("wt") as fp:
        fp.write(
            f"""<html><head>
<title>STK Race results</title>
<link href="https://cdn.jsdelivr.net/gh/tofsjonas/sortable@latest/dist/sortable.min.css" rel="stylesheet" />
<script src="https://cdn.jsdelivr.net/gh/tofsjonas/sortable@latest/dist/sortable.min.js"></script>
<body>
<h1>Team evaluation on SuperTuxKart</h1><div style="margin: 10px; font-weight: bold">Timestamp: {formatted_timestamp}</div>
<table class="sortable n-last asc">
  <thead>
    <tr>
      <th class="no-sort">Name</th>
      <th id="position">Avg. position</th>
      <th class="no-sort">±</th>
      <th id="position">Avg. steps</th>
      <th class="no-sort">±</th>
      <th id="position">Nb wins</th>
      <th id="position">Nb blocked</th>
    </tr>
  </thead>
  <tbody>"""
        )

        scores.display_html(fp)
            
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
        fp.write("""</body>""")
