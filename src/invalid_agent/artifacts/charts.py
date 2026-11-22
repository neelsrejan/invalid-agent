"""Plotly figures for the dashboard. The deck renders its own PNGs with matplotlib."""

from __future__ import annotations

from typing import Any

import plotly.graph_objects as go

_NAVY = "#0B3A5B"
_TEAL = "#1F7A8C"
_RED = "#B23A48"
_GRID = "#E3E8EC"


def p_chart_figure(
    chart: dict[str, Any],
    title: str = "Weekly invalid rate",
    y_title: str = "Invalid rate (%)",
    series_name: str = "Invalid %",
) -> go.Figure:
    periods = [point["period"] for point in chart["points"]]
    rate = [point["p"] * 100 for point in chart["points"]]
    ucl = [point["ucl"] * 100 for point in chart["points"]]
    lcl = [point["lcl"] * 100 for point in chart["points"]]
    center = [chart["p_bar"] * 100 for _ in periods]
    rule1 = {hit["period"] for hit in chart["violations"] if hit["rule"] == 1}
    figure = go.Figure()
    figure.add_trace(go.Scatter(x=periods, y=ucl, name="High line", line={"color": _RED, "dash": "dot", "width": 1}))
    figure.add_trace(go.Scatter(x=periods, y=lcl, name="Low line", line={"color": _RED, "dash": "dot", "width": 1}))
    figure.add_trace(go.Scatter(x=periods, y=center, name="Average", line={"color": "#8AA0B2", "dash": "dash", "width": 1}))
    figure.add_trace(
        go.Scatter(
            x=periods,
            y=rate,
            name=series_name,
            mode="lines+markers",
            line={"color": _NAVY, "width": 2},
            hovertemplate="%{x}<br>" + series_name + ": %{y:.2f}<extra></extra>",
        )
    )
    flagged_x = [point["period"] for point in chart["points"] if point["period"] in rule1]
    flagged_y = [point["p"] * 100 for point in chart["points"] if point["period"] in rule1]
    if flagged_x:
        figure.add_trace(
            go.Scatter(
                x=flagged_x,
                y=flagged_y,
                name="Far above usual",
                mode="markers",
                marker={"color": _RED, "size": 9, "symbol": "x"},
            )
        )
    figure.update_layout(title=title, yaxis_title=y_title, template="plotly_white", height=380, margin={"l": 40, "r": 20, "t": 50, "b": 40})
    figure.update_xaxes(showgrid=True, gridcolor=_GRID)
    figure.update_yaxes(showgrid=True, gridcolor=_GRID)
    return figure


def pareto_figure(rows: list[dict[str, Any]], count_title: str = "Invalids") -> go.Figure:
    labels = [str(row.get("plain") or row["code"]) for row in rows]
    counts = [row["count"] for row in rows]
    cumulative = [row["cumulative_share"] * 100 for row in rows]
    figure = go.Figure()
    figure.add_trace(
        go.Bar(
            x=labels,
            y=counts,
            name="Count",
            marker_color=_TEAL,
            hovertemplate="%{x}<br>Count: %{y}<extra></extra>",
        )
    )
    figure.add_trace(
        go.Scatter(
            x=labels,
            y=cumulative,
            name="Running total %",
            yaxis="y2",
            mode="lines+markers",
            line={"color": _NAVY},
            hovertemplate="%{x}<br>Running total: %{y:.1f}%<extra></extra>",
        )
    )
    figure.update_layout(
        title="Which invalid types show up most",
        yaxis={"title": count_title},
        yaxis2={"title": "Running total %", "overlaying": "y", "side": "right", "range": [0, 105]},
        template="plotly_white",
        height=460,
        margin={"l": 70, "r": 50, "t": 50, "b": 140},
        legend={"orientation": "h", "y": -0.35},
    )
    figure.update_xaxes(automargin=True, tickangle=-35)
    figure.update_yaxes(automargin=True)
    return figure


def before_after_figure(
    before_chart: dict[str, Any],
    after_chart: dict[str, Any],
    y_title: str = "Invalid rate (%)",
) -> go.Figure:
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
            name="What-if, leading group cleared",
            mode="lines",
            line={"color": _TEAL, "width": 2},
        )
    )
    figure.update_layout(
        title="What-if on this same file, not a new test",
        yaxis_title=y_title,
        template="plotly_white",
        height=380,
        margin={"l": 40, "r": 20, "t": 50, "b": 40},
        legend={"orientation": "h"},
    )
    return figure


def company_share_figure(companies: list[dict[str, Any]]) -> go.Figure:
    """Share by company. Grey is too few reports. A red X is over 1%."""
    names = [str(row["name"]) for row in companies]
    shares = [float(row["share"]) * 100 for row in companies]
    colors = []
    symbols = []
    for row in companies:
        if not row.get("enough"):
            colors.append("#8AA0B2")
            symbols.append("circle")
        elif row.get("over"):
            colors.append(_RED)
            symbols.append("x")
        else:
            colors.append(_NAVY)
            symbols.append("circle")
    figure = go.Figure(
        go.Scatter(
            x=names,
            y=shares,
            mode="markers",
            marker={"color": colors, "symbol": symbols, "size": 14},
            name="Invalid share",
            hovertemplate="%{x}<br>%{y:.2f}%<extra></extra>",
        )
    )
    figure.add_hline(y=1, line_color=_RED, line_dash="dot", annotation_text="1%")
    figure.update_layout(
        title="Invalid share of field problem reports",
        yaxis_title="Invalid share (%)",
        template="plotly_white",
        height=380,
        margin={"l": 40, "r": 20, "t": 50, "b": 80},
        showlegend=False,
    )
    return figure


def fishbone_figure(branch: str) -> go.Figure:
    """Six cause groups. The likely branch is the red mark."""
    names = ["Man", "Machine", "Method", "Material", "Measurement", "Environment"]
    marked = str(branch or "")
    figure = go.Figure(
        go.Scatter(
            x=list(range(len(names))),
            y=[1 if index % 2 == 0 else 0 for index in range(len(names))],
            mode="markers+text",
            text=names,
            textposition="top center",
            marker={
                "size": 16,
                "color": [_RED if name == marked else _NAVY for name in names],
                "symbol": ["x" if name == marked else "circle" for name in names],
            },
        )
    )
    figure.add_shape(type="line", x0=-0.4, x1=5.4, y0=0.5, y1=0.5, line={"color": _NAVY, "width": 2})
    figure.update_layout(
        title=f"Cause diagram. Likely branch: {marked}",
        template="plotly_white",
        height=280,
        margin={"l": 20, "r": 20, "t": 50, "b": 20},
        xaxis={"visible": False},
        yaxis={"visible": False},
        showlegend=False,
    )
    return figure
