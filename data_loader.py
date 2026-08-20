import pandas as pd

MONTHS = [
    "JAN",
    "FEV",
    "MAR",
    "ABR",
    "MAI",
    "JUN",
    "JUL",
    "AGO",
    "SET",
    "OUT",
    "NOV",
    "DEZ",
]

MONTH_LABELS = [
    "Janeiro",
    "Fevereiro",
    "Março",
    "Abril",
    "Maio",
    "Junho",
    "Julho",
    "Agosto",
    "Setembro",
    "Outubro",
    "Novembro",
    "Dezembro",
]

SHEET_NAME = "CONSOLIDADO "
HEADER_ROW = 4
DAYWEEK_ROW = 5
DATA_START = 6

# ---------------------------------------------------------------------------
# Normalização de áreas técnicas
# ---------------------------------------------------------------------------
# O painel unifica nomes duplicados/errôneos digitados na planilha para que a
# análise por área não fique fragmentada. Ex.: "Manutenção automotiva (JD)"
# era um rótulo interno do polo de treinamento John Deere da MESMA área.
# As chaves estão em MAIÚSCULO (comparação case-insensitive).
AREA_NORM = {
    "MANUTENÇÃO AUTOMOTIVA (JD)": "Manutenção automotiva",
    "CONTRUÇÃO CIVIL": "Construção Civil",
    "GRAFICA EDITORIAL": "Gráfica editorial",
}

# Polo/local de regência
# - Se a planilha tiver uma coluna POLO/LOCAL (na linha de cabeçalho), ela é lida.
# - Se não existir (ou célula vazia), o valor é inferido a partir do rótulo antigo:
#   "(JD)" -> polo do treinamento John Deere; demais -> unidade-base (Vila Canaã).
# Recomenda-se que a coordenação preencha POLO/LOCAL para todos os instrutores.
POLO_DEFAULT = "Vila Canaã"
POLO_JD_LEGACY = "John Deere"
POLO_HEADERS = ("POLO", "LOCAL", "LOCAL DE REGÊNCIA", "LOCAL DE REGENCIA", "POLO/LOCAL", "POLO / LOCAL")


def _norm_area(value):
    """Normaliza nomes de área (remove espaços, acertos de digitação e duplicados)."""
    s = str(value).strip() if value is not None and not (isinstance(value, float) and pd.isna(value)) else ""
    if not s:
        return "SEM ÁREA"
    return AREA_NORM.get(s.upper(), s)


def _find_polo_column(header4: list):
    """Localiza a coluna POLO/LOCAL na linha de cabeçalho (se existir)."""
    for i, v in enumerate(header4):
        if isinstance(v, str):
            up = v.strip().upper()
            if up in POLO_HEADERS or up.startswith("POLO"):
                return i
    return None


def _to_num(value):
    if value is None:
        return None
    if isinstance(value, str):
        value = value.strip()
        if value in ("", "-", "--"):
            return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _find_month_columns(header4: list) -> dict:
    cols = {}
    for month in MONTHS:
        match = [i for i, v in enumerate(header4) if isinstance(v, str) and v.strip() == month]
        if match:
            cols[month] = match[0]
        else:
            match = [i for i, v in enumerate(header4) if isinstance(v, str) and v.strip().startswith(month)]
            if match:
                cols[month] = match[0]
    return cols


def _locate_labels(header4: list) -> dict:
    labels = {}
    for label in ["ANO", "MÉDIA", "EXTRA-QUADRO"]:
        match = [i for i, v in enumerate(header4) if isinstance(v, str) and v.strip().upper() == label]
        if match:
            labels[label] = match[0]
    return labels


def load_regencia(source) -> pd.DataFrame:
    df = pd.read_excel(source, sheet_name=SHEET_NAME, header=None)
    header4 = df.iloc[HEADER_ROW].tolist()

    month_cols = _find_month_columns(header4)
    labels = _locate_labels(header4)
    polo_col = _find_polo_column(header4)

    rows = []
    for idx in range(DATA_START, len(df)):
        nome = df.iloc[idx, 0]
        if pd.isna(nome):
            continue
        ch = df.iloc[idx, 1]
        area_raw = df.iloc[idx, 2]
        area = _norm_area(area_raw)
        area_upper = str(area_raw).strip().upper() if pd.notna(area_raw) else ""

        polo = None
        if polo_col is not None:
            v = df.iloc[idx, polo_col]
            polo = str(v).strip() if pd.notna(v) and str(v).strip() else None
        if not polo:
            # Inferência: rótulo antigo (JD) = polo do treinamento John Deere
            polo = POLO_JD_LEGACY if "(JD)" in area_upper else POLO_DEFAULT

        carga = None
        if pd.notna(ch):
            try:
                carga = int("".join(c for c in str(ch) if c.isdigit()) or 0)
            except (TypeError, ValueError):
                carga = None

        record = {
            "DOCENTE": str(nome).strip().upper(),
            "CARGA_HORARIA": carga,
            "AREA": area,
            "POLO": polo,
        }

        total_ano = None
        if "ANO" in labels:
            total_ano = df.iloc[idx, labels["ANO"]]
        extra = None
        if "EXTRA-QUADRO" in labels:
            extra = df.iloc[idx, labels["EXTRA-QUADRO"]]

        for month in MONTHS:
            if month not in month_cols:
                record[f"{month}_H_AULA"] = None
                record[f"{month}_PCT"] = None
                continue
            c = month_cols[month]
            record[f"{month}_H_AULA"] = _to_num(df.iloc[idx, c])
            record[f"{month}_PCT"] = _to_num(df.iloc[idx, c + 1])

        record["TOTAL_H_ANO"] = _to_num(total_ano)
        record["EXTRA_QUADRO"] = _to_num(extra)
        rows.append(record)

    return pd.DataFrame(rows)


def melt_monthly(df: pd.DataFrame) -> pd.DataFrame:
    id_vars = ["DOCENTE", "CARGA_HORARIA", "AREA", "POLO", "TOTAL_H_ANO", "EXTRA_QUADRO"]
    month_map = {f"{m}_H_AULA": MONTH_LABELS[i] for i, m in enumerate(MONTHS)}
    value_cols = list(month_map.keys())
    melted = df.melt(id_vars=id_vars, value_vars=value_cols, var_name="MES_COL", value_name="HORAS")
    melted["MES"] = melted["MES_COL"].map(month_map)
    melted = melted.drop(columns=["MES_COL"])

    pct_map = {f"{m}_PCT": MONTH_LABELS[i] for i, m in enumerate(MONTHS)}
    pcts = df.melt(id_vars=["DOCENTE"], value_vars=list(pct_map.keys()), var_name="MES_COL", value_name="PCT")
    pcts["MES"] = pcts["MES_COL"].map(pct_map)
    pcts = pcts.drop(columns=["MES_COL"])

    merged = melted.merge(pcts, on=["DOCENTE", "MES"], how="left")
    merged["MES"] = pd.Categorical(merged["MES"], categories=MONTH_LABELS, ordered=True)
    return merged
