import io
import os

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import streamlit as st

from data_loader import MONTH_LABELS, load_regencia, melt_monthly

# ---------------------------------------------------------------------------
# Paleta - Dark Corporate SENAI
# ---------------------------------------------------------------------------
COR_BG = "#0B0F14"
COR_CARD = "#111827"
COR_SURFACE = "#1A2029"
COR_BORDA = "#2A303A"
COR_TEXTO = "#F3F4F6"
COR_TEXTO_SEC = "#9CA3AF"
COR_TEXTO_TER = "#6B7280"
COR_GRID = "#2A3038"
COR_AXIS = "#4B5563"
COR_VERMELHO = "#D71920"
COR_AZUL = "#0066A1"
COR_AZUL_CLARO = "#2E90FA"

PLOTLY_CONFIG = {"displayModeBar": False, "displaylogo": False}

FREQ_STOPS = [
    (0.00, "#B91C1C"),
    (0.20, "#D71920"),
    (0.35, "#F97316"),
    (0.45, "#F59E0B"),
    (0.55, "#FACC15"),
    (0.70, "#A3E635"),
    (0.85, "#22C55E"),
    (1.00, "#16A34A"),
]
FREQ_COLORSCALE = [[pos, color] for pos, color in FREQ_STOPS]

st.set_page_config(
    page_title="BI de Regência - Frequência de Instrutores",
    layout="wide",
)

EXCEL_PATH = os.environ.get(
    "REGENCIA_EXCEL",
    os.path.join(os.path.dirname(__file__), "REGÊNCIA - INSTRUTORES DO QUADRO 2026.xlsx"),
)
EXCEL_URL = os.environ.get("REGENCIA_EXCEL_URL", None)
REFRESH_MINUTES = int(os.environ.get("REGENCIA_REFRESH_MINUTES", "10"))

MONTH_ORDER = MONTH_LABELS
MONTH_ORDER_ACRN = ["JAN", "FEV", "MAR", "ABR", "MAI", "JUN", "JUL", "AGO", "SET", "OUT", "NOV", "DEZ"]


def _hex2rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))


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
                round(r0 + (r1 - r0) * t),
                round(g0 + (g1 - g0) * t),
                round(b0 + (b1 - b0) * t),
            )
    return FREQ_STOPS[-1][1]


def inject_css():
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

        html, body, [class*="css"] {{
            font-family: 'Inter', 'Segoe UI', Helvetica, Arial, sans-serif;
            color: {COR_TEXTO};
        }}

        [data-testid="stAppViewContainer"] {{
            background-color: {COR_BG};
        }}
        [data-testid="stHeader"] {{
            background: transparent;
        }}
        .block-container {{
            padding-top: 1.1rem;
            padding-bottom: 2rem;
            max-width: 1440px;
        }}

        /* ---------- Header compacto ---------- */
        .senai-header {{
            background: {COR_CARD};
            border: 1px solid {COR_BORDA};
            border-left: 5px solid {COR_VERMELHO};
            border-radius: 8px;
            padding: 10px 20px;
            margin-bottom: 16px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 8px 16px;
        }}
        .senai-header .brand-line {{
            display: flex;
            align-items: baseline;
            gap: 12px;
        }}
        .senai-header .brand {{
            font-size: 22px;
            font-weight: 800;
            letter-spacing: 5px;
            color: {COR_VERMELHO};
            line-height: 1;
        }}
        .senai-header .brand-sub {{
            font-size: 11px;
            color: {COR_TEXTO_SEC};
            letter-spacing: 0.4px;
            font-weight: 500;
        }}
        .senai-header .title {{
            font-size: 15px;
            font-weight: 700;
            color: {COR_TEXTO};
            letter-spacing: 0.3px;
        }}
        .senai-header .subtitle {{
            font-size: 12px;
            color: {COR_TEXTO_SEC};
            font-weight: 500;
        }}
        .senai-header .right {{
            text-align: right;
        }}

        /* ---------- Cards / containers ---------- */
        [data-testid="stVerticalBlockBorderWrapper"] {{
            border-radius: 8px;
            border-color: {COR_BORDA};
            background: {COR_CARD};
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.25);
        }}

        /* ---------- KPI ---------- */
        .kpi-card {{
            background: {COR_CARD};
            border: 1px solid {COR_BORDA};
            border-top: 3px solid {COR_VERMELHO};
            border-radius: 8px;
            padding: 14px 18px 12px;
            height: 100%;
            box-shadow: 0 1px 2px rgba(0, 0, 0, 0.25);
        }}
        .kpi-card .label {{
            font-size: 11px;
            font-weight: 600;
            letter-spacing: 0.8px;
            text-transform: uppercase;
            color: {COR_TEXTO_SEC};
        }}
        .kpi-card .value {{
            font-size: 31px;
            font-weight: 700;
            color: {COR_TEXTO};
            line-height: 1.15;
            margin-top: 2px;
        }}
        .kpi-card .hint {{
            font-size: 12px;
            color: {COR_TEXTO_TER};
            margin-top: 4px;
        }}
        .kpi-dot {{
            display: inline-block;
            width: 11px;
            height: 11px;
            border-radius: 50%;
            margin-right: 8px;
            vertical-align: middle;
            border: 1px solid rgba(255,255,255,0.35);
        }}

        /* ---------- Títulos de seção ---------- */
        .section-title {{
            font-size: 16px;
            font-weight: 700;
            color: {COR_TEXTO};
            margin: 0 0 10px 0;
            padding-bottom: 6px;
            border-bottom: 1px solid {COR_BORDA};
        }}
        .section-caption {{
            font-size: 12px;
            color: {COR_TEXTO_SEC};
            margin: 8px 0 0 0;
        }}

        /* ---------- Legenda da frequência ---------- */
        .freq-legend {{
            margin: 2px 0 12px 0;
        }}
        .freq-legend-inner {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .freq-legend-end {{
            font-size: 11px;
            font-weight: 600;
            color: {COR_TEXTO_SEC};
        }}
        .freq-legend-bar {{
            flex: 0 1 260px;
            height: 9px;
            border-radius: 5px;
            background: linear-gradient(90deg,
                #B91C1C, #D71920, #F97316, #F59E0B,
                #FACC15, #A3E635, #22C55E, #16A34A);
            border: 1px solid {COR_BORDA};
        }}
        .freq-legend-marks {{
            font-size: 10px;
            color: {COR_TEXTO_TER};
            letter-spacing: 3px;
            margin: 4px 0 0 42px;
        }}

        /* ---------- Filtros ---------- */
        .filters-title {{
            font-size: 13px;
            font-weight: 600;
            color: {COR_TEXTO};
            margin-bottom: 8px;
        }}
        .filters-title .red {{
            color: {COR_VERMELHO};
        }}
        [data-testid="stMultiSelect"] label {{
            font-size: 12px;
            font-weight: 600;
            color: {COR_TEXTO_SEC};
        }}
        [data-testid="stMultiSelect"] [data-baseweb="select"] > div {{
            background-color: {COR_SURFACE} !important;
            border-color: {COR_BORDA} !important;
            color: {COR_TEXTO} !important;
            font-size: 13px;
        }}
        [data-testid="stMultiSelect"] [data-baseweb="select"] input {{
            color: {COR_TEXTO} !important;
        }}
        [data-testid="stMultiSelect"] [data-baseweb="select"] [data-baseweb="tag"] {{
            background-color: {COR_VERMELHO} !important;
            color: #FFFFFF !important;
        }}
        [data-testid="stMultiSelect"] [data-baseweb="popover"] [data-baseweb="menu"] {{
            background-color: {COR_SURFACE} !important;
        }}
        [data-testid="stMultiSelect"] [data-baseweb="popover"] [role="option"] {{
            color: {COR_TEXTO} !important;
        }}
        [data-testid="stMultiSelect"] [data-baseweb="popover"] [role="option"]:hover {{
            background-color: {COR_BORDA} !important;
        }}
        [data-testid="stMultiSelect"] [data-baseweb="select"]:focus-within > div {{
            border-color: {COR_AZUL_CLARO} !important;
        }}

        /* ---------- Abas ---------- */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 4px;
            background: {COR_CARD};
            border: 1px solid {COR_BORDA};
            border-radius: 8px;
            padding: 4px;
            margin-bottom: 18px;
        }}
        .stTabs [data-baseweb="tab"] {{
            height: 38px;
            border-radius: 6px;
            padding: 0 22px;
            font-size: 14px;
            font-weight: 500;
            color: {COR_TEXTO_SEC};
        }}
        .stTabs [data-baseweb="tab"]:hover {{
            color: {COR_TEXTO};
        }}
        .stTabs [aria-selected="true"] {{
            background: {COR_VERMELHO};
            color: #FFFFFF !important;
            font-weight: 600;
        }}
        .stTabs [data-baseweb="tab-highlight"] {{
            display: none;
        }}
        .stTabs [data-baseweb="tab-border"] {{
            display: none;
        }}

        /* ---------- Sidebar ---------- */
        [data-testid="stSidebar"] {{
            background: {COR_BG};
            border-right: 1px solid {COR_BORDA};
        }}
        .sidebar-title {{
            font-size: 13px;
            font-weight: 700;
            letter-spacing: 0.6px;
            text-transform: uppercase;
            color: {COR_VERMELHO};
            margin-bottom: 10px;
        }}
        .sidebar-note {{
            font-size: 12px;
            color: {COR_TEXTO_SEC};
            line-height: 1.6;
            border-top: 1px solid {COR_BORDA};
            padding-top: 10px;
            margin-top: 14px;
        }}
        .sidebar-note b {{
            color: {COR_VERMELHO};
        }}
        .sidebar-note code {{
            color: {COR_TEXTO};
            background: {COR_SURFACE};
            padding: 1px 4px;
            border-radius: 4px;
        }}

        /* ---------- Botões ---------- */
        .stButton > button, .stDownloadButton button {{
            background: {COR_AZUL};
            color: #FFFFFF;
            border: none;
            border-radius: 6px;
            font-weight: 600;
            font-size: 13px;
        }}
        .stButton > button:hover, .stDownloadButton button:hover {{
            background: {COR_AZUL_CLARO};
            color: #FFFFFF;
            border: none;
        }}
        .stButton > button[kind="secondary"], .stDownloadButton button[kind="secondary"] {{
            background: {COR_SURFACE};
            color: {COR_TEXTO_SEC};
            border: 1px solid {COR_BORDA};
        }}
        .stButton > button[kind="secondary"]:hover {{
            background: {COR_BORDA};
            color: {COR_TEXTO};
            border: 1px solid {COR_BORDA};
        }}

        /* ---------- Tabela ---------- */
        [data-testid="stDataFrame"] {{
            border: 1px solid {COR_BORDA};
            border-radius: 8px;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header():
    st.markdown(
        f"""
        <div class="senai-header">
            <div class="brand-line">
                <span class="brand">SENAI</span>
                <span class="brand-sub">SERVIÇO NACIONAL DE APRENDIZAGEM INDUSTRIAL</span>
            </div>
            <div class="right">
                <div class="title">BI DE REGÊNCIA - FREQUÊNCIA DOS INSTRUTORES</div>
                <div class="subtitle">Quadro de instrutores 2026</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def kpi_cards(instrutores, horas_periodo, freq_media, total_ano):
    freq_pct = freq_media * 100
    dot = f'<span class="kpi-dot" style="background:{freq_color(freq_pct)};"></span>'
    cards = [
        ("Instrutores ativos", f"{instrutores}", "no conjunto filtrado", ""),
        ("Horas-aula no período", f"{horas_periodo:,.0f}".replace(",", "."), "soma dos meses selecionados", ""),
        ("Frequência média", f"{freq_pct:.1f}%", "horas realizadas vs. esperadas", dot),
        ("Horas-aula no ano", f"{total_ano:,.0f}".replace(",", "."), "total consolidado do quadro", ""),
    ]
    cols = st.columns(4)
    for col, (label, value, hint, badge) in zip(cols, cards):
        col.markdown(
            f"""
            <div class="kpi-card">
                <div class="label">{label}</div>
                <div class="value">{badge}{value}</div>
                <div class="hint">{hint}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def section_title(text):
    st.markdown(f'<div class="section-title">{text}</div>', unsafe_allow_html=True)


def section_caption(text):
    st.markdown(f'<div class="section-caption">{text}</div>', unsafe_allow_html=True)


def frequency_legend():
    st.markdown(
        f"""
        <div class="freq-legend">
            <div class="freq-legend-inner">
                <span class="freq-legend-end">Baixa</span>
                <div class="freq-legend-bar"></div>
                <span class="freq-legend-end">Alta</span>
            </div>
            <div class="freq-legend-marks">0%&nbsp;&nbsp;25%&nbsp;&nbsp;50%&nbsp;&nbsp;75%&nbsp;&nbsp;100%</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def frequency_histogram(series):
    import numpy as np

    vals = pd.Series(series).dropna().to_numpy(dtype=float)
    bins = np.linspace(0, 100, 15)
    counts, edges = np.histogram(vals, bins=bins)
    centers = (edges[:-1] + edges[1:]) / 2
    width = edges[1] - edges[0]
    fig = px.bar(
        x=centers,
        y=counts,
        labels={"x": "Frequência média (%)", "y": "Instrutores"},
    )
    fig.update_traces(
        width=width,
        marker_color=[freq_color(c) for c in centers],
        marker_line_color=COR_BG,
        marker_line_width=0.5,
        hovertemplate="Frequência: %{x:.1f}%<br>Instrutores: %{y}<extra></extra>",
    )
    fig.update_layout(yaxis_title="Instrutores", xaxis_title="Frequência média (%)")
    return fig


def style_chart(fig, height=None):
    fig.update_layout(
        font=dict(family="Inter, Segoe UI, Helvetica, Arial", color=COR_TEXTO, size=13),
        height=height,
        margin=dict(l=8, r=14, t=18, b=8),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(
            gridcolor=COR_GRID,
            linecolor=COR_AXIS,
            zeroline=False,
            automargin=True,
            tickfont=dict(color=COR_TEXTO_SEC, size=12),
        ),
        yaxis=dict(
            gridcolor=COR_GRID,
            linecolor=COR_AXIS,
            zeroline=False,
            automargin=True,
            tickfont=dict(color=COR_TEXTO_SEC, size=12),
        ),
        coloraxis_colorbar=dict(thickness=12, tickfont=dict(color=COR_TEXTO_SEC, size=11), outlinewidth=0),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color=COR_TEXTO_SEC, size=12)),
        hoverlabel=dict(bgcolor=COR_SURFACE, bordercolor=COR_BORDA, font=dict(color=COR_TEXTO, size=12)),
    )
    return fig


def chart_card(fig, height=None, y_primary=False, scroll_height=None):
    if height is not None:
        fig.update_layout(height=height)
    style_chart(fig, height=fig.layout.height)
    if y_primary:
        fig.update_yaxes(tickfont=dict(color=COR_TEXTO, size=12))

    if scroll_height is not None:
        with st.container(border=True, height=scroll_height):
            st.plotly_chart(fig, width="stretch", config=PLOTLY_CONFIG)
    else:
        with st.container(border=True):
            st.plotly_chart(fig, width="stretch", config=PLOTLY_CONFIG)


# ---------------------------------------------------------------------------
# Fonte de dados (arquivo local / link SharePoint / upload)
# ---------------------------------------------------------------------------
def _download(url):
    resp = requests.get(url, timeout=90, headers={"User-Agent": "Mozilla/5.0"})
    resp.raise_for_status()
    return io.BytesIO(resp.content)


@st.cache_data(show_spinner="Atualizando dados da planilha...", ttl=REFRESH_MINUTES * 60)
def load_from_url(url):
    raw = _download(url)
    df = load_regencia(raw)
    return df, melt_monthly(df)


@st.cache_data(show_spinner="Lendo planilha local...")
def load_from_file(path):
    df = load_regencia(path)
    return df, melt_monthly(df)


def load_from_upload(uploaded):
    raw = io.BytesIO(uploaded.getvalue())
    df = load_regencia(raw)
    return df, melt_monthly(df)


def get_data():
    if EXCEL_URL:
        return load_from_url(EXCEL_URL), "URL (SharePoint/OneDrive)"
    if os.path.exists(EXCEL_PATH):
        return load_from_file(EXCEL_PATH), "arquivo local"
    return None, "nenhuma"


# ---------------------------------------------------------------------------
# Aplicação
# ---------------------------------------------------------------------------
def main():
    inject_css()
    render_header()

    df, monthly = None, None

    with st.sidebar:
        st.markdown('<div class="sidebar-title">Fonte de dados</div>', unsafe_allow_html=True)
        if EXCEL_URL:
            st.markdown(
                f'<div class="sidebar-note">Conexão: <b>URL</b><br>'
                f"Atualiza automática a cada {REFRESH_MINUTES} min.</div>",
                unsafe_allow_html=True,
            )
        elif os.path.exists(EXCEL_PATH):
            st.markdown(
                f'<div class="sidebar-note">Conexão: <b>arquivo local</b><br>'
                f"Arquivo: <code>{os.path.basename(EXCEL_PATH)}</code></div>",
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div class="sidebar-note">Nenhuma fonte configurada. Envie a planilha abaixo.</div>',
                unsafe_allow_html=True,
            )
            uploaded = st.file_uploader("Planilha de regência (xlsx)", type=["xlsx"])
            if uploaded is not None:
                df, monthly = load_from_upload(uploaded)

        if st.button("Atualizar dados agora", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    if df is None and monthly is None:
        (df, monthly), _ = get_data()

    if df is None or monthly is None:
        st.error(
            "Planilha não encontrada.\n\n"
            "- Defina a variável de ambiente REGENCIA_EXCEL (caminho local) ou\n"
            "- REGENCIA_EXCEL_URL (link direto do SharePoint/OneDrive), ou\n"
            "- envie o arquivo pela barra lateral."
        )
        st.stop()

    if df.empty:
        st.warning("Nenhum dado encontrado na aba CONSOLIDADO.")
        st.stop()

    areas = sorted(df["AREA"].dropna().unique())
    docentes = sorted(df["DOCENTE"].dropna().unique())
    polos = sorted(df["POLO"].dropna().unique())

    # ---------- Filtros ----------
    if "sel_docentes" not in st.session_state:
        st.session_state.sel_docentes = []
    if "sel_areas" not in st.session_state:
        st.session_state.sel_areas = []
    if "sel_polos" not in st.session_state:
        st.session_state.sel_polos = []
    if "sel_meses" not in st.session_state:
        st.session_state.sel_meses = MONTH_ORDER

    def reset_filters():
        st.session_state.sel_docentes = []
        st.session_state.sel_areas = []
        st.session_state.sel_polos = []
        st.session_state.sel_meses = MONTH_ORDER

    with st.container(border=True):
        st.markdown(
            '<div class="filters-title">Filtros <span class="red">|</span> período analisado</div>',
            unsafe_allow_html=True,
        )
        c_doc, c_area, c_polo, c_mes, c_btn = st.columns([3, 2.5, 2.5, 2.5, 1.5])
        with c_doc:
            st.multiselect("Instrutor(es)", docentes, key="sel_docentes", placeholder="Todos os instrutores")
        with c_area:
            st.multiselect("Área", areas, key="sel_areas", placeholder="Todas as áreas")
        with c_polo:
            st.multiselect("Polo / Local", polos, key="sel_polos", placeholder="Todos os polos")
        with c_mes:
            st.multiselect("Meses do período", MONTH_ORDER, key="sel_meses")
        with c_btn:
            st.write("")
            st.button("Limpar filtros", use_container_width=True, on_click=reset_filters)

    sel_docentes = st.session_state.sel_docentes
    sel_areas = st.session_state.sel_areas
    sel_polos = st.session_state.sel_polos
    sel_meses = st.session_state.sel_meses

    df_f = df.copy()
    if sel_docentes:
        df_f = df_f[df_f["DOCENTE"].isin(sel_docentes)]
    if sel_areas:
        df_f = df_f[df_f["AREA"].isin(sel_areas)]
    if sel_polos:
        df_f = df_f[df_f["POLO"].isin(sel_polos)]

    monthly_f = monthly[monthly["MES"].isin(sel_meses)].copy()
    if sel_docentes:
        monthly_f = monthly_f[monthly_f["DOCENTE"].isin(sel_docentes)]
    if sel_areas:
        monthly_f = monthly_f[monthly_f["AREA"].isin(sel_areas)]
    if sel_polos:
        monthly_f = monthly_f[monthly_f["POLO"].isin(sel_polos)]

    if df_f.empty:
        st.info("Nenhum dado corresponde aos filtros selecionados.")
        st.stop()

    n_instr = len(df_f)
    total_h_ano = df_f["TOTAL_H_ANO"].fillna(0).sum()
    total_h_periodo = monthly_f["HORAS"].fillna(0).sum()
    media_freq = monthly_f["PCT"].mean()
    media_freq = 0 if pd.isna(media_freq) else media_freq

    kpi_cards(n_instr, total_h_periodo, media_freq, total_h_ano)

    tab_geral, tab_individual, tab_mes, tab_tabela = st.tabs(
        ["Visão Geral", "Por Instrutor", "Por Mês", "Tabela"]
    )

    # ------------------------------------------------------------------
    # VISÃO GERAL
    # ------------------------------------------------------------------
    with tab_geral:
        section_title("Frequência média por instrutor")
        frequency_legend()
        freq = (
            monthly_f.groupby("DOCENTE")["PCT"]
            .mean()
            .reset_index()
            .sort_values("PCT")
        )
        freq["PCT%"] = (freq["PCT"] * 100).round(1)

        if freq.empty:
            st.info("Sem dados no período selecionado.")
        else:
            fig = px.bar(
                freq,
                x="PCT%",
                y="DOCENTE",
                orientation="h",
                labels={"PCT%": "Frequência média (%)"},
            )
            fig.update_traces(
                marker_color=[freq_color(p) for p in freq["PCT%"]],
                marker_line_width=0,
                hovertemplate="<b>%{y}</b><br>Frequência média: %{x:.1f}%<extra></extra>",
            )
            fig.add_vline(
                x=100,
                line_dash="dash",
                line_color=COR_AXIS,
                annotation_text="100%",
                annotation_position="top right",
                annotation_font_color=COR_TEXTO_SEC,
                annotation_font_size=11,
            )
            row_pitch = 36
            chart_h = max(350, row_pitch * len(freq) + 80)
            fig.update_layout(yaxis_title=None, height=chart_h)
            
            scroll_h = 550 if chart_h > 550 else None
            chart_card(fig, y_primary=True, scroll_height=scroll_h)
            section_caption(
                "Visão completa de todos os instrutores no período selecionado. Use a barra de rolagem interna do quadro para ver mais."
            )

        col_dist, col_area = st.columns(2, gap="large")

        with col_dist:
            section_title("Distribuição da frequência média")
            if not freq.empty:
                fig2 = frequency_histogram(freq["PCT%"])
                chart_card(fig2, height=330)

        with col_area:
            section_title("Horas-aula por área")
            area_h = (
                monthly_f.groupby("AREA")["HORAS"]
                .sum()
                .reset_index()
                .sort_values("HORAS", ascending=False)
            )
            if not area_h.empty:
                fig3 = px.bar(
                    area_h,
                    x="HORAS",
                    y="AREA",
                    orientation="h",
                    labels={"HORAS": "Horas-aula", "AREA": ""},
                )
                fig3.update_traces(
                    marker_color=COR_AZUL_CLARO,
                    marker_line_width=0,
                    hovertemplate="<b>%{y}</b><br>%{x:,.0f} horas-aula<extra></extra>",
                )
                fig3.update_layout(yaxis_title=None, height=330, xaxis=dict(tickformat=","))
                chart_card(fig3, height=330, y_primary=True)

            section_title("Horas-aula por polo")
            polo_h = (
                monthly_f.groupby("POLO")["HORAS"]
                .sum()
                .reset_index()
                .sort_values("HORAS", ascending=False)
            )
            if not polo_h.empty:
                fig4 = px.bar(
                    polo_h,
                    x="HORAS",
                    y="POLO",
                    orientation="h",
                    labels={"HORAS": "Horas-aula", "POLO": ""},
                )
                fig4.update_traces(
                    marker_color=COR_AZUL,
                    marker_line_width=0,
                    hovertemplate="<b>%{y}</b><br>%{x:,.0f} horas-aula<extra></extra>",
                )
                fig4.update_layout(yaxis_title=None, height=300, xaxis=dict(tickformat=","))
                chart_card(fig4, height=300, y_primary=True)

    # ------------------------------------------------------------------
    # POR INSTRUTOR
    # ------------------------------------------------------------------
    with tab_individual:
        section_title("Ranking de horas-aula por instrutor")
        rank = (
            monthly_f.groupby("DOCENTE")["HORAS"]
            .sum()
            .reset_index()
            .sort_values("HORAS", ascending=False)
        )
        if rank.empty:
            st.info("Sem dados no período selecionado.")
        else:
            row_pitch_rank = 36
            chart_h_rank = max(350, row_pitch_rank * len(rank) + 80)
            fig = px.bar(
                rank,
                x="HORAS",
                y="DOCENTE",
                orientation="h",
                labels={"HORAS": "Horas-aula no período"},
            )
            fig.update_traces(
                marker_color=COR_AZUL_CLARO,
                marker_line_width=0,
                hovertemplate="<b>%{y}</b><br>%{x:,.0f} horas-aula<extra></extra>",
            )
            fig.update_layout(yaxis_title=None, height=chart_h_rank,
                              yaxis=dict(tickfont=dict(color=COR_TEXTO, size=12)))
            
            scroll_h_rank = 600 if chart_h_rank > 600 else None
            chart_card(fig, y_primary=True, scroll_height=scroll_h_rank)

        section_title("Frequência por instrutor e mês (%)")
        frequency_legend()
        if not monthly_f.empty:
            pivot = (
                monthly_f.pivot_table(index="DOCENTE", columns="MES", values="PCT")
                .reindex(columns=sel_meses)
                * 100
            )
            row_pitch_heat = 36
            chart_h_heat = max(350, row_pitch_heat * len(pivot) + 80)
            fig_h = go.Figure(
                go.Heatmap(
                    z=pivot.values,
                    x=pivot.columns,
                    y=pivot.index,
                    colorscale=FREQ_COLORSCALE,
                    zmin=0,
                    zmax=100,
                    text=np_round(pivot.values),
                    texttemplate="%{text:.0f}",
                    textfont=dict(size=12, color=COR_TEXTO),
                    colorbar=dict(title="%", tickfont=dict(color=COR_TEXTO_SEC, size=11), outlinewidth=0),
                    hovertemplate="<b>%{y}</b> - %{x}<br>Frequência: %{z:.1f}%<extra></extra>",
                )
            )
            fig_h.update_layout(
                height=chart_h_heat,
                xaxis=dict(title=None, tickfont=dict(color=COR_TEXTO_SEC, size=12), automargin=True),
                yaxis=dict(title=None, tickfont=dict(color=COR_TEXTO, size=12), automargin=True),
                hoverlabel=dict(bgcolor=COR_SURFACE, bordercolor=COR_BORDA, font=dict(color=COR_TEXTO, size=12)),
            )
            
            scroll_h_heat = 650 if chart_h_heat > 650 else None
            chart_card(fig_h, scroll_height=scroll_h_heat)

    # ------------------------------------------------------------------
    # POR MÊS
    # ------------------------------------------------------------------
    with tab_mes:
        col_hm, col_fm = st.columns(2, gap="large")

        with col_hm:
            section_title("Horas-aula totais por mês")
            mes_h = monthly_f.groupby("MES", observed=True)["HORAS"].sum().reset_index()
            if not mes_h.empty:
                fig = px.bar(
                    mes_h,
                    x="MES",
                    y="HORAS",
                    labels={"MES": "Mês", "HORAS": "Horas-aula"},
                )
                fig.update_traces(
                    marker_color=COR_AZUL_CLARO,
                    marker_line_width=0,
                    hovertemplate="<b>%{x}</b><br>%{y:,.0f} horas-aula<extra></extra>",
                )
                fig.update_layout(height=380)
                chart_card(fig, height=380)

        with col_fm:
            section_title("Frequência média por mês")
            mes_p = monthly_f.groupby("MES", observed=True)["PCT"].mean().reset_index()
            if not mes_p.empty:
                fig = px.line(
                    mes_p,
                    x="MES",
                    y="PCT",
                    markers=True,
                    color_discrete_sequence=[COR_AZUL_CLARO],
                    labels={"MES": "Mês", "PCT": "Frequência média"},
                )
                fig.update_yaxes(tickformat=".0%", range=[0, max(1.2, mes_p["PCT"].max() * 1.1)])
                fig.update_traces(line=dict(width=3), marker=dict(size=8),
                                  hovertemplate="<b>%{x}</b><br>Frequência média: %{y:.1%}<extra></extra>")
                fig.update_layout(height=380)
                chart_card(fig, height=380)

    # ------------------------------------------------------------------
    # TABELA
    # ------------------------------------------------------------------
    with tab_tabela:
        section_title("Dados consolidados")
        show = df_f.copy()
        show_cols = ["DOCENTE", "CARGA_HORARIA", "AREA", "POLO", "TOTAL_H_ANO", "EXTRA_QUADRO"]
        show_cols += [f"{m}_H_AULA" for m in MONTH_ORDER_ACRN]
        show_cols += [f"{m}_PCT" for m in MONTH_ORDER_ACRN]
        show = show[show_cols]
        st.dataframe(show, width="stretch", height=520)
        csv = show.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            "Baixar dados em CSV",
            csv,
            "regencia_consolidado.csv",
            "text/csv",
            type="secondary",
        )


def np_round(arr):
    try:
        import numpy as np

        return np.round(arr, 1)
    except Exception:
        return arr


if __name__ == "__main__":
    main()