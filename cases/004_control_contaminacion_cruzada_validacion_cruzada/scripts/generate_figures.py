#!/usr/bin/env python3
"""Genera las figuras científicas disponibles del Caso 004.

La figura VLE no se genera mientras no exista un dataset experimental
trazable. De este modo una ausencia de evidencia no se transforma en una curva
aparentemente validada.
"""

from __future__ import annotations

import argparse
import csv
import math
import os
import tempfile
from collections import defaultdict
from collections.abc import Sequence
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, PngImagePlugin

CASE_DIR = Path(__file__).resolve().parents[1]
DEFAULT_SENSITIVITY = (
    CASE_DIR / "data" / "processed" / "hx301_sensitivity_v01.csv"
)
DEFAULT_PROCESS = CASE_DIR / "data" / "process_results_v01.csv"
DEFAULT_EQUIPMENT = (
    CASE_DIR / "data" / "processed" / "hx301_equipment_results_v01.csv"
)
DEFAULT_OUTPUT = CASE_DIR / "assets" / "figures"

STREAM_TAGS = {
    "hot_in": "MSTR-301_CONDENSADO_CALIENTE",
    "cold_in": "MSTR-302_AGUA_FRIA",
    "hot_out": "MSTR-303_CONDENSADO_ENFRIADO",
    "cold_out": "MSTR-304_AGUA_PRECALENTADA",
}
HX_TAG = "HX-301_INTERCAMBIADOR"

INK = "#17212B"
MUTED = "#435363"
GRID = "#D6DEE6"
PAPER = "#F7F9FC"
BLUE = "#176B87"
GREEN = "#357A4B"
ORANGE = "#B85C24"
HOT = "#C75B39"
COLD = "#2878A8"
PALE_HOT = "#F5D8CE"
PALE_COLD = "#D8EAF4"
PALE_GREEN = "#DDEDDD"


def font(size: int, *, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = (
        "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf",
        "arialbd.ttf" if bold else "arial.ttf",
    )
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def centered(
    draw: ImageDraw.ImageDraw,
    xy: tuple[float, float],
    text: str,
    text_font: ImageFont.ImageFont,
    *,
    fill: str = INK,
) -> None:
    box = draw.multiline_textbbox((0, 0), text, font=text_font, align="center")
    width = box[2] - box[0]
    height = box[3] - box[1]
    draw.multiline_text(
        (xy[0] - width / 2, xy[1] - height / 2),
        text,
        font=text_font,
        fill=fill,
        align="center",
        spacing=4,
    )


def arrow(
    draw: ImageDraw.ImageDraw,
    start: tuple[int, int],
    end: tuple[int, int],
    *,
    fill: str,
    width: int = 9,
) -> None:
    draw.line((start, end), fill=fill, width=width)
    x1, y1 = start
    x2, y2 = end
    direction = 1 if x2 >= x1 else -1
    head = 18
    draw.polygon(
        (
            (x2, y2),
            (x2 - direction * head, y2 - 12),
            (x2 - direction * head, y2 + 12),
        ),
        fill=fill,
    )


def instrument(
    draw: ImageDraw.ImageDraw,
    center: tuple[int, int],
    tag: str,
    *,
    connection_y: int,
) -> None:
    x, y = center
    radius = 35
    draw.line((x, connection_y, x, y + radius), fill=MUTED, width=3)
    draw.ellipse(
        (x - radius, y - radius, x + radius, y + radius),
        fill=PAPER,
        outline=INK,
        width=3,
    )
    centered(draw, center, tag, font(18, bold=True))


def save_png(image: Image.Image, path: Path, description: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    info = PngImagePlugin.PngInfo()
    info.add_text("Title", description)
    info.add_text("Source", "PTR Case 004; generated from repository evidence")
    info.add_text("License", "CC-BY-4.0")
    with tempfile.NamedTemporaryFile(
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
        delete=False,
    ) as handle:
        temporary = Path(handle.name)
    try:
        image.save(temporary, format="PNG", pnginfo=info, optimize=True)
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def _float(row: dict[str, str], column: str, *, source: str) -> float:
    try:
        value = float(row[column])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(f"{source}: {column} debe ser numérico.") from exc
    if not math.isfinite(value):
        raise ValueError(f"{source}: {column} debe ser finito.")
    return value


def _read_rows(path: Path, *, source: str) -> list[dict[str, str]]:
    if not path.is_file():
        raise ValueError(f"{source}: no existe {path}.")
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
    if not rows:
        raise ValueError(f"{source}: el CSV no contiene filas.")
    return rows


def load_nominal(
    process_path: Path,
    equipment_path: Path,
) -> dict[str, float]:
    process_rows = _read_rows(process_path, source="corrientes")
    by_id = {row.get("object_id", ""): row for row in process_rows}
    if len(by_id) != len(process_rows):
        raise ValueError("corrientes: object_id debe ser único y no vacío.")
    missing = sorted(set(STREAM_TAGS.values()).difference(by_id))
    if missing:
        raise ValueError(f"corrientes: faltan objetos: {', '.join(missing)}.")

    equipment_rows = _read_rows(equipment_path, source="equipo")
    hx_rows = [row for row in equipment_rows if row.get("object_id") == HX_TAG]
    if len(hx_rows) != 1:
        raise ValueError(f"equipo: se requiere exactamente una fila para {HX_TAG}.")
    hx = hx_rows[0]

    values: dict[str, float] = {}
    for role, object_id in STREAM_TAGS.items():
        row = by_id[object_id]
        values[f"{role}_temperature_K"] = _float(
            row,
            "temperature_K",
            source=object_id,
        )
        values[f"{role}_pressure_Pa"] = _float(
            row,
            "pressure_Pa",
            source=object_id,
        )
        values[f"{role}_mass_flow_kg_s"] = _float(
            row,
            "mass_flow_kg_s",
            source=object_id,
        )

    equipment_columns = {
        "overall_coefficient_W_m2_K": "overall_coefficient_W_m2_K",
        "area_m2": "area_m2",
        "ua_W_K": "ua_W_K",
        "correction_factor": "correction_factor",
        "heat_duty_kW": "heat_duty_kW",
        "lmtd_K": "lmtd_K",
        "pressure_margin_inlet_Pa": (
            "clean_contaminated_pressure_margin_inlet_Pa"
        ),
    }
    for key, column in equipment_columns.items():
        values[key] = _float(hx, column, source=HX_TAG)
    return values


def _decimal(value: float, digits: int) -> str:
    return f"{value:.{digits}f}".replace(".", ",")


def _integer_grouped(value: float) -> str:
    return f"{value:,.0f}".replace(",", " ")


def pressure_interpretation(margin_pa: float) -> str:
    if margin_pa > 0.0:
        return (
            "el signo positivo favorece una fuga hipotética hacia el lado "
            "contaminado"
        )
    if margin_pa < 0.0:
        return (
            "el signo negativo favorecería una fuga hipotética hacia el lado "
            "limpio"
        )
    return "el margen nulo no establece una dirección hidráulica preferente"


def generate_pfd(path: Path, nominal: dict[str, float]) -> None:
    image = Image.new("RGB", (1800, 1050), PAPER)
    draw = ImageDraw.Draw(image)

    centered(
        draw,
        (900, 70),
        "HX-301 — transferencia de calor y margen hidráulico nominal",
        font(40, bold=True),
    )
    centered(
        draw,
        (900, 125),
        "Esquema conceptual de instrumentación; los instrumentos no son objetos simulados",
        font(24),
        fill=MUTED,
    )

    hx_box = (680, 350, 1120, 705)
    draw.rounded_rectangle(
        hx_box, radius=45, fill="#EEF2F5", outline=INK, width=5
    )
    draw.ellipse((750, 395, 1050, 660), fill="#FFFFFF", outline=INK, width=4)
    draw.line((780, 625, 1020, 430), fill=HOT, width=8)
    draw.line((780, 430, 1020, 625), fill=COLD, width=8)
    draw.rounded_rectangle(
        (750, 475, 1050, 620), radius=18, fill="#FFFFFF", outline=GRID, width=2
    )
    centered(draw, (900, 515), "HX-301", font(34, bold=True))
    centered(
        draw,
        (900, 570),
        f"UA = {_integer_grouped(nominal['ua_W_K'])} W/K\n"
        "U = "
        f"{_integer_grouped(nominal['overall_coefficient_W_m2_K'])} W/(m²·K) · "
        f"A = {nominal['area_m2']:g} m² · "
        f"F = {nominal['correction_factor']:g}",
        font(20),
    )

    arrow(draw, (110, 440), (680, 440), fill=HOT)
    arrow(draw, (1120, 440), (1690, 440), fill=HOT)
    arrow(draw, (1690, 615), (1120, 615), fill=COLD)
    arrow(draw, (680, 615), (110, 615), fill=COLD)

    draw.rounded_rectangle(
        (90, 205, 615, 310), radius=22, fill=PALE_HOT, outline=HOT, width=3
    )
    draw.multiline_text(
        (115, 225),
        "MSTR-301 · condensado con trazas de metanol\n"
        f"{_decimal(nominal['hot_in_temperature_K'], 3)} K · "
        f"{nominal['hot_in_pressure_Pa'] / 1000:g} kPa · "
        f"{_decimal(nominal['hot_in_mass_flow_kg_s'], 6)} kg/s",
        font=font(23),
        fill=INK,
        spacing=8,
    )
    draw.rounded_rectangle(
        (1185, 770, 1710, 875), radius=22, fill=PALE_COLD, outline=COLD, width=3
    )
    draw.multiline_text(
        (1210, 790),
        "MSTR-302 · agua limpia\n"
        f"{_decimal(nominal['cold_in_temperature_K'], 3)} K · "
        f"{nominal['cold_in_pressure_Pa'] / 1000:g} kPa · "
        f"{_decimal(nominal['cold_in_mass_flow_kg_s'], 6)} kg/s",
        font=font(23),
        fill=INK,
        spacing=8,
    )

    draw.text(
        (1190, 468),
        "MSTR-303 · "
        f"{_decimal(nominal['hot_out_temperature_K'], 3)} K · "
        f"{nominal['hot_out_pressure_Pa'] / 1000:g} kPa",
        font=font(22),
        fill=INK,
    )
    draw.text(
        (125, 650),
        "MSTR-304 · "
        f"{_decimal(nominal['cold_out_temperature_K'], 3)} K · "
        f"{nominal['cold_out_pressure_Pa'] / 1000:g} kPa",
        font=font(22),
        fill=INK,
    )

    instrument(draw, (285, 370), "FT-301", connection_y=440)
    instrument(draw, (420, 370), "PT-301", connection_y=440)
    instrument(draw, (555, 370), "TT-301", connection_y=440)
    instrument(draw, (1245, 370), "TT-303", connection_y=440)
    instrument(draw, (1245, 685), "TT-302", connection_y=615)
    instrument(draw, (1380, 685), "PT-302", connection_y=615)
    instrument(draw, (1515, 685), "FT-302", connection_y=615)
    instrument(draw, (555, 685), "TT-304", connection_y=615)

    pdt_center = (900, 245)
    draw.line((420, 335, 420, 245, 845, 245), fill=MUTED, width=3)
    draw.line((1380, 650, 1380, 245, 955, 245), fill=MUTED, width=3)
    draw.ellipse((845, 190, 955, 300), fill=PALE_GREEN, outline=INK, width=4)
    centered(draw, pdt_center, "PDT-301", font(21, bold=True))
    centered(
        draw,
        (900, 330),
        "P_limpio − P_contaminado = "
        f"{nominal['pressure_margin_inlet_Pa'] / 1000:+g} kPa",
        font(23, bold=True),
        fill=GREEN,
    )

    draw.rounded_rectangle(
        (90, 915, 1710, 1005), radius=20, fill="#FFF4D6", outline="#9B7A20", width=3
    )
    centered(
        draw,
        (900, 960),
        f"Interpretación: {pressure_interpretation(nominal['pressure_margin_inlet_Pa'])},\n"
        "pero no demuestra integridad, seguridad dinámica ni una capa de protección.",
        font(21, bold=True),
    )
    save_png(
        image,
        path,
        "PFD conceptual instrumentado del HX-301 y margen hidráulico nominal",
    )


def load_sensitivity(path: Path) -> list[dict[str, float | str]]:
    rows = _read_rows(path, source="sensibilidad")
    if len(rows) != 12:
        raise ValueError(f"Se esperaban 12 escenarios y se encontraron {len(rows)}.")
    required = {
        "scenario_id",
        "overall_coefficient_W_m2_K",
        "cold_flow_factor",
        "cold_mass_flow_kg_s",
        "heat_duty_kW",
        "cold_outlet_temperature_K",
        "clean_to_contaminated_deltaP_Pa",
        "energy_balance_relative_percent",
    }
    missing = sorted(required.difference(rows[0]))
    if missing:
        raise ValueError(
            f"sensibilidad: faltan columnas: {', '.join(missing)}."
        )
    parsed: list[dict[str, float | str]] = []
    for row in rows:
        parsed.append(
            {
                "scenario_id": row["scenario_id"],
                "U": _float(
                    row,
                    "overall_coefficient_W_m2_K",
                    source="sensibilidad",
                ),
                "factor": _float(row, "cold_flow_factor", source="sensibilidad"),
                "cold_flow": _float(
                    row,
                    "cold_mass_flow_kg_s",
                    source="sensibilidad",
                ),
                "Q": _float(row, "heat_duty_kW", source="sensibilidad"),
                "Tco": _float(
                    row,
                    "cold_outlet_temperature_K",
                    source="sensibilidad",
                ),
                "dP": _float(
                    row,
                    "clean_to_contaminated_deltaP_Pa",
                    source="sensibilidad",
                ),
                "residual": _float(
                    row,
                    "energy_balance_relative_percent",
                    source="sensibilidad",
                ),
            }
        )
    scenario_ids = [str(row["scenario_id"]) for row in parsed]
    if any(not value.strip() for value in scenario_ids):
        raise ValueError("sensibilidad: scenario_id no puede estar vacío.")
    if len(set(scenario_ids)) != len(scenario_ids):
        raise ValueError("sensibilidad: scenario_id debe ser único.")
    expected_grid = {
        (u, factor)
        for u in (800.0, 1000.0, 1200.0, 1500.0)
        for factor in (0.8, 1.0, 1.2)
    }
    actual_grid = {
        (float(row["U"]), float(row["factor"]))
        for row in parsed
    }
    if actual_grid != expected_grid:
        raise ValueError(
            "sensibilidad: la malla U×factor de caudal no coincide con "
            "{800,1000,1200,1500}×{0.8,1.0,1.2}."
        )
    return parsed


def pressure_margin_summary(rows: list[dict[str, float | str]]) -> str:
    margins_kpa = [float(row["dP"]) / 1000.0 for row in rows]
    minimum = min(margins_kpa)
    maximum = max(margins_kpa)
    if math.isclose(minimum, maximum, rel_tol=0.0, abs_tol=1.0e-9):
        return f"ΔP_limpio−contaminado = {minimum:+g} kPa"
    return (
        "ΔP_limpio−contaminado en "
        f"[{minimum:+g}, {maximum:+g}] kPa"
    )


def generate_sensitivity(
    rows: list[dict[str, float | str]],
    path: Path,
    nominal_values: dict[str, float],
) -> None:
    image = Image.new("RGB", (1800, 1100), "#FFFFFF")
    draw = ImageDraw.Draw(image)

    centered(
        draw,
        (900, 65),
        "Sensibilidad térmica del HX-301: U, caudal frío y deber Q",
        font(40, bold=True),
    )
    centered(
        draw,
        (900, 118),
        "Malla DWSIM Automation3 · "
        f"A = {nominal_values['area_m2']:g} m² · "
        f"F = {nominal_values['correction_factor']:g} · contracorriente",
        font(24),
        fill=MUTED,
    )

    left, top, right, bottom = 180, 190, 1640, 820
    u_ticks = sorted({float(row["U"]) for row in rows})
    q_values = [float(row["Q"]) for row in rows]
    x_padding = max(40.0, (max(u_ticks) - min(u_ticks)) * 0.05)
    x_min, x_max = min(u_ticks) - x_padding, max(u_ticks) + x_padding
    q_padding = max(40.0, (max(q_values) - min(q_values)) * 0.08)
    y_min = math.floor((min(q_values) - q_padding) / 100.0) * 100.0
    y_max = math.ceil((max(q_values) + q_padding) / 100.0) * 100.0
    tick_step = max(20.0, math.ceil((y_max - y_min) / 6.0 / 20.0) * 20.0)

    def x_px(value: float) -> float:
        return left + (value - x_min) / (x_max - x_min) * (right - left)

    def y_px(value: float) -> float:
        return bottom - (value - y_min) / (y_max - y_min) * (bottom - top)

    draw.rectangle((left, top, right, bottom), fill=PAPER, outline=INK, width=3)
    for u in u_ticks:
        x = x_px(u)
        draw.line((x, top, x, bottom), fill=GRID, width=2)
        centered(draw, (x, bottom + 32), f"{u:g}", font(20))
    q_tick = y_min
    while q_tick <= y_max + 1.0e-9:
        y = y_px(q_tick)
        draw.line((left, y, right, y), fill=GRID, width=2)
        draw.text((85, y - 13), f"{q_tick:g}", font=font(19), fill=INK)
        q_tick += tick_step

    centered(
        draw,
        ((left + right) / 2, bottom + 82),
        "Coeficiente global U, W/(m²·K)",
        font(24, bold=True),
    )
    centered(
        draw,
        (42, (top + bottom) / 2),
        "Q, kW",
        font(24, bold=True),
    )

    grouped: dict[float, list[dict[str, float | str]]] = defaultdict(list)
    for row in rows:
        grouped[float(row["factor"])].append(row)
    colors = {0.8: ORANGE, 1.0: BLUE, 1.2: GREEN}
    factor_text = {0.8: "−20 %", 1.0: "nominal", 1.2: "+20 %"}
    styles: dict[float, tuple[str, str]] = {}
    for factor in (0.8, 1.0, 1.2):
        flows = {float(row["cold_flow"]) for row in grouped[factor]}
        if len(flows) != 1:
            raise ValueError(
                f"sensibilidad: factor {factor:g} no tiene un caudal frío único."
            )
        flow = next(iter(flows))
        styles[factor] = (
            colors[factor],
            f"{_decimal(flow, 1)} kg/s ({factor_text[factor]})",
        )
    for factor in (0.8, 1.0, 1.2):
        color, _ = styles[factor]
        points = sorted(grouped[factor], key=lambda row: float(row["U"]))
        coords = [(x_px(float(row["U"])), y_px(float(row["Q"]))) for row in points]
        draw.line(coords, fill=color, width=6)
        for x, y in coords:
            draw.ellipse((x - 9, y - 9, x + 9, y + 9), fill="#FFFFFF", outline=color, width=5)

    draw.rounded_rectangle(
        (215, 205, 625, 365), radius=16, fill="#FFFFFF", outline=GRID, width=2
    )
    for factor in (0.8, 1.0, 1.2):
        color, label = styles[factor]
        legend_y = 235 + (factor - 0.8) / 0.2 * 50
        draw.line((245, legend_y, 320, legend_y), fill=color, width=7)
        draw.text((335, legend_y - 14), label, font=font(21), fill=INK)

    nominal = next(
        row for row in rows if float(row["U"]) == 1000 and float(row["factor"]) == 1
    )
    nx, ny = x_px(1000), y_px(float(nominal["Q"]))
    draw.rounded_rectangle(
        (nx + 30, ny - 95, nx + 385, ny - 15),
        radius=16,
        fill=PALE_COLD,
        outline=BLUE,
        width=3,
    )
    draw.multiline_text(
        (nx + 48, ny - 82),
        f"Nominal {nominal['scenario_id']}\n"
        f"Q = {float(nominal['Q']):.3f} kW",
        font=font(21, bold=True),
        fill=INK,
        spacing=5,
    )
    draw.line((nx + 30, ny - 15, nx + 5, ny - 2), fill=BLUE, width=3)

    max_residual = max(float(row["residual"]) for row in rows)
    draw.rounded_rectangle(
        (120, 885, 1680, 1035), radius=24, fill="#EEF5EC", outline=GREEN, width=3
    )
    draw.multiline_text(
        (155, 910),
        "Lectura ingenieril: aumentar U eleva Q; aumentar el caudal frío también eleva Q,\n"
        "pero distribuye la energía entre más masa y modera su temperatura de salida.\n"
        f"En la malla, {pressure_margin_summary(rows)}; "
        f"máximo residuo energético relativo = {max_residual:.3e} %.",
        font=font(22),
        fill=INK,
        spacing=10,
    )
    save_png(
        image,
        path,
        "Sensibilidad de U y caudal frío sobre el deber térmico del HX-301",
    )


def _same_path(left: Path, right: Path) -> bool:
    if left == right:
        return True
    try:
        return os.path.samefile(left, right)
    except OSError:
        return False


def reject_path_collisions(
    inputs: dict[str, Path],
    outputs: dict[str, Path],
) -> None:
    all_paths = [*inputs.items(), *outputs.items()]
    for left_index, (left_label, left_path) in enumerate(all_paths):
        for right_label, right_path in all_paths[left_index + 1 :]:
            if _same_path(left_path, right_path):
                raise ValueError(
                    f"Las rutas {left_label} y {right_label} colisionan: "
                    f"{left_path}."
                )
    for label, path in inputs.items():
        if path.suffix.lower() != ".csv":
            raise ValueError(f"{label} debe apuntar a un archivo .csv.")


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--process", type=Path, default=DEFAULT_PROCESS)
    parser.add_argument("--equipment", type=Path, default=DEFAULT_EQUIPMENT)
    parser.add_argument("--sensitivity", type=Path, default=DEFAULT_SENSITIVITY)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    inputs = {
        "--process": args.process.expanduser().resolve(),
        "--equipment": args.equipment.expanduser().resolve(),
        "--sensitivity": args.sensitivity.expanduser().resolve(),
    }
    output_dir = args.output_dir.expanduser().resolve()
    outputs = {
        "figura PFD": output_dir / "fig_004_01_pfd_hx301_instrumentado.png",
        "figura sensibilidad": output_dir / "fig_004_02_sensibilidad_u_q.png",
    }
    reject_path_collisions(inputs, outputs)

    nominal = load_nominal(inputs["--process"], inputs["--equipment"])
    sensitivity = load_sensitivity(inputs["--sensitivity"])
    generate_pfd(outputs["figura PFD"], nominal)
    generate_sensitivity(
        sensitivity,
        outputs["figura sensibilidad"],
        nominal,
    )
    print(f"Figuras generadas en: {output_dir}")
    print("Figura VLE no generada: falta evidencia experimental trazable.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
