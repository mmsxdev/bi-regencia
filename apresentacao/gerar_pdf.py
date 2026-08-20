# -*- coding: utf-8 -*-
"""
Gera GRAFICOS_BI.pdf — compilacao de todos os graficos para impressao/backup.

Uso:
    python gerar_pdf.py

Requisitos: Pillow
"""
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
GRAF = os.path.join(HERE, "graficos")
OUT = os.path.join(HERE, "GRAFICOS_BI.pdf")

BG = (11, 15, 20)
TEXT = (243, 244, 246)
PAGE_W, PAGE_H = 1754, 1240  # A4 landscape @150dpi

FONT_CANDIDATES = [
    "C:/Windows/Fonts/segoeuib.ttf",
    "C:/Windows/Fonts/arialbd.ttf",
    "C:/Windows/Fonts/arial.ttf",
]


def find_font(size):
    for f in FONT_CANDIDATES:
        if os.path.exists(f):
            try:
                return ImageFont.truetype(f, size)
            except Exception:
                continue
    return ImageFont.load_default()


def page(img, title, dest, append):
    canvas = Image.new("RGB", (PAGE_W, PAGE_H), BG)
    # fit image leaving margins
    m = 90
    avail_w, avail_h = PAGE_W - m * 2, PAGE_H - m * 2 - 90
    ratio = min(avail_w / img.width, avail_h / img.height)
    w = int(img.width * ratio)
    h = int(img.height * ratio)
    x = (PAGE_W - w) // 2
    y = (PAGE_H - h) // 2 + 30
    canvas.paste(img.resize((w, h)), (x, y))
    draw = ImageDraw.Draw(canvas)
    draw.text((90, 30), title, font=find_font(48), fill=TEXT)
    canvas.save(dest, "PDF", resolution=150.0, append=append)


def main():
    items = [
        ("mes_frequencia_line.png", "Regência média por mês (2026)"),
        ("mes_horas_bar.png", "Horas-aula totais por mes"),
        ("distribuicao_hist.png", "Distribuição da regência média"),
        ("area_freq_bar.png", "Regência média por área"),
        ("instrutores_menor.png", "Menores regências (alerta)"),
        ("instrutores_maior.png", "Maiores regências (destaque)"),
        ("ranking_horas.png", "Top 10 horas-aula no ano"),
        ("automotiva_polos.png", "Manutencao automotiva (area unificada) por polo"),
        ("heatmap.png", "Heatmap instrutor x mes (%)"),
    ]
    saved = 0
    for name, title in items:
        p = os.path.join(GRAF, name)
        if not os.path.exists(p):
            continue
        img = Image.open(p).convert("RGB")
        page(img, title, OUT, append=(saved > 0))
        saved += 1
    print("OK", OUT)


if __name__ == "__main__":
    main()