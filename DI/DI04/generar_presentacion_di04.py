from __future__ import annotations

import shutil
import subprocess
import zipfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable
from xml.sax.saxutils import escape

from PIL import Image, ImageChops


BASE_DIR = Path(__file__).resolve().parent
ROOT_DIR = BASE_DIR.parent.parent
TA04_DIR = ROOT_DIR / "TA" / "TA04"
FIGURES_DIR = TA04_DIR / "figuras"
ASSETS_DIR = BASE_DIR / "assets_di04"
OUTPUT_PATH = BASE_DIR / "DI_4_INFO1184_Juan_Munoz.pptx"

EMU_PER_INCH = 914400
SLIDE_W = 12192000
SLIDE_H = 6858000


THEME = {
    "paper": "F7F5F0",
    "white": "FFFFFF",
    "navy": "10233F",
    "ink": "1E2730",
    "muted": "65727F",
    "line": "D9DDD7",
    "teal": "386F6B",
    "gold": "B8875B",
    "rust": "9C5B4A",
    "blue": "2D5D9F",
    "soft_teal": "EAF3F1",
    "soft_blue": "EAF1F8",
    "soft_gold": "FAF1E7",
    "soft_rust": "F7EDEA",
    "soft_gray": "EEF0F2",
}

TEAM = "Vicente Rivera | Juan Munoz | Fernando Valdes"
COURSE = "INFO1184 Inteligencia de Negocios"
SEMESTER = "Semestre I-2026"


def emu(inches: float) -> int:
    return int(round(inches * EMU_PER_INCH))


def xml_text(value: str) -> str:
    return escape(value, {'"': "&quot;", "'": "&apos;"})


def normalize_color(value: str) -> str:
    return value.replace("#", "").upper()


def font_size(points: float) -> int:
    return int(round(points * 100))


def convert_pdf_to_png(source_pdf: Path, target_png: Path) -> None:
    if not source_pdf.exists():
        raise FileNotFoundError(source_pdf)
    target_png.parent.mkdir(parents=True, exist_ok=True)
    output_base = target_png.with_suffix("")
    pdftoppm = shutil.which("pdftoppm")
    if pdftoppm is None:
        raise RuntimeError("No se encontro pdftoppm para convertir figuras PDF a PNG.")
    subprocess.run(
        [pdftoppm, "-png", "-singlefile", "-r", "180", str(source_pdf), str(output_base)],
        check=True,
    )
    trim_png(target_png)


def trim_png(image_path: Path) -> None:
    image = Image.open(image_path).convert("RGBA")
    background = Image.new("RGBA", image.size, (255, 255, 255, 255))
    diff = ImageChops.difference(image, background)
    bbox = diff.getbbox()
    if bbox:
        margin = 20
        left = max(bbox[0] - margin, 0)
        top = max(bbox[1] - margin, 0)
        right = min(bbox[2] + margin, image.size[0])
        bottom = min(bbox[3] + margin, image.size[1])
        image.crop((left, top, right, bottom)).save(image_path)


def prepare_assets() -> dict[str, Path]:
    ASSETS_DIR.mkdir(exist_ok=True)
    assets = {
        "outliers": ASSETS_DIR / "fig01_outliers.png",
        "pca_variance": ASSETS_DIR / "fig02_pca_varianza.png",
        "pca_biplot": ASSETS_DIR / "fig03_pca_biplot.png",
        "prediction": ASSETS_DIR / "fig04_prediccion_crim.png",
    }
    source_map = {
        "outliers": FIGURES_DIR / "fig_02_outliers_boxplot.pdf",
        "pca_variance": FIGURES_DIR / "fig_07_pca_varianza_explicada.pdf",
        "pca_biplot": FIGURES_DIR / "fig_08_pca_biplot_simple.pdf",
        "prediction": FIGURES_DIR / "fig_09_prediccion_crim.pdf",
    }
    for key, target in assets.items():
        convert_pdf_to_png(source_map[key], target)
    return assets


@dataclass
class Relationship:
    rid: str
    rel_type: str
    target: str


@dataclass
class Slide:
    number: int
    shapes: list[str] = field(default_factory=list)
    relationships: list[Relationship] = field(default_factory=list)
    next_shape_id: int = 2
    next_rel_id: int = 2

    def new_shape_id(self) -> int:
        shape_id = self.next_shape_id
        self.next_shape_id += 1
        return shape_id

    def new_relationship(self, rel_type: str, target: str) -> str:
        rid = f"rId{self.next_rel_id}"
        self.next_rel_id += 1
        self.relationships.append(Relationship(rid, rel_type, target))
        return rid

    def add(self, xml: str) -> None:
        self.shapes.append(xml)

    def xml(self) -> str:
        return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:cSld>
    <p:spTree>
      <p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>
      <p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>
      {''.join(self.shapes)}
    </p:spTree>
  </p:cSld>
  <p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>
</p:sld>'''

    def rels_xml(self) -> str:
        rels = [
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout" Target="../slideLayouts/slideLayout1.xml"/>'
        ]
        for relationship in self.relationships:
            rels.append(
                f'<Relationship Id="{relationship.rid}" Type="{relationship.rel_type}" Target="{relationship.target}"/>'
            )
        return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  {''.join(rels)}
</Relationships>'''


def fill_xml(color: str | None) -> str:
    if color is None:
        return "<a:noFill/>"
    return f'<a:solidFill><a:srgbClr val="{normalize_color(color)}"/></a:solidFill>'


def line_xml(color: str | None = None, width_pt: float = 0.8) -> str:
    if color is None:
        return "<a:ln><a:noFill/></a:ln>"
    width = int(round(width_pt * 12700))
    return f'<a:ln w="{width}"><a:solidFill><a:srgbClr val="{normalize_color(color)}"/></a:solidFill></a:ln>'


def shape_properties(x: float, y: float, w: float, h: float, fill: str | None, line: str | None, geom: str = "rect") -> str:
    return f'''
      <p:spPr>
        <a:xfrm><a:off x="{emu(x)}" y="{emu(y)}"/><a:ext cx="{emu(w)}" cy="{emu(h)}"/></a:xfrm>
        <a:prstGeom prst="{geom}"><a:avLst/></a:prstGeom>
        {fill_xml(fill)}
        {line_xml(line)}
      </p:spPr>'''


def text_runs(text: str, size: float, color: str, bold: bool, font: str) -> str:
    b_attr = ' b="1"' if bold else ""
    return f'''<a:r><a:rPr lang="es-CL" sz="{font_size(size)}"{b_attr}>
      <a:solidFill><a:srgbClr val="{normalize_color(color)}"/></a:solidFill>
      <a:latin typeface="{xml_text(font)}"/><a:ea typeface="{xml_text(font)}"/><a:cs typeface="{xml_text(font)}"/>
    </a:rPr><a:t>{xml_text(text)}</a:t></a:r>'''


def paragraph_xml(text: str, size: float, color: str, bold: bool, align: str, font: str, space_after: int = 4) -> str:
    return f'''<a:p><a:pPr algn="{align}"><a:spcAft><a:spcPts val="{space_after * 100}"/></a:spcAft></a:pPr>{text_runs(text, size, color, bold, font)}<a:endParaRPr lang="es-CL" sz="{font_size(size)}"/></a:p>'''


def add_text_box(
    slide: Slide,
    x: float,
    y: float,
    w: float,
    h: float,
    paragraphs: str | Iterable[str],
    *,
    size: float = 18,
    color: str = THEME["ink"],
    bold: bool = False,
    align: str = "l",
    fill: str | None = None,
    line: str | None = None,
    radius: bool = False,
    font: str = "Aptos",
    margin: float = 0.08,
    anchor: str = "t",
) -> None:
    shape_id = slide.new_shape_id()
    if isinstance(paragraphs, str):
        items = paragraphs.split("\n")
    else:
        items = list(paragraphs)
    p_xml = "".join(paragraph_xml(item, size, color, bold, align, font) for item in items)
    geom = "roundRect" if radius else "rect"
    slide.add(f'''
    <p:sp>
      <p:nvSpPr><p:cNvPr id="{shape_id}" name="Text {shape_id}"/><p:cNvSpPr txBox="1"/><p:nvPr/></p:nvSpPr>
      {shape_properties(x, y, w, h, fill, line, geom)}
      <p:txBody><a:bodyPr wrap="square" anchor="{anchor}" lIns="{emu(margin)}" tIns="{emu(margin)}" rIns="{emu(margin)}" bIns="{emu(margin)}"><a:spAutoFit/></a:bodyPr><a:lstStyle/>{p_xml}</p:txBody>
    </p:sp>''')


def add_rect(slide: Slide, x: float, y: float, w: float, h: float, fill: str, line: str | None = None, radius: bool = False) -> None:
    shape_id = slide.new_shape_id()
    geom = "roundRect" if radius else "rect"
    slide.add(f'''
    <p:sp>
      <p:nvSpPr><p:cNvPr id="{shape_id}" name="Shape {shape_id}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
      {shape_properties(x, y, w, h, fill, line, geom)}
    </p:sp>''')


def add_picture(slide: Slide, image_path: Path, x: float, y: float, w: float, h: float, media_name: str) -> None:
    shape_id = slide.new_shape_id()
    rid = slide.new_relationship(
        "http://schemas.openxmlformats.org/officeDocument/2006/relationships/image",
        f"../media/{media_name}",
    )
    slide.add(f'''
    <p:pic>
      <p:nvPicPr><p:cNvPr id="{shape_id}" name="{xml_text(image_path.name)}"/><p:cNvPicPr><a:picLocks noChangeAspect="1"/></p:cNvPicPr><p:nvPr/></p:nvPicPr>
      <p:blipFill><a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></p:blipFill>
      <p:spPr><a:xfrm><a:off x="{emu(x)}" y="{emu(y)}"/><a:ext cx="{emu(w)}" cy="{emu(h)}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr>
    </p:pic>''')


def add_picture_fit(slide: Slide, image_path: Path, x: float, y: float, w: float, h: float, media_name: str) -> None:
    with Image.open(image_path) as image:
        img_w, img_h = image.size
    box_ratio = w / h
    img_ratio = img_w / img_h
    if img_ratio >= box_ratio:
        final_w = w
        final_h = w / img_ratio
        final_x = x
        final_y = y + (h - final_h) / 2
    else:
        final_h = h
        final_w = h * img_ratio
        final_y = y
        final_x = x + (w - final_w) / 2
    add_picture(slide, image_path, final_x, final_y, final_w, final_h, media_name)


def add_footer(slide: Slide, number: int) -> None:
    add_rect(slide, 0.60, 7.02, 12.10, 0.01, THEME["line"])
    add_text_box(slide, 0.60, 7.08, 4.2, 0.22, "DI04 | INFO1184 | PCA Boston", size=8.5, color=THEME["muted"], margin=0)
    add_text_box(slide, 12.20, 7.04, 0.50, 0.25, f"{number:02d}", size=9, color=THEME["muted"], bold=True, align="r", margin=0)


def add_header(slide: Slide, section: str, title: str, number: int) -> None:
    add_rect(slide, 0, 0, 13.333, 7.5, THEME["paper"])
    add_rect(slide, 0, 0, 13.333, 0.08, THEME["navy"])
    add_text_box(slide, 0.62, 0.32, 3.2, 0.26, section.upper(), size=9.5, color=THEME["teal"], bold=True, margin=0)
    add_text_box(slide, 0.62, 0.58, 9.9, 0.54, title, size=25, color=THEME["navy"], bold=True, font="Aptos Display", margin=0)
    add_footer(slide, number)


def add_metric(slide: Slide, x: float, y: float, w: float, label: str, value: str, accent: str, fill: str) -> None:
    add_text_box(slide, x, y, w, 0.92, "", fill=fill, line=THEME["line"], radius=True, margin=0.04)
    add_rect(slide, x, y, 0.08, 0.92, accent, radius=True)
    add_text_box(slide, x + 0.22, y + 0.14, w - 0.32, 0.20, label.upper(), size=8.2, color=THEME["muted"], bold=True, margin=0)
    add_text_box(slide, x + 0.22, y + 0.38, w - 0.32, 0.34, value, size=18, color=THEME["navy"], bold=True, font="Aptos Display", margin=0)


def add_card(slide: Slide, x: float, y: float, w: float, h: float, title: str, body: str, accent: str, fill: str = THEME["white"]) -> None:
    add_text_box(slide, x, y, w, h, "", fill=fill, line=THEME["line"], radius=True, margin=0.06)
    add_rect(slide, x, y, 0.08, h, accent, radius=True)
    add_text_box(slide, x + 0.24, y + 0.16, w - 0.36, 0.28, title, size=12.5, color=THEME["navy"], bold=True, margin=0)
    add_text_box(slide, x + 0.24, y + 0.52, w - 0.36, h - 0.64, body, size=10.4, color=THEME["ink"], margin=0)


def add_caption(slide: Slide, x: float, y: float, w: float, text: str) -> None:
    add_text_box(slide, x, y, w, 0.22, text, size=8.6, color=THEME["muted"], align="ctr", margin=0)


def create_slides(assets: dict[str, Path]) -> tuple[list[Slide], dict[str, Path]]:
    slides: list[Slide] = []
    media_files: dict[str, Path] = {}

    def media_name(path: Path) -> str:
        name = f"image{len(media_files) + 1}{path.suffix.lower()}"
        media_files[name] = path
        return name

    # Slide 1
    s = Slide(1)
    add_rect(s, 0, 0, 13.333, 7.5, THEME["paper"])
    add_rect(s, 0, 0, 0.18, 7.5, THEME["navy"])
    add_text_box(s, 0.72, 0.62, 2.2, 0.34, "DISERTACION 04", size=10.5, color=THEME["teal"], bold=True, margin=0)
    add_text_box(s, 0.72, 1.10, 7.6, 1.35, "Analisis de Componentes Principales\nDataset Boston", size=37, color=THEME["navy"], bold=True, font="Aptos Display", margin=0)
    add_text_box(s, 0.76, 2.62, 6.2, 0.62, "Resolucion TA04 con metodologia CRISP-DM: precio de viviendas, entorno urbano y criminalidad.", size=15, color=THEME["ink"], margin=0)
    add_text_box(s, 0.76, 5.72, 5.6, 0.72, f"{COURSE}\n{SEMESTER}\n{TEAM}", size=11.3, color=THEME["muted"], margin=0)
    add_metric(s, 8.78, 1.08, 3.4, "Datos", "506 x 14", THEME["teal"], THEME["soft_teal"])
    add_metric(s, 8.78, 2.25, 3.4, "PCA", "5 CP = 80,58%", THEME["blue"], THEME["soft_blue"])
    add_metric(s, 8.78, 3.42, 3.4, "Prediccion", "R2 log = 0,8119", THEME["gold"], THEME["soft_gold"])
    add_metric(s, 8.78, 4.59, 3.4, "Calidad", "0 faltantes", THEME["rust"], THEME["soft_rust"])
    slides.append(s)

    # Slide 2
    s = Slide(2)
    add_header(s, "Ruta", "Temario de la disertacion", 2)
    agenda = [
        ("01", "Contexto y problema", "Preguntas del caso Boston."),
        ("02", "Metodo", "CRISP-DM y PCA estandarizado."),
        ("03", "Evidencia", "Exploracion, PCA y modelos."),
        ("04", "Respuestas", "Resolucion de las seis preguntas."),
        ("05", "Cierre", "Discusion, limites y fuentes."),
    ]
    for i, (step, title, body) in enumerate(agenda):
        x = 0.78 + i * 2.45
        add_text_box(s, x, 1.72, 1.02, 1.02, step, size=22, color=THEME["white"], bold=True, align="ctr", fill=THEME["navy"], radius=True, margin=0.12, anchor="mid")
        add_text_box(s, x - 0.32, 3.03, 1.85, 0.40, title, size=13, color=THEME["navy"], bold=True, align="ctr", margin=0)
        add_text_box(s, x - 0.38, 3.48, 1.98, 0.64, body, size=10.5, color=THEME["muted"], align="ctr", margin=0)
        if i < len(agenda) - 1:
            add_rect(s, x + 1.13, 2.22, 1.20, 0.04, THEME["line"])
    add_text_box(s, 1.45, 5.12, 10.45, 0.78, "Objetivo: transformar los datos historicos de Boston en evidencia interpretable para explicar precios de vivienda y evaluar si la criminalidad puede estimarse con componentes principales.", size=16, color=THEME["ink"], align="ctr", margin=0)
    slides.append(s)

    # Slide 3
    s = Slide(3)
    add_header(s, "Problema", "Preguntas de investigacion TA04", 3)
    questions = [
        ("P1", "Valores atipicos", "Detectar outliers en al menos dos variables."),
        ("P2", "Casas mas baratas", "Identificar observaciones con menor MEDV."),
        ("P3", "Tamano y precio", "Medir relacion entre habitaciones y valor."),
        ("P4", "Rio Charles", "Evaluar efecto de CHAS sobre MEDV."),
        ("P5", "Estatus", "Cuantificar impacto de LSTAT."),
        ("P6", "Criminalidad", "Probar prediccion de CRIM."),
    ]
    for idx, (code, title, body) in enumerate(questions):
        col = idx % 3
        row = idx // 3
        x = 0.72 + col * 4.12
        y = 1.62 + row * 1.86
        add_card(s, x, y, 3.58, 1.35, f"{code}  {title}", body, [THEME["teal"], THEME["blue"], THEME["gold"], THEME["rust"], THEME["teal"], THEME["blue"]][idx], THEME["white"])
    add_text_box(s, 1.05, 5.70, 11.2, 0.62, "La problematica combina comprension urbana, relaciones economicas y reduccion de dimensionalidad para responder con evidencia cuantitativa.", size=15, color=THEME["ink"], align="ctr", margin=0)
    slides.append(s)

    # Slide 4
    s = Slide(4)
    add_header(s, "Datos", "Comprension y preparacion", 4)
    add_metric(s, 0.78, 1.52, 2.55, "Observaciones", "506", THEME["teal"], THEME["soft_teal"])
    add_metric(s, 3.62, 1.52, 2.55, "Variables", "14", THEME["blue"], THEME["soft_blue"])
    add_metric(s, 6.46, 1.52, 2.55, "Faltantes", "0", THEME["gold"], THEME["soft_gold"])
    add_metric(s, 9.30, 1.52, 2.55, "Fuente", "MASS::Boston", THEME["rust"], THEME["soft_rust"])
    add_text_box(s, 0.84, 3.05, 5.72, 2.08, "Variables clave\ncrim: criminalidad per capita\nrm: habitaciones promedio\nlstat: menor estatus socioeconomico\nchas: limite con rio Charles\nmedv: valor mediano de vivienda", size=12.2, color=THEME["ink"], fill=THEME["white"], line=THEME["line"], radius=True, margin=0.18)
    add_text_box(s, 7.05, 3.05, 5.15, 2.08, "Preparacion\nRevision de calidad de datos.\nDeteccion IQR de outliers.\nEstandarizacion z-score.\nPCA con prcomp(center=TRUE, scale.=TRUE).\nSplit 70/30 para prediccion de CRIM.", size=12.2, color=THEME["ink"], fill=THEME["white"], line=THEME["line"], radius=True, margin=0.18)
    add_text_box(s, 3.24, 5.78, 6.8, 0.48, "z = (x - media) / desviacion estandar", size=18, color=THEME["navy"], bold=True, align="ctr", fill=THEME["soft_gray"], line=THEME["line"], radius=True, margin=0.08)
    slides.append(s)

    # Slide 5
    s = Slide(5)
    add_header(s, "Metodo", "CRISP-DM + Analisis de Componentes Principales", 5)
    phases = [
        ("1", "Negocio", "Definir preguntas y criterios de exito."),
        ("2", "Datos", "Describir estructura, variables y calidad."),
        ("3", "Preparacion", "Estandarizar y separar objetivo CRIM."),
        ("4", "Modelamiento", "Aplicar PCA y regresion sobre componentes."),
        ("5", "Evaluacion", "Responder preguntas con evidencia."),
    ]
    for i, (num, name, body) in enumerate(phases):
        x = 0.70 + i * 2.48
        add_text_box(s, x, 1.52, 1.02, 0.58, num, size=18, color=THEME["white"], bold=True, align="ctr", fill=THEME["teal"] if i < 3 else THEME["navy"], radius=True, margin=0.07, anchor="mid")
        add_text_box(s, x - 0.28, 2.28, 1.78, 0.34, name, size=12.5, color=THEME["navy"], bold=True, align="ctr", margin=0)
        add_text_box(s, x - 0.44, 2.72, 2.10, 0.85, body, size=10, color=THEME["muted"], align="ctr", margin=0)
    add_text_box(s, 0.92, 4.38, 5.85, 1.36, "PCA reduce variables correlacionadas a componentes ortogonales ordenados por varianza explicada. Esto permite leer patrones urbanos agregados sin revisar cada variable por separado.", size=13.2, color=THEME["ink"], fill=THEME["white"], line=THEME["line"], radius=True, margin=0.16)
    add_text_box(s, 7.28, 4.38, 4.98, 1.36, "Criterio usado\nConservar componentes hasta superar 80% de varianza explicada y evaluar interpretacion de PC1/PC2.", size=13.2, color=THEME["ink"], fill=THEME["soft_blue"], line=THEME["line"], radius=True, margin=0.16)
    slides.append(s)

    # Slide 6
    s = Slide(6)
    add_header(s, "Exploracion", "Hallazgos antes del PCA", 6)
    add_text_box(s, 0.78, 1.38, 4.00, 3.74, "", fill=THEME["white"], line=THEME["line"], radius=True, margin=0.04)
    add_picture_fit(s, assets["outliers"], 0.98, 1.62, 3.60, 2.56, media_name(assets["outliers"]))
    add_caption(s, 0.98, 4.34, 3.60, "Fig. 1. Variables con mas outliers por regla IQR.")
    add_card(s, 5.18, 1.54, 3.32, 1.34, "Outliers", "Destacan black (77), zn (68), crim (66), medv (40) y rm (30).", THEME["rust"], THEME["white"])
    add_card(s, 8.88, 1.54, 3.32, 1.34, "Casas mas baratas", "El dataset no incluye nombres reales; se reportan IDs. Los menores MEDV son ID 399 e ID 406 con valor 5.", THEME["gold"], THEME["white"])
    add_card(s, 5.18, 3.35, 3.32, 1.34, "Lectura", "Los extremos no se eliminan automaticamente; se reportan porque afectan ejes relevantes del PCA.", THEME["blue"], THEME["white"])
    add_card(s, 8.88, 3.35, 3.32, 1.34, "Precaucion", "black se conserva por reproducibilidad historica, pero no se usa para conclusiones sociales sustantivas.", THEME["teal"], THEME["white"])
    slides.append(s)

    # Slide 7
    s = Slide(7)
    add_header(s, "PCA", "Resultados de componentes principales", 7)
    add_text_box(s, 0.78, 1.36, 5.20, 4.20, "", fill=THEME["white"], line=THEME["line"], radius=True, margin=0.04)
    add_picture_fit(s, assets["pca_variance"], 1.02, 1.62, 4.72, 3.12, media_name(assets["pca_variance"]))
    add_caption(s, 1.02, 4.94, 4.72, "Fig. 2. Varianza individual y acumulada por componente.")
    add_metric(s, 6.50, 1.46, 2.62, "PC1", "46,76%", THEME["teal"], THEME["soft_teal"])
    add_metric(s, 9.36, 1.46, 2.62, "PC1-PC5", "80,58%", THEME["blue"], THEME["soft_blue"])
    add_card(s, 6.50, 2.86, 2.62, 1.66, "PC1", "Presion urbana y socioeconomica: indus, nox, tax, lstat y rad; opuesto a medv.", THEME["teal"], THEME["white"])
    add_card(s, 9.36, 2.86, 2.62, 1.66, "PC2", "Eje residencial: medv, rm y chas cargan positivamente.", THEME["blue"], THEME["white"])
    add_text_box(s, 6.70, 5.08, 5.10, 0.60, "Interpretacion central: mayor presion urbana se asocia con menor valor habitacional, mientras PC2 agrupa atributos residenciales favorables.", size=13.2, color=THEME["ink"], align="ctr", margin=0)
    slides.append(s)

    # Slide 8
    s = Slide(8)
    add_header(s, "PCA", "Lectura visual del plano PC1-PC2", 8)
    add_text_box(s, 0.80, 1.34, 6.25, 4.34, "", fill=THEME["white"], line=THEME["line"], radius=True, margin=0.04)
    add_picture_fit(s, assets["pca_biplot"], 1.06, 1.58, 5.74, 3.48, media_name(assets["pca_biplot"]))
    add_caption(s, 1.06, 5.18, 5.74, "Fig. 3. Biplot PCA simplificado para PC1 y PC2.")
    add_card(s, 7.45, 1.50, 4.68, 1.18, "Variables alineadas", "rm, medv y chas aparecen cercanas en PC2: senal residencial positiva.", THEME["blue"], THEME["white"])
    add_card(s, 7.45, 2.98, 4.68, 1.18, "Variables opuestas", "lstat se ubica en direccion contraria al valor habitacional, coherente con su relacion negativa.", THEME["rust"], THEME["white"])
    add_card(s, 7.45, 4.46, 4.68, 1.18, "Aporte del PCA", "Resume relaciones multivariadas y da contexto a las respuestas individuales.", THEME["teal"], THEME["white"])
    slides.append(s)

    # Slide 9
    s = Slide(9)
    add_header(s, "Respuestas", "Determinantes del valor de vivienda", 9)
    add_metric(s, 0.78, 1.50, 3.50, "Tamano de casa", "rm-medv = 0,695", THEME["teal"], THEME["soft_teal"])
    add_metric(s, 4.92, 1.50, 3.50, "Rio Charles", "+6,346 mil USD", THEME["blue"], THEME["soft_blue"])
    add_metric(s, 9.06, 1.50, 3.50, "Estatus", "lstat-medv = -0,738", THEME["rust"], THEME["soft_rust"])
    add_card(s, 0.88, 3.05, 3.42, 1.82, "P3 Tamano", "Cada habitacion promedio adicional se asocia con +9,102 miles de dolares en MEDV (p < 0,001).", THEME["teal"], THEME["white"])
    add_card(s, 4.96, 3.05, 3.42, 1.82, "P4 Charles", "MEDV medio: 28,440 con rio vs 22,094 sin rio; p = 0,00357. CHAS es binaria y solo 35 casos limitan con el rio.", THEME["blue"], THEME["white"])
    add_card(s, 9.04, 3.05, 3.42, 1.82, "P5 Estatus", "Cada punto adicional en LSTAT se asocia con -0,950 miles de dolares en MEDV (p < 0,001).", THEME["rust"], THEME["white"])
    add_text_box(s, 1.52, 5.70, 10.28, 0.48, "En PCA, rm y medv se alinean en PC2; lstat se opone a medv, reforzando los resultados directos.", size=14.8, color=THEME["navy"], bold=True, align="ctr", margin=0)
    slides.append(s)

    # Slide 10
    s = Slide(10)
    add_header(s, "Prediccion", "Criminalidad con componentes principales", 10)
    add_text_box(s, 0.78, 1.34, 5.42, 4.38, "", fill=THEME["white"], line=THEME["line"], radius=True, margin=0.04)
    add_picture_fit(s, assets["prediction"], 1.02, 1.62, 4.92, 3.38, media_name(assets["prediction"]))
    add_caption(s, 1.02, 5.18, 4.92, "Fig. 4. Prediccion de log1p(crim) en conjunto de prueba.")
    add_metric(s, 6.72, 1.46, 2.48, "Entrenamiento", "354", THEME["teal"], THEME["soft_teal"])
    add_metric(s, 9.48, 1.46, 2.48, "Prueba", "152", THEME["blue"], THEME["soft_blue"])
    add_metric(s, 6.72, 2.62, 2.48, "Componentes", "5", THEME["gold"], THEME["soft_gold"])
    add_metric(s, 9.48, 2.62, 2.48, "Varianza", "82,84%", THEME["rust"], THEME["soft_rust"])
    add_card(s, 6.72, 4.05, 5.24, 1.22, "Resultado P6", "El modelo predice log1p(crim) con R2 = 0,8119 y mejora RMSE de 11,85% frente al promedio base.", THEME["navy"], THEME["white"])
    add_text_box(s, 6.96, 5.58, 4.82, 0.44, "Uso academico/exploratorio: no es un modelo listo para despliegue.", size=12.5, color=THEME["muted"], align="ctr", margin=0)
    slides.append(s)

    # Slide 11
    s = Slide(11)
    add_header(s, "Resolucion", "Respuestas integradas", 11)
    answers = [
        ("P1", "Si hay outliers; destacan black, zn y crim."),
        ("P2", "IDs 399 y 406 tienen el menor MEDV = 5."),
        ("P3", "Mas habitaciones se asocian con mayor precio."),
        ("P4", "Limitar con Charles muestra mayor MEDV, con cautela."),
        ("P5", "Mayor LSTAT se asocia con menor valor."),
        ("P6", "La criminalidad puede predecirse razonablemente en escala log."),
    ]
    for idx, (code, answer) in enumerate(answers):
        y = 1.38 + idx * 0.72
        add_text_box(s, 0.88, y, 0.72, 0.42, code, size=12, color=THEME["white"], bold=True, align="ctr", fill=THEME["navy"], radius=True, margin=0.05, anchor="mid")
        add_text_box(s, 1.78, y + 0.03, 9.85, 0.36, answer, size=14, color=THEME["ink"], margin=0)
    add_text_box(s, 1.14, 6.00, 10.96, 0.52, "La resolucion combina evidencia directa y lectura multivariada: PCA no reemplaza las respuestas, las contextualiza.", size=15.2, color=THEME["navy"], bold=True, align="ctr", fill=THEME["soft_gray"], line=THEME["line"], radius=True, margin=0.06)
    slides.append(s)

    # Slide 12
    s = Slide(12)
    add_header(s, "Cierre", "Discusion, limites y fuentes", 12)
    add_card(s, 0.82, 1.44, 3.52, 2.00, "Conclusiones", "PCA sintetiza la estructura urbana; PC1 refleja presion urbana opuesta a MEDV y PC2 resume atributos residenciales favorables.", THEME["teal"], THEME["white"])
    add_card(s, 4.88, 1.44, 3.52, 2.00, "Limites", "Los resultados son asociaciones, no causalidad. El dataset es historico y requiere actualizacion para decisiones reales.", THEME["rust"], THEME["white"])
    add_card(s, 8.94, 1.44, 3.52, 2.00, "Mejoras", "Aplicar validacion cruzada, revisar sesgos y comparar con modelos no lineales antes de un despliegue.", THEME["blue"], THEME["white"])
    sources = "Fuentes\nChapman et al. (2000), CRISP-DM 1.0.\nHarrison y Rubinfeld (1978), Boston housing.\nJolliffe (2002), Principal Component Analysis.\nVenables y Ripley (2002), MASS.\nR Core Team (2024), R Project."
    add_text_box(s, 1.26, 4.34, 10.82, 1.40, sources, size=11.4, color=THEME["ink"], fill=THEME["white"], line=THEME["line"], radius=True, margin=0.16)
    add_text_box(s, 3.34, 6.06, 6.70, 0.42, "Presentacion minimalista de apoyo para video de 3,5 a 4 minutos.", size=13.5, color=THEME["muted"], align="ctr", margin=0)
    slides.append(s)

    return slides, media_files


def relationships_xml(rels: Iterable[Relationship]) -> str:
    body = "".join(
        f'<Relationship Id="{rel.rid}" Type="{rel.rel_type}" Target="{rel.target}"/>' for rel in rels
    )
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">{body}</Relationships>'''


def content_types_xml(slide_count: int) -> str:
    overrides = [
        '<Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>',
        '<Override PartName="/ppt/slideMasters/slideMaster1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml"/>',
        '<Override PartName="/ppt/slideLayouts/slideLayout1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml"/>',
        '<Override PartName="/ppt/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>',
        '<Override PartName="/ppt/presProps.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presProps+xml"/>',
        '<Override PartName="/ppt/viewProps.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.viewProps+xml"/>',
        '<Override PartName="/ppt/tableStyles.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.tableStyles+xml"/>',
        '<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>',
        '<Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>',
    ]
    for idx in range(1, slide_count + 1):
        overrides.append(
            f'<Override PartName="/ppt/slides/slide{idx}.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>'
        )
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Default Extension="png" ContentType="image/png"/>
  {''.join(overrides)}
</Types>'''


def presentation_xml(slide_count: int) -> str:
    slide_ids = "".join(
        f'<p:sldId id="{255 + idx}" r:id="rId{idx + 1}"/>' for idx in range(1, slide_count + 1)
    )
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:presentation xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" saveSubsetFonts="1">
  <p:sldMasterIdLst><p:sldMasterId id="2147483648" r:id="rId1"/></p:sldMasterIdLst>
  <p:sldIdLst>{slide_ids}</p:sldIdLst>
  <p:sldSz cx="{SLIDE_W}" cy="{SLIDE_H}" type="wide"/>
  <p:notesSz cx="6858000" cy="9144000"/>
  <p:defaultTextStyle>
    <a:defPPr><a:defRPr lang="es-CL"><a:latin typeface="Aptos"/></a:defRPr></a:defPPr>
  </p:defaultTextStyle>
</p:presentation>'''


def presentation_rels_xml(slide_count: int) -> str:
    rels = [
        Relationship("rId1", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster", "slideMasters/slideMaster1.xml")
    ]
    for idx in range(1, slide_count + 1):
        rels.append(Relationship(f"rId{idx + 1}", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide", f"slides/slide{idx}.xml"))
    rels.extend(
        [
            Relationship(f"rId{slide_count + 2}", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/presProps", "presProps.xml"),
            Relationship(f"rId{slide_count + 3}", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/viewProps", "viewProps.xml"),
            Relationship(f"rId{slide_count + 4}", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/tableStyles", "tableStyles.xml"),
        ]
    )
    return relationships_xml(rels)


def package_rels_xml() -> str:
    rels = [
        Relationship("rId1", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument", "ppt/presentation.xml"),
        Relationship("rId2", "http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties", "docProps/core.xml"),
        Relationship("rId3", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties", "docProps/app.xml"),
    ]
    return relationships_xml(rels)


def slide_master_xml() -> str:
    return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldMaster xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:cSld><p:bg><p:bgPr><a:solidFill><a:srgbClr val="F7F5F0"/></a:solidFill><a:effectLst/></p:bgPr></p:bg><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr></p:spTree></p:cSld>
  <p:clrMap bg1="lt1" tx1="dk1" bg2="lt2" tx2="dk2" accent1="accent1" accent2="accent2" accent3="accent3" accent4="accent4" accent5="accent5" accent6="accent6" hlink="hlink" folHlink="folHlink"/>
  <p:sldLayoutIdLst><p:sldLayoutId id="2147483649" r:id="rId1"/></p:sldLayoutIdLst>
  <p:txStyles><p:titleStyle/><p:bodyStyle/><p:otherStyle/></p:txStyles>
</p:sldMaster>'''


def slide_master_rels_xml() -> str:
    rels = [
        Relationship("rId1", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout", "../slideLayouts/slideLayout1.xml"),
        Relationship("rId2", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme", "../theme/theme1.xml"),
    ]
    return relationships_xml(rels)


def slide_layout_xml() -> str:
    return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldLayout xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" type="blank" preserve="1">
  <p:cSld name="Blank"><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr></p:spTree></p:cSld>
  <p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>
</p:sldLayout>'''


def slide_layout_rels_xml() -> str:
    rels = [Relationship("rId1", "http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideMaster", "../slideMasters/slideMaster1.xml")]
    return relationships_xml(rels)


def theme_xml() -> str:
    return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<a:theme xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" name="DI04 Minimal">
  <a:themeElements>
    <a:clrScheme name="DI04"><a:dk1><a:srgbClr val="10233F"/></a:dk1><a:lt1><a:srgbClr val="F7F5F0"/></a:lt1><a:dk2><a:srgbClr val="1E2730"/></a:dk2><a:lt2><a:srgbClr val="FFFFFF"/></a:lt2><a:accent1><a:srgbClr val="386F6B"/></a:accent1><a:accent2><a:srgbClr val="2D5D9F"/></a:accent2><a:accent3><a:srgbClr val="B8875B"/></a:accent3><a:accent4><a:srgbClr val="9C5B4A"/></a:accent4><a:accent5><a:srgbClr val="65727F"/></a:accent5><a:accent6><a:srgbClr val="D9DDD7"/></a:accent6><a:hlink><a:srgbClr val="2D5D9F"/></a:hlink><a:folHlink><a:srgbClr val="9C5B4A"/></a:folHlink></a:clrScheme>
    <a:fontScheme name="Aptos"><a:majorFont><a:latin typeface="Aptos Display"/><a:ea typeface=""/><a:cs typeface=""/></a:majorFont><a:minorFont><a:latin typeface="Aptos"/><a:ea typeface=""/><a:cs typeface=""/></a:minorFont></a:fontScheme>
    <a:fmtScheme name="DI04"><a:fillStyleLst><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:fillStyleLst><a:lnStyleLst><a:ln w="9525"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln></a:lnStyleLst><a:effectStyleLst><a:effectStyle><a:effectLst/></a:effectStyle></a:effectStyleLst><a:bgFillStyleLst><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:bgFillStyleLst></a:fmtScheme>
  </a:themeElements>
  <a:objectDefaults/><a:extraClrSchemeLst/>
</a:theme>'''


def app_xml(slide_count: int) -> str:
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">
  <Application>OpenCode</Application><PresentationFormat>On-screen Show (16:9)</PresentationFormat><Slides>{slide_count}</Slides><Notes>0</Notes><HiddenSlides>0</HiddenSlides><MMClips>0</MMClips><ScaleCrop>false</ScaleCrop><Company>Universidad Catolica de Temuco</Company><LinksUpToDate>false</LinksUpToDate><SharedDoc>false</SharedDoc><HyperlinksChanged>false</HyperlinksChanged><AppVersion>16.0000</AppVersion>
</Properties>'''


def core_xml() -> str:
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:dcmitype="http://purl.org/dc/dcmitype/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <dc:title>DI04 - PCA Dataset Boston</dc:title><dc:subject>INFO1184 Inteligencia de Negocios</dc:subject><dc:creator>Vicente Rivera, Juan Munoz, Fernando Valdes</dc:creator><cp:keywords>PCA; CRISP-DM; Boston; INFO1184</cp:keywords><dc:description>Presentacion minimalista profesional basada en TA04.</dc:description><cp:lastModifiedBy>OpenCode</cp:lastModifiedBy><dcterms:created xsi:type="dcterms:W3CDTF">{now}</dcterms:created><dcterms:modified xsi:type="dcterms:W3CDTF">{now}</dcterms:modified>
</cp:coreProperties>'''


def pres_props_xml() -> str:
    return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:presentationPr xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"><p:showPr><p:present/></p:showPr></p:presentationPr>'''


def view_props_xml() -> str:
    return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:viewPr xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"><p:normalViewPr><p:restoredLeft sz="15620"/><p:restoredTop sz="94660"/></p:normalViewPr><p:slideViewPr><p:cSldViewPr><p:cViewPr varScale="1"><p:scale><a:sx n="100" d="100"/><a:sy n="100" d="100"/></p:scale><p:origin x="0" y="0"/></p:cViewPr><p:guideLst/></p:cSldViewPr></p:slideViewPr></p:viewPr>'''


def table_styles_xml() -> str:
    return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<a:tblStyleLst xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" def="{5C22544A-7EE6-4342-B048-85BDC9FD1C3A}"/>'''


def build_pptx(slides: list[Slide], media_files: dict[str, Path]) -> None:
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(OUTPUT_PATH, "w", compression=zipfile.ZIP_DEFLATED) as pptx:
        pptx.writestr("[Content_Types].xml", content_types_xml(len(slides)))
        pptx.writestr("_rels/.rels", package_rels_xml())
        pptx.writestr("docProps/app.xml", app_xml(len(slides)))
        pptx.writestr("docProps/core.xml", core_xml())
        pptx.writestr("ppt/presentation.xml", presentation_xml(len(slides)))
        pptx.writestr("ppt/_rels/presentation.xml.rels", presentation_rels_xml(len(slides)))
        pptx.writestr("ppt/slideMasters/slideMaster1.xml", slide_master_xml())
        pptx.writestr("ppt/slideMasters/_rels/slideMaster1.xml.rels", slide_master_rels_xml())
        pptx.writestr("ppt/slideLayouts/slideLayout1.xml", slide_layout_xml())
        pptx.writestr("ppt/slideLayouts/_rels/slideLayout1.xml.rels", slide_layout_rels_xml())
        pptx.writestr("ppt/theme/theme1.xml", theme_xml())
        pptx.writestr("ppt/presProps.xml", pres_props_xml())
        pptx.writestr("ppt/viewProps.xml", view_props_xml())
        pptx.writestr("ppt/tableStyles.xml", table_styles_xml())
        for slide in slides:
            pptx.writestr(f"ppt/slides/slide{slide.number}.xml", slide.xml())
            pptx.writestr(f"ppt/slides/_rels/slide{slide.number}.xml.rels", slide.rels_xml())
        for name, path in media_files.items():
            pptx.write(path, f"ppt/media/{name}")


def main() -> None:
    assets = prepare_assets()
    slides, media_files = create_slides(assets)
    build_pptx(slides, media_files)
    print(f"Presentacion creada: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
