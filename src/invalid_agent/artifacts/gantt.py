"""4-week investigation Gantt.

HTML comes from plotly. The PNG is drawn with matplotlib so a machine
without kaleido (the usual case on a laptop and in CI) still gets a file
that can sit in the executive deck later.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px

_OWNERS = {
    "PM": "#0B3A5B",
    "QA": "#1F7A8C",
    "R&D": "#3D5A40",
    "Manufacturing": "#8C5A2A",
    "Regulatory": "#5C4B51",
    "Customer Support": "#6B3A4A",
}


def _frame(plan: dict) -> pd.DataFrame:
    rows = []
    for task in plan["tasks"]:
        rows.append(
            {
                "task": f"{task['id']}  {task['name']}",
                "owner": task["owner"],
                "start": task["start"],
                "end": task["end"],
            }
        )
    frame = pd.DataFrame(rows)
    frame["start"] = pd.to_datetime(frame["start"])
    frame["end"] = pd.to_datetime(frame["end"])
    return frame


def write_gantt(plan: dict, html_path: Path, png_path: Path) -> None:
    html_path.parent.mkdir(parents=True, exist_ok=True)
    frame = _frame(plan)
    title = "Investigation plan — simulation, not for clinical use"
    figure = px.timeline(
        frame,
        x_start="start",
        x_end="end",
        y="task",
        color="owner",
        color_discrete_map=_OWNERS,
        title=title,
    )
    figure.update_yaxes(autorange="reversed")
    figure.update_layout(margin={"l": 20, "r": 20, "t": 60, "b": 20}, height=max(360, 36 * len(frame)))
    figure.write_html(str(html_path), include_plotlyjs="cdn")
    _write_png(frame, png_path, title)


def _write_png(frame: pd.DataFrame, path: Path, title: str) -> None:
    fig, ax = plt.subplots(figsize=(11, max(3.5, 0.42 * len(frame))))
    for index, row in frame.iloc[::-1].reset_index(drop=True).iterrows():
        start = mdates.date2num(row["start"])
        end = mdates.date2num(row["end"])
        width = max(end - start, 0.4)
        ax.barh(index, width, left=start, height=0.6, color=_OWNERS.get(row["owner"], "#0B3A5B"))
    labels = list(frame["task"].iloc[::-1])
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels, fontsize=8)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
    ax.set_title(title, loc="left", fontsize=11)
    ax.grid(axis="x", linestyle=":", color="#C5CED6")
    fig.tight_layout()
    fig.savefig(path, dpi=120)
    plt.close(fig)
