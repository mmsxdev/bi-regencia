# -*- coding: utf-8 -*-
"""
Gera os PNGs dos graficos usados na apresentacao (PPT / PDF backup / handout).

Uso:
    python gerar_graficos.py

Requisitos: plotly, kaleido, pandas, openpyxl (instalar: pip install plotly kaleido pandas openpyxl)
Saida: pasta ./graficos/ (varios .png em tema escuro SENAI, mesmo visual do app).
"""
import glob
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from data_loader import MONTH_LABELS, load_regencia, melt_monthly

OUT = os.path.join(os.path.dirname(__file__), "graficos")
os.makedirs(OUT, exist_ok=True)

# ---- Paleta SENAI (igual ao app) ----
BG = "#0B0F14"
CARD = "#111827"
BORDA = "#2A303A"
TEXTO = "#F3F4F6"
TEXTO_SEC = "#9CA3AF"
GRID = "#2A3038"
AXIS = "#4B5563"
COR_AZUL_CLARO = "#2E90FA"
COR_VERMELHO = "#D71920"

FREQ_STOPS = [
    (0.00, "#B91C1C"), (0.20, "#D71920"), (0.35, "#F97316"), (0.45, "#F59E0B"),
    (0.55, "#FACC15"), (0.70, "#A3E635"), (0.85, "#22C55E"), (1.00, "#16A34A"),
]
FREQ_COLORSCALE = [[pos, color] for pos, color in FREQ_STOPS]


def _hex2rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def freq_color(pct):
    x = max(0.0, min(100.0, float(pct))) / 100.0
    for i in range(len(FREQ_STOPS) - 1):
        p0, c0 = FREQ_STOPS[i]
        p1, c1 = FREQ_STOPS[i + 1]
        if p0 <= x <= p1:
            t = (x - p0) / (p1 - p0) if p1 != p0 else 0.0
            r0, g0, b0 = _hex2rgb(c0)
            r1, g1, b1 = _hex2rgb(c1)
            return "#%02x%02x%02x" % (
                round(r0 + (r1 - r0) * t), round(g0 + (g1 - g0) * t), round(b0 + (b1 - b0) * t))
    return FREQ_STOPS[-1][1]


def style(fig, width=1280, height=700):
    fig.update_layout(
        font=dict(family="Inter, Segoe UI, Helvetica, Arial", color=TEXTO, size=15),
        width=width, height=height,
        paper_bgcolor=BG, plot_bgcolor=BG,
        margin=dict(l=16, r=16, t=40, b=16),
        xaxis=dict(gridcolor=GRID, linecolor=AXIS, zeroline=False, automargin=True,
                   tickfont=dict(color=TEXTO_SEC, size=13)),
        yaxis=dict(gridcolor=GRID, linecolor=AXIS, zeroline=False, automargin=True,
                   tickfont=dict(color=TEXTO_SEC, size=13)),
        hoverlabel=dict(bgcolor=CARD, bordercolor=BORDA, font=dict(color=TEXTO, size=13)),
    )
    return fig


def save(fig, name):
    path = os.path.join(OUT, name)
    fig.write_image(path)
    print("OK", name)


def main():
    path = glob.glob(os.path.join(os.path.dirname(__file__), "..", "*.xlsx"))[0]
    df = load_regencia(path)
    monthly = melt_monthly(df)

    fcols = [m + "_PCT" for m in ["JAN", "FEV", "MAR", "ABR", "MAI", "JUN", "JUL", "AGO", "SET", "OUT", "NOV", "DEZ"]]
    hcols = [m + "_H_AULA" for m in ["JAN", "FEV", "MAR", "ABR", "MAI", "JUN", "JUL", "AGO", "SET", "OUT", "NOV", "DEZ"]]

    # 1) Frequencia media por mes (linha)
    mes_p = monthly.groupby("MES", observed=True)["PCT"].mean().reset_index()
    mes_p["PCT%"] = (mes_p["PCT"] * 100).round(1)
    fig = px.line(mes_p, x="MES", y="PCT%", markers=True,
                  color_discrete_sequence=[COR_AZUL_CLARO])
    fig.update_traces(line=dict(width=4), marker=dict(size=10),
                      text=mes_p["PCT%"], textposition="top center",
                      textfont=dict(color=TEXTO, size=12),
                      hovertemplate="<b>%{x}</b><br>Frequência: %{y:.1f}%<extra></extra>")
    fig.update_yaxes(tickformat="", range=[0, 95], ticksuffix="%")
    fig.add_hline(y=61.0, line_dash="dash", line_color=TEXTO_SEC,
                  annotation_text="Média do ano: 61%", annotation_position="bottom right",
                  annotation_font_color=TEXTO_SEC)
    save(style(fig, width=1280, height=640), "mes_frequencia_line.png")

    # 2) Horas totais por mes (barra)
    mes_h = monthly.groupby("MES", observed=True)["HORAS"].sum().reset_index()
    mes_h["HORAS"] = mes_h["HORAS"].round(0)
    fig = px.bar(mes_h, x="MES", y="HORAS")
    fig.update_traces(marker_color=COR_AZUL_CLARO,
                      text=mes_h["HORAS"].apply(lambda v: f"{v:,.0f}".replace(",", ".")),
                      textposition="outside", textfont=dict(color=TEXTO, size=12),
                      hovertemplate="<b>%{x}</b><br>%{y:,.0f} horas<extra></extra>")
    fig.update_yaxes(tickformat=",", range=[0, mes_h["HORAS"].max() * 1.15])
    save(style(fig, width=1280, height=640), "mes_horas_bar.png")

    # 3) Distribuicao da frequencia media (histograma)
    df2 = df.copy()
    df2["FREQ_MEDIA"] = df2[fcols].mean(axis=1) * 100
    import numpy as np
    vals = df2["FREQ_MEDIA"].dropna().to_numpy(dtype=float)
    bins = np.linspace(0, 110, 12)
    counts, edges = np.histogram(vals, bins=bins)
    centers = (edges[:-1] + edges[1:]) / 2
    width = edges[1] - edges[0]
    fig = px.bar(x=centers, y=counts,
                 labels={"x": "Frequência média (%)", "y": "Instrutores"})
    fig.update_traces(width=width, marker_color=[freq_color(c) for c in centers],
                      marker_line_color=BG, marker_line_width=1,
                      hovertemplate="Frequência: %{x:.0f}%<br>Instrutores: %{y}<extra></extra>")
    fig.update_yaxes(dtick=1)
    save(style(fig, width=900, height=560), "distribuicao_hist.png")

    # 4) Frequencia media por area (barras horizontais)
    area = df2.groupby("AREA").agg(n=("DOCENTE", "count"), f=("FREQ_MEDIA", "mean")).reset_index()
    area = area.sort_values("f")
    fig = px.bar(area, x="f", y="AREA", orientation="h",
                 text=area["f"].apply(lambda v: f"{v:.1f}%"))
    fig.update_traces(marker_color=[freq_color(v) for v in area["f"]],
                      textposition="outside", textfont=dict(color=TEXTO, size=12),
                      hovertemplate="<b>%{y}</b><br>%{x:.1f}%<extra></extra>")
    fig.update_xaxes(range=[0, 90], ticksuffix="%")
    save(style(fig, width=1100, height=600), "area_freq_bar.png")

    # 5) 10 menores frequencias
    low = df2.sort_values("FREQ_MEDIA").head(10)
    fig = px.bar(low, x="FREQ_MEDIA", y="DOCENTE", orientation="h",
                 text=low["FREQ_MEDIA"].apply(lambda v: f"{v:.1f}%"))
    fig.update_traces(marker_color=[freq_color(v) for v in low["FREQ_MEDIA"]],
                      textposition="outside", textfont=dict(color=TEXTO, size=12),
                      hovertemplate="<b>%{y}</b><br>%{x:.1f}%<extra></extra>")
    fig.update_xaxes(range=[0, 60], ticksuffix="%")
    save(style(fig, width=1100, height=620), "instrutores_menor.png")

    # 6) 10 maiores frequencias
    high = df2.sort_values("FREQ_MEDIA", ascending=False).head(10)
    fig = px.bar(high, x="FREQ_MEDIA", y="DOCENTE", orientation="h",
                 text=high["FREQ_MEDIA"].apply(lambda v: f"{v:.1f}%"))
    fig.update_traces(marker_color=[freq_color(v) for v in high["FREQ_MEDIA"]],
                      textposition="outside", textfont=dict(color=TEXTO, size=12),
                      hovertemplate="<b>%{y}</b><br>%{x:.1f}%<extra></extra>")
    fig.update_xaxes(range=[0, 120], ticksuffix="%")
    save(style(fig, width=1100, height=620), "instrutores_maior.png")

    # 7) Top 10 horas no ano
    df2["H_ANO"] = df2["TOTAL_H_ANO"].fillna(0)
    top_h = df2.sort_values("H_ANO", ascending=False).head(10)
    fig = px.bar(top_h, x="H_ANO", y="DOCENTE", orientation="h")
    fig.update_traces(marker_color=COR_AZUL_CLARO,
                      text=top_h["H_ANO"].apply(lambda v: f"{v:,.0f}".replace(",", ".")),
                      textposition="outside", textfont=dict(color=TEXTO, size=12),
                      hovertemplate="<b>%{y}</b><br>%{x:,.0f} h<extra></extra>")
    fig.update_xaxes(tickformat=",", range=[0, top_h["H_ANO"].max() * 1.15])
    save(style(fig, width=1100, height=620), "ranking_horas.png")

    # 8) Heatmap instrutor x mes
    pivot = (monthly.pivot_table(index="DOCENTE", columns="MES", values="PCT") * 100)
    pivot = pivot.fillna(-1)  # sem registro
    fig = go.Figure(go.Heatmap(
        z=pivot.values, x=pivot.columns, y=pivot.index,
        colorscale=FREQ_COLORSCALE, zmin=0, zmax=100,
        text=np.round(pivot.values, 0),
        texttemplate="%{text:.0f}",
        textfont=dict(size=10, color=TEXTO),
        colorbar=dict(title="%", tickfont=dict(color=TEXTO_SEC)),
        hovertemplate="<b>%{y}</b> - %{x}<br>Frequência: %{z:.1f}%<extra></extra>",
    ))
    fig.update_layout(font=dict(family="Inter, Segoe UI", color=TEXTO, size=13),
                      width=1400, height=1000, paper_bgcolor=BG, plot_bgcolor=BG,
                      margin=dict(l=240, r=30, t=20, b=30),
                      yaxis=dict(tickfont=dict(color=TEXTO, size=11)),
                      xaxis=dict(tickfont=dict(color=TEXTO_SEC, size=12)))
    save(fig, "heatmap.png")

    # 9) Manutencao automotiva - area unificada, colorido por POLO
    auto = df2[df2["AREA"] == "Manutenção automotiva"].copy()
    auto = auto.sort_values("FREQ_MEDIA")
    auto["GRUPO"] = auto["POLO"].apply(
        lambda p: "Polo John Deere" if "Deere" in str(p) else "Vila Canaã"
    )
    fig = px.bar(auto, x="FREQ_MEDIA", y="DOCENTE", orientation="h",
                 color="GRUPO",
                 color_discrete_map={"Vila Canaã": COR_AZUL_CLARO, "Polo John Deere": COR_VERMELHO},
                 text=auto["FREQ_MEDIA"].apply(lambda v: f"{v:.1f}%"))
    fig.update_traces(textposition="outside", textfont=dict(color=TEXTO, size=11),
                      hovertemplate="<b>%{y}</b><br>%{x:.1f}%<extra></extra>")
    fig.update_xaxes(range=[0, 90], ticksuffix="%")
    save(style(fig, width=1100, height=680), "automotiva_polos.png")


if __name__ == "__main__":
    main()