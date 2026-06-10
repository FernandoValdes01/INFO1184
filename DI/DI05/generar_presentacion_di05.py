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
TA05_DIR = ROOT_DIR / "TA" / "TA05"
FIGURES_DIR = TA05_DIR / "figuras"
ASSETS_DIR = BASE_DIR / "assets_di05"
OUTPUT_PATH = BASE_DIR / "DI_5_INFO1184_Juan_Munoz.pptx"

EMU_PER_INCH = 914400
SLIDE_W = 12192000
SLIDE_H = 6858000


THEME = {
    "paper": "F6F8FA",
    "white": "FFFFFF",
    "navy": "102A43",
    "ink": "243447",
    "muted": "65758B",
    "line": "D9E2EC",
    "teal": "147D64",
    "blue": "2F6FDB",
    "red": "B9413C",
    "gold": "B7791F",
    "soft_teal": "E6F4F1",
    "soft_blue": "E8F1FF",
    "soft_red": "FCEDEA",
    "soft_gold": "FFF5DD",
    "soft_gray": "EDF2F7",
}

TEAM = "Juan Munoz | Vicente Rivera | Fernando Valdes"
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
        margin = 24
        left = max(bbox[0] - margin, 0)
        top = max(bbox[1] - margin, 0)
        right = min(bbox[2] + margin, image.size[0])
        bottom = min(bbox[3] + margin, image.size[1])
        image.crop((left, top, right, bottom)).save(image_path)


def prepare_assets() -> dict[str, Path]:
    ASSETS_DIR.mkdir(exist_ok=True)
    assets = {
        "target": ASSETS_DIR / "fig01_target.png",
        "correlation": ASSETS_DIR / "fig02_correlacion.png",
        "numeric": ASSETS_DIR / "fig03_numericas.png",
        "models": ASSETS_DIR / "fig04_modelos.png",
        "confusion": ASSETS_DIR / "fig05_confusion.png",
        "elbow": ASSETS_DIR / "fig06_elbow.png",
        "clusters": ASSETS_DIR / "fig07_clusters_pca.png",
        "profiles": ASSETS_DIR / "fig08_perfiles_clusters.png",
    }
    source_map = {
        "target": FIGURES_DIR / "fig_01_distribucion_target.pdf",
        "correlation": FIGURES_DIR / "fig_03_matriz_correlacion.pdf",
        "numeric": FIGURES_DIR / "fig_02_variables_numericas_por_target.pdf",
        "models": FIGURES_DIR / "fig_06_comparacion_modelos.pdf",
        "confusion": FIGURES_DIR / "fig_05_matriz_confusion_mejor_modelo.pdf",
        "elbow": FIGURES_DIR / "fig_07_elbow_kmeans.pdf",
        "clusters": FIGURES_DIR / "fig_08_clusters_pca.pdf",
        "profiles": FIGURES_DIR / "fig_09_perfiles_clusters.pdf",
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
    font: str = "Liberation Sans",
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
    add_text_box(slide, 0.60, 7.08, 4.60, 0.22, "DI05 | INFO1184 | Heart Disease", size=8.5, color=THEME["muted"], margin=0)
    add_text_box(slide, 12.20, 7.04, 0.50, 0.25, f"{number:02d}", size=9, color=THEME["muted"], bold=True, align="r", margin=0)


def add_header(slide: Slide, section: str, title: str, number: int) -> None:
    add_rect(slide, 0, 0, 13.333, 7.5, THEME["paper"])
    add_rect(slide, 0, 0, 13.333, 0.08, THEME["navy"])
    add_text_box(slide, 0.62, 0.32, 3.4, 0.26, section.upper(), size=9.5, color=THEME["teal"], bold=True, margin=0)
    add_text_box(slide, 0.62, 0.58, 10.2, 0.54, title, size=25, color=THEME["navy"], bold=True, font="Liberation Sans", margin=0)
    add_footer(slide, number)


def add_metric(slide: Slide, x: float, y: float, w: float, label: str, value: str, accent: str, fill: str) -> None:
    add_text_box(slide, x, y, w, 0.92, "", fill=fill, line=THEME["line"], radius=True, margin=0.04)
    add_rect(slide, x, y, 0.08, 0.92, accent, radius=True)
    add_text_box(slide, x + 0.22, y + 0.14, w - 0.32, 0.20, label.upper(), size=8.2, color=THEME["muted"], bold=True, margin=0)
    add_text_box(slide, x + 0.22, y + 0.38, w - 0.32, 0.34, value, size=18, color=THEME["navy"], bold=True, font="Liberation Sans", margin=0)


def add_card(slide: Slide, x: float, y: float, w: float, h: float, title: str, body: str, accent: str, fill: str = THEME["white"]) -> None:
    add_text_box(slide, x, y, w, h, "", fill=fill, line=THEME["line"], radius=True, margin=0.06)
    add_rect(slide, x, y, 0.08, h, accent, radius=True)
    add_text_box(slide, x + 0.24, y + 0.16, w - 0.36, 0.28, title, size=12.5, color=THEME["navy"], bold=True, margin=0)
    add_text_box(slide, x + 0.24, y + 0.52, w - 0.36, h - 0.64, body, size=10.4, color=THEME["ink"], margin=0)


def add_caption(slide: Slide, x: float, y: float, w: float, text: str) -> None:
    add_text_box(slide, x, y, w, 0.24, text, size=8.4, color=THEME["muted"], align="ctr", margin=0)


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
    add_text_box(s, 0.72, 0.62, 2.2, 0.34, "DISERTACION 05", size=10.5, color=THEME["teal"], bold=True, margin=0)
    add_text_box(s, 0.72, 1.08, 7.65, 1.62, "Analisis de enfermedad cardiaca\nClasificacion y segmentacion", size=31, color=THEME["navy"], bold=True, font="Liberation Sans", margin=0)
    add_text_box(s, 0.76, 2.86, 6.24, 0.68, "Resolucion TA05: datos clinicos, patrones exploratorios, modelos simples y perfiles de pacientes.", size=15, color=THEME["ink"], margin=0)
    add_text_box(s, 0.76, 5.74, 5.7, 0.72, f"{COURSE}\n{SEMESTER}\n{TEAM}", size=11.3, color=THEME["muted"], margin=0)
    add_metric(s, 8.80, 1.02, 3.36, "Dataset", "1025 x 14", THEME["teal"], THEME["soft_teal"])
    add_metric(s, 8.80, 2.20, 3.36, "Depurado", "302 filas", THEME["blue"], THEME["soft_blue"])
    add_metric(s, 8.80, 3.38, 3.36, "Mejor F1", "0,832", THEME["red"], THEME["soft_red"])
    add_metric(s, 8.80, 4.56, 3.36, "Clusters", "k = 2", THEME["gold"], THEME["soft_gold"])
    slides.append(s)

    # Slide 2
    s = Slide(2)
    add_header(s, "Ruta", "Temario de la disertacion", 2)
    agenda = [
        ("01", "Contexto", "Problema y pregunta guia."),
        ("02", "Datos", "Dataset, variables y limpieza."),
        ("03", "Analisis", "Patrones por target."),
        ("04", "Modelos", "Clasificacion y clustering."),
        ("05", "Cierre", "Conclusiones y fuentes."),
    ]
    for i, (step, title, body) in enumerate(agenda):
        x = 0.78 + i * 2.45
        add_text_box(s, x, 1.70, 1.02, 1.02, step, size=22, color=THEME["white"], bold=True, align="ctr", fill=THEME["navy"], radius=True, margin=0.12, anchor="mid")
        add_text_box(s, x - 0.34, 3.02, 1.88, 0.40, title, size=13, color=THEME["navy"], bold=True, align="ctr", margin=0)
        add_text_box(s, x - 0.40, 3.47, 2.02, 0.64, body, size=10.5, color=THEME["muted"], align="ctr", margin=0)
        if i < len(agenda) - 1:
            add_rect(s, x + 1.13, 2.20, 1.20, 0.04, THEME["line"])
    add_text_box(s, 1.36, 5.08, 10.60, 0.90, "Objetivo: transformar registros clinicos en evidencia interpretable para identificar variables asociadas, evaluar modelos de deteccion y describir perfiles exploratorios.", size=15.8, color=THEME["ink"], align="ctr", margin=0)
    slides.append(s)

    # Slide 3
    s = Slide(3)
    add_header(s, "Problema", "Pregunta de investigacion TA05", 3)
    add_text_box(s, 0.86, 1.42, 5.50, 1.80, "Pregunta principal\nQue variables clinicas y demograficas se relacionan mas con la presencia de enfermedad cardiaca en los pacientes del dataset?", size=15.0, color=THEME["ink"], fill=THEME["white"], line=THEME["line"], radius=True, margin=0.18)
    add_text_box(s, 6.92, 1.42, 5.40, 1.80, "Enfoque\nAnalisis academico de inteligencia de negocios: exploracion, visualizacion, clasificacion supervisada y clustering no supervisado.", size=15.0, color=THEME["ink"], fill=THEME["soft_teal"], line=THEME["line"], radius=True, margin=0.18)
    questions = [
        ("Diferencias", "Edad, colesterol, presion y frecuencia maxima por target."),
        ("Asociaciones", "Ranking exploratorio de variables relacionadas con target."),
        ("Prediccion", "Regresion logistica, KNN y arbol de decision."),
        ("Perfiles", "K-Means para segmentar pacientes con variables continuas."),
    ]
    for idx, (title, body) in enumerate(questions):
        x = 0.86 + (idx % 2) * 6.06
        y = 3.72 + (idx // 2) * 1.18
        add_card(s, x, y, 5.40, 0.86, title, body, [THEME["teal"], THEME["blue"], THEME["red"], THEME["gold"]][idx], THEME["white"])
    slides.append(s)

    # Slide 4
    s = Slide(4)
    add_header(s, "Datos", "Dataset elegido: Heart Disease Dataset", 4)
    add_metric(s, 0.78, 1.38, 2.58, "Fuente", "Kaggle", THEME["teal"], THEME["soft_teal"])
    add_metric(s, 3.66, 1.38, 2.58, "Autor", "John Smith", THEME["blue"], THEME["soft_blue"])
    add_metric(s, 6.54, 1.38, 2.58, "Original", "1025 x 14", THEME["gold"], THEME["soft_gold"])
    add_metric(s, 9.42, 1.38, 2.58, "Objetivo", "target", THEME["red"], THEME["soft_red"])
    add_text_box(s, 0.86, 2.86, 5.38, 2.38, "Que contiene\nRegistros clinicos de pacientes con variables demograficas, mediciones cardiovasculares y resultados de pruebas medicas codificadas.\n\nUso en TA05\nAnalizar patrones asociados a presencia de enfermedad cardiaca y evaluar modelos simples.", size=11.8, color=THEME["ink"], fill=THEME["white"], line=THEME["line"], radius=True, margin=0.18)
    add_text_box(s, 6.76, 2.86, 5.48, 2.38, "Variable objetivo\ntarget = 0: no presenta enfermedad cardiaca\ntarget = 1: presenta enfermedad cardiaca\n\nNota\nEl dataset se usa con fines academicos y exploratorios; no constituye diagnostico medico.", size=11.8, color=THEME["ink"], fill=THEME["soft_teal"], line=THEME["line"], radius=True, margin=0.18)
    add_card(s, 0.90, 5.66, 2.64, 0.82, "Demograficas", "age, sex", THEME["teal"], THEME["white"])
    add_card(s, 3.82, 5.66, 3.04, 0.82, "Clinicas", "trestbps, chol, thalach, oldpeak", THEME["blue"], THEME["white"])
    add_card(s, 7.14, 5.66, 3.34, 0.82, "Pruebas codificadas", "cp, fbs, restecg, exang, slope, ca, thal", THEME["gold"], THEME["white"])
    add_card(s, 10.76, 5.66, 1.56, 0.82, "Clase", "target", THEME["red"], THEME["white"])
    slides.append(s)

    # Slide 5
    s = Slide(5)
    add_header(s, "Datos", "Comprension y limpieza", 5)
    add_metric(s, 0.78, 1.40, 2.55, "Original", "1025 filas", THEME["teal"], THEME["soft_teal"])
    add_metric(s, 3.62, 1.40, 2.55, "Variables", "14", THEME["blue"], THEME["soft_blue"])
    add_metric(s, 6.46, 1.40, 2.55, "Faltantes", "0", THEME["gold"], THEME["soft_gold"])
    add_metric(s, 9.30, 1.40, 2.55, "Depurado", "302 filas", THEME["red"], THEME["soft_red"])
    add_text_box(s, 0.86, 2.92, 5.66, 2.08, "Variables principales\nage: edad del paciente\ntrestbps: presion arterial en reposo\nchol: colesterol serico\nthalach: frecuencia cardiaca maxima\ntarget: ausencia/presencia de enfermedad", size=12.1, color=THEME["ink"], fill=THEME["white"], line=THEME["line"], radius=True, margin=0.18)
    add_text_box(s, 6.98, 2.92, 5.36, 2.08, "Decision metodologica\nSe detectaron 723 duplicados exactos. Fueron eliminados para reducir fuga de informacion entre entrenamiento y prueba, evitando metricas artificialmente optimistas.", size=12.3, color=THEME["ink"], fill=THEME["white"], line=THEME["line"], radius=True, margin=0.18)
    add_text_box(s, 2.62, 5.72, 8.10, 0.54, "Tabla 1. Resumen: 70,54% de filas removidas por duplicacion exacta.", size=14, color=THEME["navy"], bold=True, align="ctr", fill=THEME["soft_gray"], line=THEME["line"], radius=True, margin=0.07)
    slides.append(s)

    # Slide 6
    s = Slide(6)
    add_header(s, "Metodo", "Flujo CRISP-DM aplicado", 6)
    phases = [
        ("1", "Problema", "Definir preguntas y alcance no diagnostico."),
        ("2", "Datos", "Revisar tipos, faltantes, duplicados y balance."),
        ("3", "Preparacion", "Eliminar duplicados y escalar cuando corresponde."),
        ("4", "Modelos", "Comparar clasificadores y aplicar K-Means."),
        ("5", "Evaluacion", "Interpretar metricas, limites y evidencia."),
    ]
    for i, (num, name, body) in enumerate(phases):
        x = 0.70 + i * 2.48
        add_text_box(s, x, 1.46, 1.02, 0.58, num, size=18, color=THEME["white"], bold=True, align="ctr", fill=THEME["teal"] if i < 3 else THEME["navy"], radius=True, margin=0.07, anchor="mid")
        add_text_box(s, x - 0.30, 2.24, 1.84, 0.34, name, size=12.5, color=THEME["navy"], bold=True, align="ctr", margin=0)
        add_text_box(s, x - 0.48, 2.68, 2.16, 0.92, body, size=9.8, color=THEME["muted"], align="ctr", margin=0)
    add_text_box(s, 0.92, 4.35, 5.85, 1.36, "Clasificacion supervisada\nSe compararon KNN, regresion logistica y arbol de decision con split estratificado y validacion cruzada de cinco pliegues.", size=13.0, color=THEME["ink"], fill=THEME["white"], line=THEME["line"], radius=True, margin=0.16)
    add_text_box(s, 7.28, 4.35, 4.98, 1.36, "Clustering\nK-Means uso solo variables continuas escaladas; target quedo fuera de la entrada y se uso despues para perfilar.", size=13.0, color=THEME["ink"], fill=THEME["soft_blue"], line=THEME["line"], radius=True, margin=0.16)
    slides.append(s)

    # Slide 7
    s = Slide(7)
    add_header(s, "Exploracion", "Distribucion y patrones por target", 7)
    add_text_box(s, 0.78, 1.34, 5.02, 4.30, "", fill=THEME["white"], line=THEME["line"], radius=True, margin=0.04)
    add_picture_fit(s, assets["target"], 1.08, 1.58, 4.42, 2.72, media_name(assets["target"]))
    add_caption(s, 1.08, 4.56, 4.42, "Fig. 1. Distribucion de target en dataset depurado.")
    add_metric(s, 6.38, 1.46, 2.58, "Sin enfermedad", "138", THEME["blue"], THEME["soft_blue"])
    add_metric(s, 9.30, 1.46, 2.58, "Con enfermedad", "164", THEME["teal"], THEME["soft_teal"])
    add_card(s, 6.38, 2.86, 2.58, 1.48, "Balance", "La proporcion target=1 es 0,543; no hay desbalance extremo.", THEME["teal"], THEME["white"])
    add_card(s, 9.30, 2.86, 2.58, 1.48, "Lectura", "Las comparaciones se interpretan como senales exploratorias, no diagnostico.", THEME["red"], THEME["white"])
    add_text_box(s, 6.72, 5.02, 4.82, 0.62, "El dataset permite comparar grupos y construir indicadores interpretables para BI en salud.", size=13.2, color=THEME["navy"], bold=True, align="ctr", margin=0)
    slides.append(s)

    # Slide 8
    s = Slide(8)
    add_header(s, "Exploracion", "Variables mas asociadas con target", 8)
    add_text_box(s, 0.78, 1.30, 5.58, 4.60, "", fill=THEME["white"], line=THEME["line"], radius=True, margin=0.04)
    add_picture_fit(s, assets["correlation"], 0.98, 1.52, 5.18, 3.86, media_name(assets["correlation"]))
    add_caption(s, 0.98, 5.52, 5.18, "Fig. 2. Matriz de correlacion de variables del dataset.")
    signals = [
        ("exang", "r = -0,436", THEME["red"]),
        ("cp", "r = 0,432", THEME["teal"]),
        ("oldpeak", "r = -0,429", THEME["red"]),
        ("thalach", "r = 0,420", THEME["teal"]),
        ("ca", "r = -0,409", THEME["blue"]),
    ]
    for i, (var, value, color) in enumerate(signals):
        y = 1.38 + i * 0.76
        add_text_box(s, 6.86, y, 1.28, 0.42, var, size=12.5, color=THEME["white"], bold=True, align="ctr", fill=color, radius=True, margin=0.05, anchor="mid")
        add_text_box(s, 8.34, y + 0.03, 2.36, 0.36, value, size=14.2, color=THEME["navy"], bold=True, margin=0)
    add_text_box(s, 6.88, 5.44, 4.92, 0.62, "Variables categoricas codificadas: la correlacion se lee como asociacion numerica exploratoria.", size=12.5, color=THEME["muted"], align="ctr", margin=0)
    slides.append(s)

    # Slide 9
    s = Slide(9)
    add_header(s, "Clasificacion", "Comparacion de modelos", 9)
    add_text_box(s, 0.78, 1.34, 5.28, 4.30, "", fill=THEME["white"], line=THEME["line"], radius=True, margin=0.04)
    add_picture_fit(s, assets["models"], 1.06, 1.58, 4.72, 3.28, media_name(assets["models"]))
    add_caption(s, 1.06, 5.08, 4.72, "Fig. 3. Comparacion visual de metricas de clasificacion.")
    add_metric(s, 6.62, 1.46, 2.68, "KNN k=9", "F1 0,832", THEME["teal"], THEME["soft_teal"])
    add_metric(s, 9.56, 1.46, 2.68, "Logistica", "F1 0,828", THEME["blue"], THEME["soft_blue"])
    add_metric(s, 6.62, 2.66, 2.68, "Arbol", "F1 0,814", THEME["gold"], THEME["soft_gold"])
    add_metric(s, 9.56, 2.66, 2.68, "Recall KNN", "0,902", THEME["red"], THEME["soft_red"])
    add_card(s, 6.62, 4.16, 5.62, 1.22, "Resultado", "KNN obtuvo el mejor F1 en el split final; validacion cruzada muestra desempenos muy cercanos entre KNN y regresion logistica.", THEME["navy"], THEME["white"])
    slides.append(s)

    # Slide 10
    s = Slide(10)
    add_header(s, "Clasificacion", "Matriz de confusion del mejor modelo", 10)
    add_text_box(s, 0.78, 1.34, 5.42, 4.34, "", fill=THEME["white"], line=THEME["line"], radius=True, margin=0.04)
    add_picture_fit(s, assets["confusion"], 1.18, 1.62, 4.62, 3.36, media_name(assets["confusion"]))
    add_caption(s, 1.18, 5.18, 4.62, "Fig. 4. Matriz de confusion para KNN k=9.")
    add_metric(s, 6.72, 1.46, 2.48, "VN", "24", THEME["blue"], THEME["soft_blue"])
    add_metric(s, 9.48, 1.46, 2.48, "VP", "37", THEME["teal"], THEME["soft_teal"])
    add_metric(s, 6.72, 2.62, 2.48, "FP", "11", THEME["gold"], THEME["soft_gold"])
    add_metric(s, 9.48, 2.62, 2.48, "FN", "4", THEME["red"], THEME["soft_red"])
    add_card(s, 6.72, 4.06, 5.24, 1.32, "Interpretacion", "El modelo detecta la mayoria de casos target=1, pero no reemplaza juicio clinico. Su utilidad es academica y exploratoria.", THEME["navy"], THEME["white"])
    slides.append(s)

    # Slide 11
    s = Slide(11)
    add_header(s, "Clustering", "Segmentacion exploratoria con K-Means", 11)
    add_text_box(s, 0.78, 1.30, 4.04, 4.42, "", fill=THEME["white"], line=THEME["line"], radius=True, margin=0.04)
    add_picture_fit(s, assets["elbow"], 0.98, 1.56, 3.64, 3.36, media_name(assets["elbow"]))
    add_caption(s, 0.98, 5.12, 3.64, "Fig. 5. Codo y silueta para seleccion de k.")
    add_text_box(s, 4.98, 1.30, 3.36, 4.42, "", fill=THEME["white"], line=THEME["line"], radius=True, margin=0.04)
    add_picture_fit(s, assets["clusters"], 5.18, 1.56, 2.96, 3.36, media_name(assets["clusters"]))
    add_caption(s, 5.18, 5.12, 2.96, "Fig. 6. Proyeccion PCA de clusters.")
    add_metric(s, 8.78, 1.42, 2.86, "Mejor k", "2", THEME["teal"], THEME["soft_teal"])
    add_metric(s, 8.78, 2.60, 2.86, "Silueta", "0,240", THEME["red"], THEME["soft_red"])
    add_card(s, 8.78, 4.02, 2.86, 1.26, "Lectura", "Los grupos ayudan a perfilar pacientes, pero la separacion es limitada.", THEME["gold"], THEME["white"])
    slides.append(s)

    # Slide 12
    s = Slide(12)
    add_header(s, "Perfiles", "Resultados de clusters y conclusiones", 12)
    add_text_box(s, 0.78, 1.30, 4.70, 4.42, "", fill=THEME["white"], line=THEME["line"], radius=True, margin=0.04)
    add_picture_fit(s, assets["profiles"], 1.04, 1.58, 4.18, 3.26, media_name(assets["profiles"]))
    add_caption(s, 1.04, 5.10, 4.18, "Fig. 7. Perfiles relativos de clusters.")
    add_card(s, 5.96, 1.42, 3.00, 1.60, "Cluster 0", "n=173; target=1 promedio 0,717; edad media 49,6; thalach media 161,5; oldpeak 0,52.", THEME["teal"], THEME["white"])
    add_card(s, 9.28, 1.42, 3.00, 1.60, "Cluster 1", "n=129; target=1 promedio 0,310; edad media 60,9; thalach media 133,6; oldpeak 1,75.", THEME["blue"], THEME["white"])
    add_text_box(s, 5.96, 3.58, 6.32, 1.46, "Conclusion integrada\nLos datos permiten identificar senales asociadas y modelos base reproducibles, pero las conclusiones son exploratorias por duplicados, tamano final reducido y codificacion de variables.", size=13.0, color=THEME["ink"], fill=THEME["soft_gray"], line=THEME["line"], radius=True, margin=0.16)
    slides.append(s)

    # Slide 13
    s = Slide(13)
    add_header(s, "Cierre", "Bibliografia y fuentes de apoyo", 13)
    add_card(s, 0.82, 1.42, 3.52, 1.86, "Conclusiones", "Variables como exang, cp, oldpeak, thalach y ca destacan como senales exploratorias asociadas a target.", THEME["teal"], THEME["white"])
    add_card(s, 4.88, 1.42, 3.52, 1.86, "Modelos", "KNN k=9 logro F1=0,832; regresion logistica fue muy cercana en validacion cruzada.", THEME["blue"], THEME["white"])
    add_card(s, 8.94, 1.42, 3.52, 1.86, "Limites", "No constituye diagnostico medico; requiere mas datos y validacion externa para uso real.", THEME["red"], THEME["white"])
    sources = "Fuentes\nSmith (2026), Heart Disease Dataset, Kaggle.\nChapman et al. (2000), CRISP-DM 1.0.\nJames et al. (2021), Introduction to Statistical Learning.\nHosmer et al. (2013), Applied Logistic Regression.\nPedregosa et al. (2011), scikit-learn.\nLevano (2026), material de clases INFO1184."
    add_text_box(s, 1.26, 4.00, 10.82, 2.06, sources, size=9.8, color=THEME["ink"], fill=THEME["white"], line=THEME["line"], radius=True, margin=0.14)
    add_text_box(s, 3.34, 6.28, 6.70, 0.42, "Presentacion de apoyo para video de 3,5 a 4 minutos.", size=13.0, color=THEME["muted"], align="ctr", margin=0)
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
    <a:defPPr><a:defRPr lang="es-CL"><a:latin typeface="Liberation Sans"/></a:defRPr></a:defPPr>
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
  <p:cSld><p:bg><p:bgPr><a:solidFill><a:srgbClr val="F6F8FA"/></a:solidFill><a:effectLst/></p:bgPr></p:bg><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr></p:spTree></p:cSld>
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
<a:theme xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" name="DI05 Minimal Health">
  <a:themeElements>
    <a:clrScheme name="DI05"><a:dk1><a:srgbClr val="102A43"/></a:dk1><a:lt1><a:srgbClr val="F6F8FA"/></a:lt1><a:dk2><a:srgbClr val="243447"/></a:dk2><a:lt2><a:srgbClr val="FFFFFF"/></a:lt2><a:accent1><a:srgbClr val="147D64"/></a:accent1><a:accent2><a:srgbClr val="2F6FDB"/></a:accent2><a:accent3><a:srgbClr val="B9413C"/></a:accent3><a:accent4><a:srgbClr val="B7791F"/></a:accent4><a:accent5><a:srgbClr val="65758B"/></a:accent5><a:accent6><a:srgbClr val="D9E2EC"/></a:accent6><a:hlink><a:srgbClr val="2F6FDB"/></a:hlink><a:folHlink><a:srgbClr val="B9413C"/></a:folHlink></a:clrScheme>
    <a:fontScheme name="Liberation Sans"><a:majorFont><a:latin typeface="Liberation Sans"/><a:ea typeface=""/><a:cs typeface=""/></a:majorFont><a:minorFont><a:latin typeface="Liberation Sans"/><a:ea typeface=""/><a:cs typeface=""/></a:minorFont></a:fontScheme>
    <a:fmtScheme name="DI05"><a:fillStyleLst><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:fillStyleLst><a:lnStyleLst><a:ln w="9525"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln></a:lnStyleLst><a:effectStyleLst><a:effectStyle><a:effectLst/></a:effectStyle></a:effectStyleLst><a:bgFillStyleLst><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:bgFillStyleLst></a:fmtScheme>
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
  <dc:title>DI05 - Heart Disease TA05</dc:title><dc:subject>INFO1184 Inteligencia de Negocios</dc:subject><dc:creator>Juan Munoz, Vicente Rivera, Fernando Valdes</dc:creator><cp:keywords>Heart Disease; Clasificacion; K-Means; CRISP-DM; INFO1184</cp:keywords><dc:description>Presentacion profesional basada en TA05.</dc:description><cp:lastModifiedBy>OpenCode</cp:lastModifiedBy><dcterms:created xsi:type="dcterms:W3CDTF">{now}</dcterms:created><dcterms:modified xsi:type="dcterms:W3CDTF">{now}</dcterms:modified>
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
