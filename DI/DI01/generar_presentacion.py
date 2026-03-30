#!/usr/bin/env python3
from __future__ import annotations

import pathlib
import subprocess
import sys
import time

import uno
from com.sun.star.awt import Point, Size
from com.sun.star.beans import PropertyValue


BASE_DIR = pathlib.Path(__file__).resolve().parent
OUTPUT_FILE = BASE_DIR / "Presentacion_Pinguino_de_Humboldt.pptx"
SOCKET_URL = "uno:socket,host=127.0.0.1,port=2002;urp;StarOffice.ComponentContext"
SLIDE_WIDTH = 28000
SLIDE_HEIGHT = 15750

PALETTE = {
    "forest": int("1F4D3E", 16),
    "forest_dark": int("153329", 16),
    "ocean": int("2D6A6A", 16),
    "sage": int("9EB8A7", 16),
    "sage_light": int("DDE8E1", 16),
    "sand": int("E8E0CF", 16),
    "mist": int("F4F6F2", 16),
    "white": int("FFFFFF", 16),
    "ink": int("233033", 16),
    "stone": int("677776", 16),
    "accent": int("88A97C", 16),
}


def mm(value: float) -> int:
    return int(round(value * 100))


def prop(name: str, value) -> PropertyValue:
    item = PropertyValue()
    item.Name = name
    item.Value = value
    return item


def identify_size(path: pathlib.Path) -> tuple[int, int]:
    result = subprocess.run(
        ["identify", "-format", "%w %h", str(path)],
        check=True,
        capture_output=True,
        text=True,
    )
    width, height = result.stdout.strip().split()
    return int(width), int(height)


def connect():
    local_ctx = uno.getComponentContext()
    resolver = local_ctx.ServiceManager.createInstanceWithContext(
        "com.sun.star.bridge.UnoUrlResolver", local_ctx
    )
    return resolver.resolve(SOCKET_URL)


def ensure_office():
    try:
        return connect(), None
    except Exception:
        profile_dir = BASE_DIR / ".lo-profile-auto"
        profile_dir.mkdir(exist_ok=True)
        process = subprocess.Popen(
            [
                "soffice",
                f"-env:UserInstallation={profile_dir.resolve().as_uri()}",
                "--headless",
                "--nologo",
                "--nodefault",
                "--nofirststartwizard",
                "--norestore",
                "--accept=socket,host=127.0.0.1,port=2002;urp;StarOffice.ComponentContext",
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        for _ in range(60):
            time.sleep(0.5)
            try:
                return connect(), process
            except Exception:
                continue
        process.terminate()
        raise RuntimeError("No fue posible iniciar LibreOffice en modo headless.")


def safe_set(obj, name: str, value) -> None:
    try:
        obj.setPropertyValue(name, value)
    except Exception:
        try:
            setattr(obj, name, value)
        except Exception:
            pass


def add_shape(doc, page, service: str, x: int, y: int, width: int, height: int):
    shape = doc.createInstance(service)
    shape.Position = Point(x, y)
    shape.Size = Size(width, height)
    page.add(shape)
    return shape


def add_rect(doc, page, x: int, y: int, width: int, height: int, fill: int, line=None):
    rect = add_shape(doc, page, "com.sun.star.drawing.RectangleShape", x, y, width, height)
    rect.FillStyle = 1
    rect.FillColor = fill
    if line is None:
        rect.LineStyle = 0
    else:
        rect.LineStyle = 1
        rect.LineColor = line
    return rect


def add_text(
    doc,
    page,
    x: int,
    y: int,
    width: int,
    height: int,
    text: str,
    *,
    fill=None,
    line=None,
    font: str = "Liberation Sans",
    size: float = 14.0,
    color: int = PALETTE["ink"],
    bold: bool = False,
    padding: tuple[float, float, float, float] = (4.0, 3.0, 4.0, 3.0),
):
    service = (
        "com.sun.star.drawing.RectangleShape"
        if fill is not None or line is not None
        else "com.sun.star.drawing.TextShape"
    )
    shape = add_shape(doc, page, service, x, y, width, height)
    if fill is None:
        shape.FillStyle = 0
    else:
        shape.FillStyle = 1
        shape.FillColor = fill
    if line is None:
        shape.LineStyle = 0
    else:
        shape.LineStyle = 1
        shape.LineColor = line
    safe_set(shape, "TextAutoGrowHeight", True)
    safe_set(shape, "TextLeftDistance", mm(padding[0]))
    safe_set(shape, "TextUpperDistance", mm(padding[1]))
    safe_set(shape, "TextRightDistance", mm(padding[2]))
    safe_set(shape, "TextLowerDistance", mm(padding[3]))
    shape.String = text
    safe_set(shape, "CharFontName", font)
    safe_set(shape, "CharHeight", float(size))
    safe_set(shape, "CharColor", color)
    safe_set(shape, "ParaAdjust", 0)
    if bold:
        safe_set(shape, "CharWeight", 150.0)
    return shape


def add_label(doc, page, x: int, y: int, width: int, text: str, fill: int, text_color: int):
    add_text(
        doc,
        page,
        x,
        y,
        width,
        mm(10),
        text,
        fill=fill,
        font="Liberation Sans",
        size=10.0,
        color=text_color,
        bold=True,
        padding=(3.0, 2.0, 3.0, 2.0),
    )


def add_card(
    doc,
    page,
    x: int,
    y: int,
    width: int,
    height: int,
    title: str,
    body: str,
    *,
    accent: int,
    fill: int = PALETTE["white"],
    title_color: int = PALETTE["forest"],
    body_color: int = PALETTE["ink"],
    title_size: float = 13.2,
    body_size: float = 11.2,
) -> None:
    add_rect(doc, page, x, y, width, height, fill)
    add_rect(doc, page, x, y, width, mm(4), accent)
    add_text(
        doc,
        page,
        x + mm(3),
        y + mm(6),
        width - mm(6),
        mm(10),
        title,
        font="Liberation Serif",
        size=title_size,
        color=title_color,
        bold=True,
        padding=(0, 0, 0, 0),
    )
    add_text(
        doc,
        page,
        x + mm(3),
        y + mm(14),
        width - mm(6),
        height - mm(17),
        body,
        font="Liberation Sans",
        size=body_size,
        color=body_color,
        padding=(0, 0, 0, 0),
    )


def add_photo(
    doc,
    page,
    image_path: pathlib.Path,
    x: int,
    y: int,
    width: int,
    height: int,
    *,
    frame_fill: int = PALETTE["sage_light"],
    margin_mm: float = 2.5,
) -> None:
    add_rect(doc, page, x, y, width, height, frame_fill)
    margin = mm(margin_mm)
    available_width = width - 2 * margin
    available_height = height - 2 * margin
    img_width, img_height = identify_size(image_path)
    scale = min(available_width / img_width, available_height / img_height)
    fitted_width = int(img_width * scale)
    fitted_height = int(img_height * scale)
    offset_x = x + (width - fitted_width) // 2
    offset_y = y + (height - fitted_height) // 2
    image = add_shape(
        doc,
        page,
        "com.sun.star.drawing.GraphicObjectShape",
        offset_x,
        offset_y,
        fitted_width,
        fitted_height,
    )
    image.GraphicURL = uno.systemPathToFileUrl(str(image_path))
    safe_set(image, "LineStyle", 0)


def add_figure_caption(doc, page, x: int, y: int, width: int, text: str):
    add_text(
        doc,
        page,
        x,
        y,
        width,
        mm(10),
        text,
        font="Liberation Sans",
        size=9.2,
        color=PALETTE["stone"],
        padding=(0, 0, 0, 0),
    )


def add_footer_number(doc, page, number: int) -> None:
    add_text(
        doc,
        page,
        mm(253),
        mm(146.5),
        mm(12),
        mm(6),
        f"{number:02d}",
        font="Liberation Sans",
        size=9.0,
        color=PALETTE["stone"],
        padding=(0, 0, 0, 0),
    )


def setup_content_slide(doc, page, section: str, title: str, number: int) -> None:
    add_rect(doc, page, 0, 0, SLIDE_WIDTH, SLIDE_HEIGHT, PALETTE["mist"])
    add_rect(doc, page, 0, 0, SLIDE_WIDTH, mm(5), PALETTE["forest"])
    add_rect(doc, page, 0, mm(153.5), SLIDE_WIDTH, mm(2), PALETTE["sage"])
    add_text(
        doc,
        page,
        mm(16),
        mm(12),
        mm(150),
        mm(6),
        section.upper(),
        font="Liberation Sans",
        size=9.0,
        color=PALETTE["ocean"],
        bold=True,
        padding=(0, 0, 0, 0),
    )
    add_text(
        doc,
        page,
        mm(16),
        mm(20),
        mm(210),
        mm(12),
        title,
        font="Liberation Serif",
        size=22.0,
        color=PALETTE["forest"],
        bold=True,
        padding=(0, 0, 0, 0),
    )
    add_footer_number(doc, page, number)


def slide_hook(doc, page) -> None:
    add_rect(doc, page, 0, 0, SLIDE_WIDTH, SLIDE_HEIGHT, PALETTE["mist"])
    add_rect(doc, page, 0, 0, mm(108), SLIDE_HEIGHT, PALETTE["forest"])
    add_rect(doc, page, mm(108), 0, mm(5), SLIDE_HEIGHT, PALETTE["sage"])
    add_text(
        doc,
        page,
        mm(16),
        mm(16),
        mm(74),
        mm(8),
        "CASO DE ESTUDIO | ODS 14",
        font="Liberation Sans",
        size=10.0,
        color=PALETTE["sage_light"],
        bold=True,
        padding=(0, 0, 0, 0),
    )
    add_text(
        doc,
        page,
        mm(16),
        mm(32),
        mm(76),
        mm(36),
        "¿Qué nos dice un pingüino cuando el ecosistema costero entra en riesgo?",
        font="Liberation Serif",
        size=25.5,
        color=PALETTE["white"],
        bold=True,
        padding=(0, 0, 0, 0),
    )
    add_text(
        doc,
        page,
        mm(16),
        mm(78),
        mm(78),
        mm(24),
        "Tesis: aplicar CRISP-DM permite traducir amenazas ecológicas y humanas en variables, indicadores y decisiones útiles para la conservación.",
        font="Liberation Sans",
        size=14.0,
        color=PALETTE["sage_light"],
        padding=(0, 0, 0, 0),
    )
    add_text(
        doc,
        page,
        mm(16),
        mm(112),
        mm(78),
        mm(16),
        "ONU / ODS 14:\nconservar y usar sosteniblemente los océanos y recursos marinos.",
        fill=PALETTE["sage"],
        font="Liberation Sans",
        size=11.5,
        color=PALETTE["forest_dark"],
        bold=True,
        padding=(4.0, 2.5, 4.0, 2.0),
    )
    add_photo(
        doc,
        page,
        BASE_DIR / "pinguino3.jpg",
        mm(118),
        mm(18),
        mm(146),
        mm(92),
        frame_fill=PALETTE["sand"],
        margin_mm=2.0,
    )
    add_text(
        doc,
        page,
        mm(118),
        mm(116),
        mm(146),
        mm(16),
        "Dato de contexto oficial: en Chile, el 20º proceso RCE propuso elevar la especie a En Peligro (MMA, 2025-2026).",
        fill=PALETTE["white"],
        font="Liberation Sans",
        size=12.0,
        color=PALETTE["ink"],
        bold=True,
        padding=(4.0, 2.5, 4.0, 2.0),
    )
    add_figure_caption(
        doc,
        page,
        mm(118),
        mm(136),
        mm(146),
        "Fig. 1. Colonia de pingüinos de Humboldt. Fuente: archivo de imagen provisto en el repositorio de la actividad.",
    )


def slide_methodology(doc, page) -> None:
    setup_content_slide(doc, page, "Metodología", "CRISP-DM como marco explícito de trabajo", 2)
    add_text(
        doc,
        page,
        mm(16),
        mm(38),
        mm(200),
        mm(12),
        "La actividad exige trabajar formalmente las tres primeras fases. El resto del ciclo queda fuera de alcance, pero se mantiene visible para dar coherencia metodológica.",
        font="Liberation Sans",
        size=12.0,
        color=PALETTE["stone"],
        padding=(0, 0, 0, 0),
    )
    phases = [
        ("1", "Comprensión del negocio", PALETTE["forest"], PALETTE["white"]),
        ("2", "Comprensión de los datos", PALETTE["ocean"], PALETTE["white"]),
        ("3", "Preparación de los datos", PALETTE["accent"], PALETTE["forest_dark"]),
        ("4", "Modelado", PALETTE["sand"], PALETTE["forest_dark"]),
        ("5", "Evaluación", PALETTE["sand"], PALETTE["forest_dark"]),
        ("6", "Despliegue", PALETTE["sand"], PALETTE["forest_dark"]),
    ]
    x_values = [mm(16), mm(58), mm(100), mm(142), mm(184), mm(226)]
    for x_value, (number, label, fill, text_color) in zip(x_values, phases):
        add_text(
            doc,
            page,
            x_value,
            mm(64),
            mm(36),
            mm(30),
            f"{number}\n{label}",
            fill=fill,
            font="Liberation Sans",
            size=11.5,
            color=text_color,
            bold=True,
            padding=(3.0, 3.0, 3.0, 2.0),
        )
    add_text(
        doc,
        page,
        mm(16),
        mm(112),
        mm(248),
        mm(18),
        "Alcance de esta presentación: problema -> datos -> preparación.\nTransición explícita: cada sección siguiente corresponde a una fase CRISP-DM.",
        fill=PALETTE["forest"],
        font="Liberation Sans",
        size=14.0,
        color=PALETTE["white"],
        bold=True,
        padding=(5.0, 4.0, 5.0, 2.0),
    )


def slide_business(doc, page) -> None:
    setup_content_slide(doc, page, "Fase 1 | Comprensión del negocio", "Problema, contexto ONU y proposición de trabajo", 3)
    add_card(
        doc,
        page,
        mm(16),
        mm(42),
        mm(112),
        mm(26),
        "Problema central",
        "La presión humana y los cambios ambientales deterioran una especie centinela del ecosistema costero.",
        accent=PALETTE["forest"],
    )
    add_card(
        doc,
        page,
        mm(16),
        mm(72),
        mm(112),
        mm(26),
        "Marco ONU",
        "El caso se conecta directamente con el ODS 14: proteger océanos, recursos marinos y ecosistemas costeros.",
        accent=PALETTE["ocean"],
    )
    add_card(
        doc,
        page,
        mm(16),
        mm(102),
        mm(112),
        mm(30),
        "Pregunta y tesis",
        "Pregunta: ¿qué factores explican el deterioro del estado de conservación?\nTesis: un dataset bien diseñado permite priorizar riesgos y acciones.",
        accent=PALETTE["accent"],
        body_size=10.7,
    )
    add_photo(
        doc,
        page,
        BASE_DIR / "Pinguino1.jpg",
        mm(150),
        mm(44),
        mm(70),
        mm(74),
        frame_fill=PALETTE["sand"],
    )
    add_text(
        doc,
        page,
        mm(224),
        mm(44),
        mm(40),
        mm(26),
        "Stakeholders:\nMMA\nCONAF\nSERNAPESCA\nciencia\ncomunidades\nturismo",
        fill=PALETTE["white"],
        font="Liberation Sans",
        size=11.0,
        color=PALETTE["ink"],
        bold=True,
        padding=(3.0, 3.0, 3.0, 2.0),
    )
    add_text(
        doc,
        page,
        mm(224),
        mm(76),
        mm(40),
        mm(28),
        "Salida esperada de la fase:\nuna definición clara del problema analítico y de las decisiones que la evidencia debe apoyar.",
        fill=PALETTE["white"],
        font="Liberation Sans",
        size=10.2,
        color=PALETTE["ink"],
        padding=(3.0, 3.0, 3.0, 2.0),
    )
    add_figure_caption(
        doc,
        page,
        mm(150),
        mm(121),
        mm(114),
        "Fig. 2. Pingüinos de Humboldt adultos. Fuente: archivo de imagen provisto en el repositorio de la actividad.",
    )


def slide_data_understanding(doc, page) -> None:
    setup_content_slide(doc, page, "Fase 2 | Comprensión de los datos", "Qué dataset se necesita y qué variables lo componen", 4)
    add_text(
        doc,
        page,
        mm(16),
        mm(38),
        mm(190),
        mm(12),
        "En esta fase se identifican las fuentes potenciales, las variables relevantes y los indicadores que representarán el estado de la especie.",
        font="Liberation Sans",
        size=12.0,
        color=PALETTE["stone"],
        padding=(0, 0, 0, 0),
    )
    cards = [
        ("Hábitat", "colonias\nubicación\nregión", PALETTE["forest"]),
        ("Reproducción", "nidos activos\nparejas\néxito reproductivo", PALETTE["ocean"]),
        ("Alimentación", "presa dominante\nsardina\nanchoveta", PALETTE["accent"]),
        ("Salud", "parásitos\nenfermedades\ndatos faltantes", PALETTE["sage"]),
        ("Amenazas", "pesca\nbasura\nturismo\nEl Niño", PALETTE["forest_dark"]),
    ]
    x_values = [mm(16), mm(66), mm(116), mm(166), mm(216)]
    for x_value, (title, body, accent) in zip(x_values, cards):
        add_card(
            doc,
            page,
            x_value,
            mm(54),
            mm(46),
            mm(46),
            title,
            body,
            accent=accent,
            body_size=10.5,
        )
    add_text(
        doc,
        page,
        mm(16),
        mm(110),
        mm(118),
        mm(20),
        "Lenguaje técnico de la fase:\ndataset, variables explicativas, variable objetivo, indicadores y calidad de datos.",
        fill=PALETTE["white"],
        font="Liberation Sans",
        size=11.5,
        color=PALETTE["forest_dark"],
        bold=True,
        padding=(4.0, 3.0, 4.0, 2.0),
    )
    add_text(
        doc,
        page,
        mm(146),
        mm(110),
        mm(118),
        mm(20),
        "Transición a la siguiente fase:\nuna vez entendidas las variables, se define cómo estandarizarlas y prepararlas para análisis.",
        fill=PALETTE["forest"],
        font="Liberation Sans",
        size=11.5,
        color=PALETTE["white"],
        bold=True,
        padding=(4.0, 3.0, 4.0, 2.0),
    )


def slide_preparation(doc, page) -> None:
    setup_content_slide(doc, page, "Fase 3 | Preparación de los datos", "Del registro ecológico a un dataset consistente", 5)
    steps = [
        ("1", "Estandarizar", "colonias, regiones y fechas"),
        ("2", "Definir unidad", "dataset tipo colonia + año"),
        ("3", "Crear variables", "nidos activos, dieta, amenazas, ambiente"),
        ("4", "Construir indicadores", "presión humana y calidad del hábitat"),
    ]
    y_value = mm(42)
    for number, title, body in steps:
        add_text(
            doc,
            page,
            mm(16),
            y_value,
            mm(12),
            mm(16),
            number,
            fill=PALETTE["forest"],
            font="Liberation Serif",
            size=18.0,
            color=PALETTE["white"],
            bold=True,
            padding=(3.0, 2.0, 3.0, 2.0),
        )
        add_text(
            doc,
            page,
            mm(31),
            y_value,
            mm(58),
            mm(16),
            f"{title}\n{body}",
            fill=PALETTE["white"],
            font="Liberation Sans",
            size=11.0,
            color=PALETTE["ink"],
            bold=True,
            padding=(4.0, 2.5, 4.0, 2.0),
        )
        y_value += mm(19)
    add_text(
        doc,
        page,
        mm(102),
        mm(42),
        mm(162),
        mm(22),
        "Ejemplo de estructura del dataset",
        fill=PALETTE["sand"],
        font="Liberation Serif",
        size=17.0,
        color=PALETTE["forest_dark"],
        bold=True,
        padding=(5.0, 3.0, 4.0, 2.0),
    )
    add_text(
        doc,
        page,
        mm(102),
        mm(68),
        mm(162),
        mm(32),
        "colonia | año | nidos activos | dieta dominante | amenaza pesca | amenaza basura | indicador presión humana | condición El Niño",
        fill=PALETTE["white"],
        font="Liberation Sans",
        size=12.0,
        color=PALETTE["ink"],
        padding=(5.0, 4.0, 5.0, 3.0),
    )
    add_text(
        doc,
        page,
        mm(102),
        mm(106),
        mm(162),
        mm(20),
        "Criterio técnico clave:\ntratar faltantes en salud y agrupar amenazas para hacer comparables las colonias.",
        fill=PALETTE["forest"],
        font="Liberation Sans",
        size=11.8,
        color=PALETTE["white"],
        bold=True,
        padding=(5.0, 3.0, 5.0, 2.0),
    )


def slide_evidence(doc, page) -> None:
    setup_content_slide(doc, page, "Evidencia y ejemplos", "Datos oficiales y observables concretos del caso", 6)
    add_card(
        doc,
        page,
        mm(16),
        mm(44),
        mm(76),
        mm(36),
        "RCE Chile 2025-2026",
        "La ficha final del 20º proceso clasifica la especie como En Peligro (EN).",
        accent=PALETTE["forest"],
        body_size=11.0,
    )
    add_card(
        doc,
        page,
        mm(102),
        mm(44),
        mm(76),
        mm(36),
        "Dato poblacional",
        "Se reporta una disminución de 50% entre 2017 y 2021 en parejas reproductivas de principales colonias.",
        accent=PALETTE["ocean"],
        body_size=10.7,
    )
    add_card(
        doc,
        page,
        mm(188),
        mm(44),
        mm(76),
        mm(36),
        "Distribución confirmada",
        "En Chile se ha confirmado nidificación en al menos 48 colonias.",
        accent=PALETTE["accent"],
        body_size=11.0,
    )
    add_text(
        doc,
        page,
        mm(16),
        mm(92),
        mm(248),
        mm(18),
        "Amenazas documentadas oficialmente:\npesquerías, disminución del alimento, perturbación humana en colonias y cambio climático.",
        fill=PALETTE["white"],
        font="Liberation Sans",
        size=12.6,
        color=PALETTE["forest_dark"],
        bold=True,
        padding=(4.0, 3.0, 4.0, 2.0),
    )
    add_text(
        doc,
        page,
        mm(16),
        mm(116),
        mm(248),
        mm(18),
        "Ejemplo de indicador analítico:\npresión humana = pesca incidental + basura marina + perturbación turística observada en una colonia.",
        fill=PALETTE["forest"],
        font="Liberation Sans",
        size=12.6,
        color=PALETTE["white"],
        bold=True,
        padding=(4.0, 3.0, 4.0, 2.0),
    )


def slide_analysis(doc, page) -> None:
    setup_content_slide(doc, page, "Salida analítica", "Cómo el dataset responde la pregunta del negocio", 7)
    add_card(
        doc,
        page,
        mm(16),
        mm(46),
        mm(114),
        mm(70),
        "Relaciones a evaluar",
        "• alimento -> reproducción\n"
        "• amenazas -> éxito reproductivo\n"
        "• El Niño -> disponibilidad marina\n"
        "• presión humana -> vulnerabilidad por colonia",
        accent=PALETTE["forest"],
        body_size=12.0,
    )
    add_card(
        doc,
        page,
        mm(148),
        mm(46),
        mm(116),
        mm(70),
        "Decisiones que habilita",
        "• priorizar colonias críticas\n"
        "• orientar monitoreo\n"
        "• justificar medidas de conservación\n"
        "• comunicar riesgos con evidencia",
        accent=PALETTE["ocean"],
        body_size=12.0,
    )
    add_text(
        doc,
        page,
        mm(16),
        mm(124),
        mm(248),
        mm(18),
        "Conclusión metodológica: la presentación no se limita a describir la especie; muestra cómo convertir un problema ambiental en un problema analítico estructurado.",
        fill=PALETTE["forest_dark"],
        font="Liberation Sans",
        size=13.8,
        color=PALETTE["white"],
        bold=True,
        padding=(5.0, 4.0, 5.0, 2.0),
    )


def slide_conclusion(doc, page) -> None:
    add_rect(doc, page, 0, 0, SLIDE_WIDTH, SLIDE_HEIGHT, PALETTE["forest"])
    add_rect(doc, page, 0, mm(153.5), SLIDE_WIDTH, mm(2), PALETTE["sage"])
    add_text(
        doc,
        page,
        mm(16),
        mm(18),
        mm(120),
        mm(8),
        "CIERRE",
        font="Liberation Sans",
        size=9.0,
        color=PALETTE["sage_light"],
        bold=True,
        padding=(0, 0, 0, 0),
    )
    add_text(
        doc,
        page,
        mm(16),
        mm(34),
        mm(122),
        mm(44),
        "El pingüino de Humboldt funciona como indicador del equilibrio entre salud marina y presión humana.",
        font="Liberation Serif",
        size=24.0,
        color=PALETTE["white"],
        bold=True,
        padding=(0, 0, 0, 0),
    )
    add_text(
        doc,
        page,
        mm(16),
        mm(84),
        mm(122),
        mm(18),
        "Por eso, el enfoque CRISP-DM ayuda a ordenar la evidencia y a convertirla en conservación basada en datos.",
        font="Liberation Sans",
        size=13.2,
        color=PALETTE["sage_light"],
        padding=(0, 0, 0, 0),
    )
    add_photo(
        doc,
        page,
        BASE_DIR / "pinguino4.jpg",
        mm(164),
        mm(28),
        mm(100),
        mm(68),
        frame_fill=PALETTE["sand"],
    )
    add_figure_caption(
        doc,
        page,
        mm(164),
        mm(100),
        mm(100),
        "Fig. 3. Pingüinos de Humboldt. Fuente: archivo de imagen provisto en el repositorio de la actividad.",
    )
    takeaways = [
        ("Amenaza prioritaria", "Pesca y pérdida de alimento aparecen como variables críticas."),
        ("Indicador clave", "La reproducción y los nidos activos son el mejor termómetro del sistema."),
        ("Sentido académico", "La presentación cumple fases CRISP-DM y deja una tesis explícita."),
    ]
    x_values = [mm(16), mm(101), mm(186)]
    accents = [PALETTE["sage"], PALETTE["ocean"], PALETTE["accent"]]
    for x_value, accent, (title, body) in zip(x_values, accents, takeaways):
        add_card(
            doc,
            page,
            x_value,
            mm(115),
            mm(78),
            mm(26),
            title,
            body,
            accent=accent,
            fill=PALETTE["white"],
            body_size=10.1,
        )
    add_footer_number(doc, page, 8)


def slide_bibliography(doc, page) -> None:
    setup_content_slide(doc, page, "Bibliografía y fuentes", "Referencias académicas y fuentes oficiales utilizadas", 9)
    references = [
        "1. Naciones Unidas. Goal 14 / Life Below Water. https://sdgs.un.org/goals/goal14",
        "2. Ministerio del Medio Ambiente de Chile (2026). Consejo de Ministros declara al pingüino de Humboldt como Monumento Natural.",
        "3. Ministerio del Medio Ambiente de Chile (2025). Ficha final 20º RCE: Spheniscus humboldti.",
        "4. Ministerio del Medio Ambiente de Chile (2023). Plan RECOGE para proteger al pingüino de Humboldt.",
        "5. CONAF. Reserva Nacional Pingüino de Humboldt.",
        "6. Material visual (Fig. 1-Fig. 3): archivos de imagen provistos en el repositorio de la actividad.",
    ]
    current_y = mm(42)
    for ref in references:
        add_text(
            doc,
            page,
            mm(16),
            current_y,
            mm(248),
            mm(12),
            ref,
            fill=PALETTE["white"],
            font="Liberation Sans",
            size=11.0,
            color=PALETTE["ink"],
            padding=(4.0, 2.8, 4.0, 2.0),
        )
        current_y += mm(16)
    add_text(
        doc,
        page,
        mm(16),
        mm(136),
        mm(248),
        mm(10),
        "Nota: el contexto ONU se integra mediante ODS 14; la actualización de conservación en Chile se apoya en fuentes MMA 2025-2026.",
        font="Liberation Sans",
        size=10.0,
        color=PALETTE["stone"],
        padding=(0, 0, 0, 0),
    )


def build_presentation():
    required_files = [
        BASE_DIR / "Informacion.txt",
        BASE_DIR / "Pinguino1.jpg",
        BASE_DIR / "pinguino2.jpg",
        BASE_DIR / "pinguino3.jpg",
        BASE_DIR / "pinguino4.jpg",
    ]
    missing = [path.name for path in required_files if not path.exists()]
    if missing:
        raise FileNotFoundError(f"Faltan archivos requeridos: {', '.join(missing)}")

    context, office_process = ensure_office()
    doc = None
    try:
        desktop = context.ServiceManager.createInstanceWithContext(
            "com.sun.star.frame.Desktop", context
        )
        doc = desktop.loadComponentFromURL("private:factory/simpress", "_blank", 0, ())
        pages = doc.getDrawPages()
        while pages.getCount() < 9:
            pages.insertNewByIndex(pages.getCount())

        slide_hook(doc, pages.getByIndex(0))
        slide_methodology(doc, pages.getByIndex(1))
        slide_business(doc, pages.getByIndex(2))
        slide_data_understanding(doc, pages.getByIndex(3))
        slide_preparation(doc, pages.getByIndex(4))
        slide_evidence(doc, pages.getByIndex(5))
        slide_analysis(doc, pages.getByIndex(6))
        slide_conclusion(doc, pages.getByIndex(7))
        slide_bibliography(doc, pages.getByIndex(8))

        output_url = uno.systemPathToFileUrl(str(OUTPUT_FILE))
        doc.storeAsURL(output_url, (prop("FilterName", "Impress Office Open XML"),))
    finally:
        if doc is not None:
            try:
                doc.close(True)
            except Exception:
                pass
        if office_process is not None:
            office_process.terminate()
            try:
                office_process.wait(timeout=10)
            except Exception:
                office_process.kill()


def main() -> int:
    try:
        build_presentation()
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    print(f"Presentación creada en: {OUTPUT_FILE}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
