import io
import re
from typing import Optional
import unicodedata

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

MONTH_NUM_TO_LABEL = {str(i + 1).zfill(2): MONTH_LABELS[i] for i in range(12)}
MONTH_NUM_TO_LABEL.update({str(i + 1): MONTH_LABELS[i] for i in range(12)})

SHEET_NAME = "CONSOLIDADO "
HEADER_ROW = 4
DAYWEEK_ROW = 5
DATA_START = 6

# ---------------------------------------------------------------------------
# Normalização de áreas técnicas
# ---------------------------------------------------------------------------
AREA_NORM = {
    "MANUTENÇÃO AUTOMOTIVA (JD)": "Manutenção automotiva",
    "CONTRUÇÃO CIVIL": "Construção Civil",
    "GRAFICA EDITORIAL": "Gráfica editorial",
}

# Polo/local de regência
POLO_DEFAULT = "Complexo de Educação, Tecnologia, Inovação e Saúde Paulo Vargas"
POLO_JD_LEGACY = "John Deere"
POLO_HEADERS = ("POLO", "LOCAL", "LOCAL DE REGÊNCIA", "LOCAL DE REGENCIA", "POLO/LOCAL", "POLO / LOCAL")

POLO_NORM = {
    "VILA CANAÃ": POLO_DEFAULT,
    "CANAÃ": POLO_DEFAULT,
    "SENAI CANAÃ": POLO_DEFAULT,
    "SENAI VILA CANAÃ": POLO_DEFAULT,
}

# ---------------------------------------------------------------------------
# Códigos de modalidade das abas individuais de instrutores
# ---------------------------------------------------------------------------
CODIGOS_OUTROS = {1, 2, 3, 4, 9}   # Planejamento, Reuniões, Capacitação, Banco de horas, Outros
CODIGOS_REGENCIA = {11, 21, 24, 31, 33, 34, 35, 51}   # Modalidades de ensino/aprendizagem
CODIGOS_FERIAS = {0}                # Férias


def _norm_polo(value):
    """Normaliza variações do nome da unidade-base para o nome oficial."""
    s = str(value).strip()
    if not s:
        return s
    return POLO_NORM.get(s.upper(), s)


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
        nome_str = str(nome).strip()
        if not any(c.isalpha() for c in nome_str):
            continue
        area_raw = df.iloc[idx, 2]
        area_str = str(area_raw).strip() if pd.notna(area_raw) else ""
        if area_str in ("0", "CARGA HORÁRIA", "CARGA HORARIA", "Carga Horária", "Carga Horaria", "SEM ÁREA"):
            continue
        has_month_data = False
        for m in MONTHS:
            if m in month_cols:
                c = month_cols[m]
                val = df.iloc[idx, c]
                if pd.notna(val):
                    has_month_data = True
                    break
        if not has_month_data:
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
            polo = POLO_JD_LEGACY if "(JD)" in area_upper else POLO_DEFAULT
        polo = _norm_polo(polo)

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


# ===========================================================================
# Leitura de horas "OUTROS" das abas individuais dos instrutores
# ===========================================================================

def _norm_text(s: str) -> str:
    """Normaliza texto: sem acentos, maiúsculo e sem espaços extras."""
    if not isinstance(s, str):
        return ""
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().upper().strip()


def _classify_text_activity(text: str) -> Optional[str]:
    """
    Classifica texto de atividade quando não há código numérico explícito.
    Retorna 'FERIAS', 'OUTROS', ou None.
    """
    n = _norm_text(text)
    if not n:
        return None

    # Férias / Recesso
    if any(k in n for k in ["FERIAS", "0-FERIAS", "RECESSO"]):
        return "FERIAS"

    # Códigos de outros embutidos
    if any(k in n for k in ["1-PLANEJAMENTO", "2-REUNIOES", "3-CAPACITACAO", "4-BANCO DE HORAS", "9-OUTROS"]):
        return "OUTROS"

    # Atividades de Planejamento (evitando disciplinas de cursos que contêm a palavra)
    if any(k in n for k in ["PLANEJAMENTO", "PLANO DE AULA", "PREPARACAO DE AULA"]):
        if not any(course in n for course in ["OP TI", "PINTOR", "TECNICO", "CURSO", "DISCIPLINA", "EDIFICACOES"]):
            return "OUTROS"

    # Reuniões
    if any(k in n for k in ["REUNIAO", "REUNIOES", "MEETING", "CONSELHO DE CLASSE", "ALINHAMENTO"]):
        return "OUTROS"

    # Capacitação / Treinamento docente / Visita técnica
    if any(k in n for k in ["CAPACITACAO DOCENTE", "TREINAMENTO DOCENTE", "CAPACITACAO GEMINY", "CAPACITACAO GEP", "VISITA TECNICA", "VISITA PEDAGOGICA", "WORKSHOP DOCENTE"]):
        return "OUTROS"

    # Banco de horas
    if any(k in n for k in ["BANCO DE HORAS", "COMPENSACAO DE BANCO"]):
        return "OUTROS"

    return None


def _clean_docente_name(name: str) -> str:
    """Remove sufixos de carga horária como '- 15 HORAS SEMANAL' ou ' - CONSTRUÇÃO CIVIL'."""
    if not isinstance(name, str):
        return ""
    cleaned = re.sub(r"[-\s]+\d+\s*H(ORAS)?\s*(SEMANAL)?.*$", "", name, flags=re.IGNORECASE).strip()
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned.upper()


def _extract_codigo_from_modalidade(text: str) -> Optional[int]:
    """
    Extrai o código numérico de uma string de modalidade.
    Exemplos: '2-REUNIÕES' -> 2, '35-TÉCNICO DE NÍVEL MÉDIO' -> 35
    """
    if not isinstance(text, str):
        return None
    m = re.match(r"^\s*(\d+)\s*[-–]", text.strip())
    if m:
        return int(m.group(1))
    return None


def _find_mes_col_in_block_header(row: list) -> Optional[int]:
    """Retorna o índice da coluna com o número do mês (logo após 'MÊS:')."""
    for i, v in enumerate(row):
        if isinstance(v, str) and "M" in v.upper() and "S" in v.upper() and ":" in v:
            for j in range(i + 1, min(i + 5, len(row))):
                cand = row[j]
                if pd.notna(cand) and str(cand).strip() != "":
                    return j
    return None


def _find_ano_in_block_header(row: list) -> Optional[str]:
    """Retorna o ano (string '2026') logo após 'ANO:'."""
    for i, v in enumerate(row):
        if isinstance(v, str) and "ANO" in v.upper() and ":" in v:
            for j in range(i + 1, min(i + 5, len(row))):
                cand = row[j]
                if pd.notna(cand):
                    try:
                        year = int(float(str(cand).strip()))
                        if 2000 <= year <= 2100:
                            return str(year)
                    except (ValueError, TypeError):
                        pass
    return None


def _detect_modalidade_col(
    block_header_row: list,
    df_inst: Optional[pd.DataFrame] = None,
    block_header_row_idx: Optional[int] = None,
    next_block_row: Optional[int] = None,
) -> Optional[int]:
    """
    Detecta a coluna MODALIDADE:
    1. Procura 'MODALIDADE' no cabeçalho do bloco.
    2. Se não encontrar, inspeciona as primeiras 15 linhas de dados procurando células com 'CÓDIGO-TEXTO'.
    """
    for i, v in enumerate(block_header_row):
        if isinstance(v, str) and "MODALIDADE" in v.strip().upper():
            return i

    if df_inst is not None and block_header_row_idx is not None and next_block_row is not None:
        scan_limit = min(block_header_row_idx + 15, next_block_row)
        for r_scan in range(block_header_row_idx + 1, scan_limit):
            for c_scan in range(min(5, df_inst.shape[1])):
                val = df_inst.iloc[r_scan, c_scan]
                if pd.notna(val) and _extract_codigo_from_modalidade(str(val)) is not None:
                    return c_scan

    return None


def _detect_componente_col(block_header_row: list, modalidade_col: Optional[int] = None) -> int:
    """Detecta a coluna COMPONENTE / ATIVIDADE."""
    for i, v in enumerate(block_header_row):
        if isinstance(v, str) and ("COMPONENTE" in v.strip().upper() or "ATIVIDADE" in v.strip().upper()):
            return i
    return 1 if modalidade_col != 1 else 2


def _detect_total_col(block_header_row: list) -> Optional[int]:
    """
    Detecta a coluna de total mensal no header de bloco.
    Aceita: TOTAL MENSAL, Total Mensal, TOTAL MES, TOTAL MÊS, TOTAL (fallback).
    """
    def _n(s):
        return (
            s.upper()
             .replace("\u00ca", "E").replace("\u00c9", "E")
             .replace("\u00e3", "A").replace("\u00c3", "A")
             .replace("\u00e2", "A").replace("\u00c2", "A")
             .replace("\u00e7", "C").replace("\u00c7", "C")
        )
    fallback = None
    for i, v in enumerate(block_header_row):
        if not isinstance(v, str):
            continue
        n = _n(v.strip())
        if "TOTAL" in n and ("MENSAL" in n or "MES" in n):
            return i
        if "TOTAL" in n:
            fallback = i
    return fallback


def _sum_outros_from_block(
    df_inst: pd.DataFrame,
    block_start: int,
    next_block_start: int,
    modalidade_col: Optional[int],
    total_col: Optional[int],
    target_year: Optional[int],
    comp_col: Optional[int] = None,
) -> tuple:
    """
    Varre um bloco mensal e classifica cada linha com horas registradas:
        - Código numérico (0=Férias, 1..9=Outros, demais=Regência)
        - Classificação textual (se não houver código explícito)
    Retorna: (horas_regencia, horas_outros, horas_ferias)
    """
    horas_regencia = 0.0
    horas_outros = 0.0
    horas_ferias = 0.0

    if total_col is None:
        return horas_regencia, horas_outros, horas_ferias

    data_start_row = block_start + 2
    for row_idx in range(data_start_row, next_block_start):
        # Ignora linhas de cabeçalho interno ou totalizadores
        val_ev = str(df_inst.iloc[row_idx, 0]).strip().upper() if df_inst.shape[1] > 0 else ""
        if "TOTAL" in val_ev or "MÊS" in val_ev or "MES" in val_ev:
            continue

        total_val = _to_num(df_inst.iloc[row_idx, total_col]) if total_col < df_inst.shape[1] else None
        if total_val is None or total_val == 0:
            continue

        classified = False

        # 1. Classificação por código numérico na coluna modalidade
        if modalidade_col is not None and modalidade_col < df_inst.shape[1]:
            modalidade_val = df_inst.iloc[row_idx, modalidade_col]
            if pd.notna(modalidade_val):
                modalidade_str = str(modalidade_val).replace("\xa0", " ").strip()
                codigo = _extract_codigo_from_modalidade(modalidade_str)
                if codigo is None:
                    try:
                        codigo = int(float(modalidade_str))
                    except (ValueError, TypeError):
                        pass

                if codigo is not None:
                    if codigo in CODIGOS_FERIAS:
                        horas_ferias += total_val
                    elif codigo in CODIGOS_OUTROS:
                        horas_outros += total_val
                    else:
                        horas_regencia += total_val
                    classified = True

        # 2. Classificação textual de fallback (para abas com texto livre)
        if not classified:
          chk_cols = [comp_col, modalidade_col, 0, 1, 2]
          for c_chk in chk_cols:
              if c_chk is not None and c_chk < df_inst.shape[1]:
                  txt_val = df_inst.iloc[row_idx, c_chk]
                  if pd.notna(txt_val) and isinstance(txt_val, str):
                      cat = _classify_text_activity(txt_val)
                      if cat == "FERIAS":
                          horas_ferias += total_val
                          classified = True
                          break
                      elif cat == "OUTROS":
                          horas_outros += total_val
                          classified = True
                          break

        # 3. Se teve total_val mas não foi Férias nem Outros, contabiliza como regência
        if not classified:
            horas_regencia += total_val

    return horas_regencia, horas_outros, horas_ferias


def load_outros_por_instrutor(
    source,
    target_year: int = 2026,
    skip_sheets: int = 3,
) -> pd.DataFrame:
    """
    Lê todas as abas individuais dos instrutores e extrai as horas de atividades
    'OUTROS' (não-sala-de-aula) e 'FÉRIAS' por mês.
    """
    xl = pd.ExcelFile(source)
    all_sheets = xl.sheet_names
    instructor_sheets = all_sheets[skip_sheets:]

    records = []

    for sheet_name in instructor_sheets:
        try:
            df_inst = pd.read_excel(xl, sheet_name=sheet_name, header=None)
        except Exception:
            continue

        # Nome do docente
        docente_name = None
        for search_row in range(0, min(10, len(df_inst))):
            for col_idx in range(min(6, df_inst.shape[1])):
                cell = df_inst.iloc[search_row, col_idx]
                if isinstance(cell, str) and len(cell.strip()) > 3:
                    text = cell.strip()
                    if any(skip in text.upper() for skip in ("SENAI", "ESCOLA", "DEPARTAMENTO", "REGÊNCIA", "REGENCIA")):
                        continue
                    docente_name = _clean_docente_name(text)
                    break
            if docente_name:
                break

        if not docente_name:
            docente_name = _clean_docente_name(sheet_name)

        # Encontrar blocos mensais do ano de interesse
        block_starts = []
        for i in range(len(df_inst)):
            row_list = df_inst.iloc[i, :].tolist()
            mes_col_idx = _find_mes_col_in_block_header(row_list)
            if mes_col_idx is None:
                continue
            ano_str = _find_ano_in_block_header(row_list)
            if ano_str is None or int(ano_str) != target_year:
                continue
            mes_raw = str(df_inst.iloc[i, mes_col_idx]).strip().lstrip("0") or "0"
            try:
                mes_num = int(float(mes_raw))
            except (ValueError, TypeError):
                continue
            if not (1 <= mes_num <= 12):
                continue
            block_starts.append((i, mes_num))

        if not block_starts:
            continue

        for b_idx, (block_row, mes_num) in enumerate(block_starts):
            next_block_row = block_starts[b_idx + 1][0] if b_idx + 1 < len(block_starts) else len(df_inst)

            header_candidates = range(block_row + 1, min(block_row + 5, next_block_row))
            block_header_row_data = None
            block_header_row_idx = None
            for hc in header_candidates:
                row_data = df_inst.iloc[hc, :].tolist()
                if any(isinstance(v, str) and "EVENTO" in v.upper() for v in row_data):
                    block_header_row_data = row_data
                    block_header_row_idx = hc
                    break

            if block_header_row_data is None:
                continue

            modalidade_col = _detect_modalidade_col(
                block_header_row_data,
                df_inst=df_inst,
                block_header_row_idx=block_header_row_idx,
                next_block_row=next_block_row,
            )
            total_col = _detect_total_col(block_header_row_data)
            comp_col = _detect_componente_col(block_header_row_data, modalidade_col)

            mes_label = MONTH_LABELS[mes_num - 1]

            horas_reg, horas_outros, horas_ferias = _sum_outros_from_block(
                df_inst,
                block_header_row_idx,
                next_block_row,
                modalidade_col,
                total_col,
                target_year,
                comp_col=comp_col,
            )

            records.append({
                "DOCENTE": docente_name,
                "MES": mes_label,
                "MES_NUM": mes_num,
                "HORAS_OUTROS": horas_outros,
                "HORAS_FERIAS": horas_ferias,
                "HORAS_REGENCIA_IND": horas_reg,
                "TEM_MODALIDADE": (modalidade_col is not None) or ((horas_outros + horas_ferias) > 0),
            })

    if not records:
        return pd.DataFrame(columns=[
            "DOCENTE", "MES", "MES_NUM", "HORAS_OUTROS", "HORAS_FERIAS",
            "HORAS_REGENCIA_IND", "TEM_MODALIDADE",
        ])

    result = pd.DataFrame(records)
    result["MES"] = pd.Categorical(result["MES"], categories=MONTH_LABELS, ordered=True)
    return result
