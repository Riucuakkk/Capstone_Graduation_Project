from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


COLORWAY = ["#0F766E", "#2563EB", "#E11D48", "#F59E0B", "#7C3AED", "#16A34A"]


def apply_chart_theme(fig: go.Figure, height: int = 360) -> go.Figure:
    fig.update_layout(
        height=height,
        margin=dict(l=8, r=8, t=48, b=8),
        colorway=COLORWAY,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#1F2937", family="Inter, Segoe UI, sans-serif"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(gridcolor="rgba(148, 163, 184, 0.22)", zeroline=False)
    return fig


def line_chart(df: pd.DataFrame, x: str, y: str, title: str, color: str | None = None) -> go.Figure:
    fig = px.line(df, x=x, y=y, color=color, markers=True, title=title)
    return apply_chart_theme(fig)


def bar_chart(df: pd.DataFrame, x: str, y: str, title: str, color: str | None = None) -> go.Figure:
    fig = px.bar(df, x=x, y=y, color=color, title=title, text_auto=".2s")
    fig.update_traces(marker_line_width=0, textposition="outside", cliponaxis=False)
    return apply_chart_theme(fig)


def donut_chart(df: pd.DataFrame, names: str, values: str, title: str) -> go.Figure:
    fig = px.pie(df, names=names, values=values, hole=0.62, title=title)
    fig.update_traces(textposition="inside", textinfo="percent+label")
    return apply_chart_theme(fig)
