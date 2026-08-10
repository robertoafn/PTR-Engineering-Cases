#!/usr/bin/env python3
"""Extrae el estado guardado del flowsheet DWSIM del Caso 004.

Este lector no ejecuta el solver ni modifica el archivo dwxmz. Su objetivo es
materializar de forma reproducible la evidencia ya serializada. La ejecución
Automation3 se mantiene separada para no confundir estado guardado con API.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import zipfile
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

CASE_DIR = Path(__file__).resolve().parents[1]
DEFAULT_SIMULATION = (
    CASE_DIR
    / "simulations"
    / "dwsim"
    / "004_control_contaminacion_cruzada_validacion_cruzada.dwxmz"
)
DEFAULT_PROCESS_OUTPUT = CASE_DIR / "data" / "process_results_v01.csv"
DEFAULT_EQUIPMENT_OUTPUT = (
    CASE_DIR / "data" / "processed" / "hx301_equipment_results_v01.csv"
)

STREAM_TAGS = (
    "MSTR-301_CONDENSADO_CALIENTE",
    "MSTR-302_AGUA_FRIA",
    "MSTR-303_CONDENSADO_ENFRIADO",
    "MSTR-304_AGUA_PRECALENTADA",
)
HX_TAG = "HX-301_INTERCAMBIADOR"

PROCESS_COLUMNS = (
    "object_id",
    "object_type",
    "temperature_K",
    "pressure_Pa",
    "mass_flow_kg_s",
    "molar_flow_mol_s",
    "volumetric_flow_m3_s",
    "density_kg_m3",
    "vapor_molar_fraction",
    "vapor_mass_fraction",
    "specific_enthalpy_kJ_kg",
    "methanol_mass_fraction",
    "methanol_mass_flow_kg_s",
    "energy_flow_kW",
)

EQUIPMENT_COLUMNS = (
    "object_id",
    "object_type",
    "calculation_mode",
    "flow_arrangement",
    "overall_coefficient_W_m2_K",
    "area_m2",
    "ua_W_K",
    "correction_factor",
    "heat_duty_kW",
    "lmtd_K",
    "hot_inlet_temperature_K",
    "hot_outlet_temperature_K",
    "cold_inlet_temperature_K",
    "cold_outlet_temperature_K",
    "hot_inlet_pressure_Pa",
    "hot_outlet_pressure_Pa",
    "cold_inlet_pressure_Pa",
    "cold_outlet_pressure_Pa",
    "hot_side_pressure_drop_Pa",
    "cold_side_pressure_drop_Pa",
    "clean_contaminated_pressure_margin_inlet_Pa",
    "clean_contaminated_pressure_margin_outlet_Pa",
    "use_shell_and_tube_geometry",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def reject_path_collisions(
    simulation: Path,
    process_output: Path,
    equipment_output: Path,
) -> None:
    """Valida identidades resueltas antes de abrir cualquier salida."""
    collisions: Mapping[tuple[str, str], tuple[Path, Path]] = {
        ("--simulation", "--process-output"): (simulation, process_output),
        ("--simulation", "--equipment-output"): (simulation, equipment_output),
        ("--process-output", "--equipment-output"): (
            process_output,
            equipment_output,
        ),
    }
    for labels, paths in collisions.items():
        if paths[0] == paths[1]:
            raise ValueError(
                f"Las rutas {labels[0]} y {labels[1]} colisionan: {paths[0]}."
            )


def verify_source_hash(simulation: Path, expected: str, context: str) -> None:
    try:
        actual = sha256(simulation)
    except OSError as error:
        raise RuntimeError(
            f"No se pudo reverificar el SHA-256 fuente {context}: {error}"
        ) from error
    if actual.lower() != expected.lower():
        raise RuntimeError(
            f"El checksum del archivo de simulación cambió {context}: "
            f"esperado={expected}; actual={actual}."
        )


def numeric(text: str | None, *, field: str) -> float:
    if text is None:
        raise ValueError(f"Falta el campo serializado requerido: {field}")
    return float(text)


def format_value(value: Any) -> Any:
    if isinstance(value, float):
        return format(value, ".15g")
    if isinstance(value, bool):
        return str(value).lower()
    return value


def load_saved_state(path: Path) -> tuple[ET.Element, dict[str, ET.Element]]:
    with zipfile.ZipFile(path) as package:
        xml_names = [name for name in package.namelist() if name.endswith(".xml")]
        if len(xml_names) != 1:
            raise ValueError(
                "El paquete debe contener exactamente un documento XML de simulación."
            )
        root = ET.fromstring(package.read(xml_names[0]))

    tags_by_name: dict[str, str] = {}
    for graphic in root.findall(".//GraphicObjects/GraphicObject"):
        name = graphic.findtext("Name")
        tag = graphic.findtext("Tag")
        if name and tag:
            tags_by_name[name] = tag

    objects: dict[str, ET.Element] = {}
    for obj in root.findall(".//SimulationObjects/SimulationObject"):
        name = obj.findtext("Name")
        tag = tags_by_name.get(name or "")
        if tag:
            objects[tag] = obj
    return root, objects


def phase_by_id(stream: ET.Element, phase_id: str) -> ET.Element | None:
    for phase in stream.findall("./Phases/Phase"):
        if phase.findtext("ID") == phase_id:
            return phase
    return None


def compound(phase: ET.Element, name: str) -> ET.Element | None:
    for node in phase.findall("./Compounds/Compound"):
        if node.findtext("Name") == name:
            return node
    return None


def phase_properties(phase: ET.Element) -> ET.Element | None:
    """Devuelve el nodo Properties poblado (DWSIM serializa uno vacío antes)."""
    return next(
        (node for node in phase.findall("./Properties") if len(node) > 0),
        None,
    )


def stream_row(tag: str, stream: ET.Element) -> dict[str, Any]:
    phase0 = phase_by_id(stream, "0")
    if phase0 is None:
        raise ValueError(f"{tag}: falta la fase global ID=0.")
    properties = phase_properties(phase0)
    if properties is None:
        raise ValueError(f"{tag}: faltan propiedades de la fase global.")

    methanol = compound(phase0, "Methanol")
    if methanol is None:
        raise ValueError(f"{tag}: no se encontró el compuesto Methanol.")

    vapor = phase_by_id(stream, "2")
    vapor_molar_fraction = 0.0
    vapor_mass_fraction = 0.0
    if vapor is not None:
        vapor_properties = phase_properties(vapor)
        if vapor_properties is not None:
            vapor_molar_fraction = float(
                vapor_properties.findtext("molarfraction") or "0"
            )
            vapor_mass_fraction = float(
                vapor_properties.findtext("massfraction") or "0"
            )

    mass_flow = numeric(properties.findtext("massflow"), field=f"{tag}.massflow")
    enthalpy = numeric(properties.findtext("enthalpy"), field=f"{tag}.enthalpy")
    return {
        "object_id": tag,
        "object_type": "material_stream",
        "temperature_K": numeric(
            properties.findtext("temperature"), field=f"{tag}.temperature"
        ),
        "pressure_Pa": numeric(
            properties.findtext("pressure"), field=f"{tag}.pressure"
        ),
        "mass_flow_kg_s": mass_flow,
        "molar_flow_mol_s": numeric(
            properties.findtext("molarflow"), field=f"{tag}.molarflow"
        ),
        "volumetric_flow_m3_s": numeric(
            properties.findtext("volumetric_flow"),
            field=f"{tag}.volumetric_flow",
        ),
        "density_kg_m3": numeric(
            properties.findtext("density"), field=f"{tag}.density"
        ),
        "vapor_molar_fraction": vapor_molar_fraction,
        "vapor_mass_fraction": vapor_mass_fraction,
        "specific_enthalpy_kJ_kg": enthalpy,
        "methanol_mass_fraction": numeric(
            methanol.findtext("MassFraction"),
            field=f"{tag}.Methanol.MassFraction",
        ),
        "methanol_mass_flow_kg_s": numeric(
            methanol.findtext("MassFlow"), field=f"{tag}.Methanol.MassFlow"
        ),
        "energy_flow_kW": mass_flow * enthalpy,
    }


def equipment_row(
    hx: ET.Element, streams: dict[str, dict[str, Any]]
) -> dict[str, Any]:
    value = hx.findtext
    overall_coefficient = numeric(
        value("OverallCoefficient"), field=f"{HX_TAG}.OverallCoefficient"
    )
    area = numeric(value("Area"), field=f"{HX_TAG}.Area")
    hot_in = streams["MSTR-301_CONDENSADO_CALIENTE"]
    cold_in = streams["MSTR-302_AGUA_FRIA"]
    hot_out = streams["MSTR-303_CONDENSADO_ENFRIADO"]
    cold_out = streams["MSTR-304_AGUA_PRECALENTADA"]

    return {
        "object_id": HX_TAG,
        "object_type": "heat_exchanger",
        "calculation_mode": value("CalculationMode"),
        "flow_arrangement": value("FlowDir"),
        "overall_coefficient_W_m2_K": overall_coefficient,
        "area_m2": area,
        "ua_W_K": overall_coefficient * area,
        "correction_factor": numeric(
            value("LMTD_F"), field=f"{HX_TAG}.LMTD_F"
        ),
        "heat_duty_kW": numeric(value("HeatDuty"), field=f"{HX_TAG}.HeatDuty"),
        "lmtd_K": numeric(value("LMTD"), field=f"{HX_TAG}.LMTD"),
        "hot_inlet_temperature_K": hot_in["temperature_K"],
        "hot_outlet_temperature_K": hot_out["temperature_K"],
        "cold_inlet_temperature_K": cold_in["temperature_K"],
        "cold_outlet_temperature_K": cold_out["temperature_K"],
        "hot_inlet_pressure_Pa": hot_in["pressure_Pa"],
        "hot_outlet_pressure_Pa": hot_out["pressure_Pa"],
        "cold_inlet_pressure_Pa": cold_in["pressure_Pa"],
        "cold_outlet_pressure_Pa": cold_out["pressure_Pa"],
        "hot_side_pressure_drop_Pa": numeric(
            value("HotSidePressureDrop"),
            field=f"{HX_TAG}.HotSidePressureDrop",
        ),
        "cold_side_pressure_drop_Pa": numeric(
            value("ColdSidePressureDrop"),
            field=f"{HX_TAG}.ColdSidePressureDrop",
        ),
        "clean_contaminated_pressure_margin_inlet_Pa": (
            cold_in["pressure_Pa"] - hot_in["pressure_Pa"]
        ),
        "clean_contaminated_pressure_margin_outlet_Pa": (
            cold_out["pressure_Pa"] - hot_out["pressure_Pa"]
        ),
        "use_shell_and_tube_geometry": (
            (value("UseShellAndTubeGeometryInformation") or "").lower() == "true"
        ),
    }


def write_csv(path: Path, columns: tuple[str, ...], rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: format_value(row[key]) for key in columns})


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extrae resultados serializados del dwxmz del Caso 004."
    )
    parser.add_argument("--simulation", type=Path, default=DEFAULT_SIMULATION)
    parser.add_argument(
        "--process-output", type=Path, default=DEFAULT_PROCESS_OUTPUT
    )
    parser.add_argument(
        "--equipment-output", type=Path, default=DEFAULT_EQUIPMENT_OUTPUT
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    simulation = args.simulation.resolve()
    process_output = args.process_output.resolve()
    equipment_output = args.equipment_output.resolve()
    reject_path_collisions(simulation, process_output, equipment_output)

    source_before = sha256(simulation)
    _, objects = load_saved_state(simulation)

    missing = [tag for tag in (*STREAM_TAGS, HX_TAG) if tag not in objects]
    if missing:
        raise ValueError(f"Objetos ausentes en el flowsheet: {', '.join(missing)}")

    rows = [stream_row(tag, objects[tag]) for tag in STREAM_TAGS]
    rows_by_tag = {row["object_id"]: row for row in rows}
    hx_row = equipment_row(objects[HX_TAG], rows_by_tag)

    verify_source_hash(simulation, source_before, "antes de escribir los CSV")
    write_csv(process_output, PROCESS_COLUMNS, rows)
    verify_source_hash(simulation, source_before, "después del CSV de proceso")
    write_csv(equipment_output, EQUIPMENT_COLUMNS, [hx_row])

    verify_source_hash(simulation, source_before, "después del CSV de equipo")

    print(
        json.dumps(
            {
                "source_method": "dwxmz_saved_state_xml",
                "simulation": str(simulation),
                "simulation_sha256": source_before,
                "source_unchanged": True,
                "process_output": str(process_output),
                "equipment_output": str(equipment_output),
                "stream_count": len(rows),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
