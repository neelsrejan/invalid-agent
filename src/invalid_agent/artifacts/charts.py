"""Plotly figures for the dashboard. The deck renders its own PNGs with matplotlib."""

from __future__ import annotations

from typing import Any

import plotly.graph_objects as go

_NAVY = "#0B3A5B"
_TEAL = "#1F7A8C"
_RED = "#B23A48"
_GRID = "#E3E8EC"


def p_chart_figure(chart: dict[str, Any], title: str = "Weekly invalid rate") -> go.Figure:
    periods = [point["period"] for point in chart["points"]]
    rate = [point["p"] * 100 for point in chart["points"]]
    ucl = [point["ucl"] * 100 for point in chart["points"]]
    lcl = [point["lcl"] * 100 for point in chart["points"]]
    center = [chart["p_bar"] * 100 for _ in periods]
    rule1 = {hit["period"] for hit in chart["violations"] if hit["rule"] == 1}
    figure = go.Figure()
    figure.add_trace(go.Scatter(x=periods, y=ucl, name="UCL", line={"color": _RED, "dash": "dot", "width": 1}))
    figure.add_trace(go.Scatter(x=periods, y=lcl, name="LCL", line={"color": _RED, "dash": "dot", "width": 1}))
    figure.add_trace(go.Scatter(x=periods, y=center, name="p-bar", line={"color": "#8AA0B2", "dash": "dash", "width": 1}))
    figure.add_trace(go.Scatter(x=periods, y=rate, name="Invalid %", mode="lines+markers", line={"color": _NAVY, "width": 2}))
    flagged_x = [point["period"] for point in chart["points"] if point["period"] in rule1]
    flagged_y = [point["p"] * 100 for point in chart["points"] if point["period"] in rule1]
    if flagged_x:
        figure.add_trace(
            go.Scatter(x=flagged_x, y=flagged_y, name="Rule 1", mode="markers", marker={"color": _RED, "size": 9, "symbol": "x"})
        )
    figure.update_layout(title=title, yaxis_title="Invalid rate (%)", template="plotly_white", height=380, margin={"l": 40, "r": 20, "t": 50, "b": 40})
    figure.update_xaxes(showgrid=True, gridcolor=_GRID)
    figure.update_yaxes(showgrid=True, gridcolor=_GRID)
    return figure


def pareto_figure(rows: list[dict[str, Any]]) -> go.Figure:
    codes = [row["code"] for row in rows]
    counts = [row["count"] for row in rows]
    cumulative = [row["cumulative_share"] * 100 for row in rows]
    figure = go.Figure()
    figure.add_trace(go.Bar(x=codes, y=counts, name="Count", marker_color=_TEAL))
    figure.add_trace(go.Scatter(x=codes, y=cumulative, name="Cumulative %", yaxis="y2", mode="lines+markers", line={"color": _NAVY}))
    figure.update_layout(
        title="Pareto of invalid codes",
        yaxis={"title": "Invalids"},
        yaxis2={"title": "Cumulative %", "overlaying": "y", "side": "right", "range": [0, 105]},
        template="plotly_white",
        height=380,
        margin={"l": 40, "r": 40, "t": 50, "b": 40},
        legend={"orientation": "h"},
    )
    return figure


def before_after_figure(before_chart: dict[str, Any], after_chart: dict[str, Any]) -> go.Figure:
    figure = go.Figure()
    figure.add_trace(
        go.Scatter(
            x=[point["period"] for point in before_chart["points"]],
            y=[point["p"] * 100 for point in before_chart["points"]],
            name="Observed",
            mode="lines",
            line={"color": _RED, "width": 2},
        )
    )
    figure.add_trace(
        go.Scatter(
            x=[point["period"] for point in after_chart["points"]],
            y=[point["p"] * 100 for point in after_chart["points"]],
            name="Projected without leading stratum",
            mode="lines",
            line={"color": _TEAL, "width": 2},
        )
    )
    figure.update_layout(
        title="Before / after — projection, not observed follow-up",
        yaxis_title="Invalid rate (%)",
        template="plotly_white",
        height=380,
        margin={"l": 40, "r": 20, "t": 50, "b": 40},
        legend={"orientation": "h"},
    )
    return figure
