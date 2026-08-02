"""Carga y normalización de la evidencia publicada por los casos PTR.

El dashboard consume exclusivamente artefactos versionados del repositorio. La
capa de datos se mantiene separada de Streamlit para que el descubrimiento de
casos, la resolución de rutas y las tablas de criterios puedan probarse sin
levantar la interfaz.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pandas as pd
import yaml

STREAM_TYPES = {"material_stream", "material stream", "materialstream"}


@dataclass(frozen=True)
class CaseBundle:
    """Artefactos estructurados y contenido explicativo de un caso."""

    case_id: str
    path: Path
    metadata: dict[str, Any]
    validation: dict[str, Any]
    catalog: dict[str, Any]
    datasets: dict[str, pd.DataFrame]
    dataset_paths: dict[str, Path]
    figure_paths: tuple[Path, ...]

    @property
    def title(self) -> str:
        return str(self.metadata.get("title", self.path.name))

    @property
    def short_title(self) -> str:
        return str(self.catalog.get("short_title", self.title))

    @property
    def version(self) -> str:
        return str(self.validation.get("case_version", self.metadata.get("version", "N/D")))

    @property
    def lifecycle_status(self) -> str:
        return str(
            self.validation.get("lifecycle_status", self.metadata.get("status", "N/D"))
        )

    @property
    def overall_status(self) -> str:
        return str(self.validation.get("overall_status", "NOT_RUN"))


def repository_root(start: Path | None = None) -> Path:
    """Encuentra la raíz por marcadores estables del repositorio."""

    current = (start or Path(__file__)).resolve()
    if current.is_file():
        current = current.parent
    for candidate in (current, *current.parents):
        if (candidate / "pyproject.toml").is_file() and (candidate / "cases").is_dir():
            return candidate
    raise FileNotFoundError("No se encontró la raíz de PTR-Engineering-Cases.")


def load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def load_catalog(root: Path | None = None) -> dict[str, Any]:
    repo = root or repository_root()
    return load_yaml(repo / "dashboards" / "streamlit" / "case_catalog.yaml")


def discover_case_dirs(root: Path | None = None) -> list[Path]:
    """Descubre casos implementados, excluyendo plantillas y propuestas."""

    repo = root or repository_root()
    return sorted(
        path
        for path in (repo / "cases").glob("[0-9][0-9][0-9]_*")
        if path.is_dir()
        and (path / "metadata.yaml").is_file()
        and (path / "validation_results.json").is_file()
    )


def _portable_path(raw_path: str) -> Path:
    return Path(*raw_path.replace("\\", "/").split("/"))


def _resolve_portable(root: Path, raw_path: str) -> Path:
    target = (root / _portable_path(raw_path)).resolve()
    try:
        target.relative_to(root.resolve())
    except ValueError as exc:
        raise ValueError(f"Ruta fuera del repositorio: {raw_path}") from exc
    return target


def load_case_bundle(
    case_dir: Path,
    root: Path | None = None,
    catalog: dict[str, Any] | None = None,
) -> CaseBundle:
    repo = (root or repository_root(case_dir)).resolve()
    case_dir = case_dir.resolve()
    case_id = case_dir.name.split("_", maxsplit=1)[0]
    metadata = load_yaml(case_dir / "metadata.yaml")
    validation = load_json(case_dir / "validation_results.json")
    catalog_data = catalog or load_catalog(repo)
    catalog_entry = dict(catalog_data.get("cases", {}).get(case_id, {}))

    datasets: dict[str, pd.DataFrame] = {}
    dataset_paths: dict[str, Path] = {}
    for raw_path in validation.get("datasets", []):
        path = _resolve_portable(repo, str(raw_path))
        if path.suffix.lower() != ".csv" or not path.is_file():
            continue
        key = path.stem
        datasets[key] = pd.read_csv(path)
        dataset_paths[key] = path

    figures = tuple(
        path
        for raw_path in validation.get("figures", [])
        if (path := _resolve_portable(repo, str(raw_path))).is_file()
    )

    return CaseBundle(
        case_id=case_id,
        path=case_dir,
        metadata=metadata,
        validation=validation,
        catalog=catalog_entry,
        datasets=datasets,
        dataset_paths=dataset_paths,
        figure_paths=figures,
    )


def load_all_cases(root: Path | None = None) -> list[CaseBundle]:
    repo = (root or repository_root()).resolve()
    catalog = load_catalog(repo)
    return [load_case_bundle(path, repo, catalog) for path in discover_case_dirs(repo)]


def process_dataset(case: CaseBundle) -> pd.DataFrame:
    for key, frame in case.datasets.items():
        if key.startswith("process_results"):
            return frame.copy()
    return pd.DataFrame()


def chromatography_dataset(case: CaseBundle) -> pd.DataFrame:
    for key, frame in case.datasets.items():
        if key.startswith("chromatography_results"):
            return frame.copy()
    return pd.DataFrame()


def material_streams(case: CaseBundle) -> pd.DataFrame:
    frame = process_dataset(case)
    if frame.empty or "object_type" not in frame.columns:
        return frame
    normalized = frame["object_type"].astype(str).str.lower().str.strip()
    return frame.loc[normalized.isin(STREAM_TYPES)].reset_index(drop=True)


def criteria_frame(case: CaseBundle) -> pd.DataFrame:
    records: list[dict[str, Any]] = []
    for criterion in case.validation.get("criteria", []):
        result = criterion.get("result") or {}
        threshold = criterion.get("threshold") or {}
        threshold_text = "N/A"
        if threshold:
            threshold_text = " ".join(
                str(value)
                for value in (
                    threshold.get("operator", ""),
                    threshold.get("value", ""),
                    threshold.get("unit", ""),
                )
                if value != ""
            )
        records.append(
            {
                "Alcance": criterion.get("scope", "N/D"),
                "Criterio": criterion.get("title", criterion.get("id", "N/D")),
                "Estado": criterion.get("status", "NOT_RUN"),
                "Resultado": result.get("value"),
                "Unidad": result.get("unit", ""),
                "Umbral": threshold_text,
                "Fuente": criterion.get("evidence_source", "N/D"),
                "Bloqueante": bool(criterion.get("blocking", False)),
            }
        )
    return pd.DataFrame.from_records(records)


def portfolio_frame(cases: list[CaseBundle]) -> pd.DataFrame:
    return pd.DataFrame.from_records(
        [
            {
                "ID": case.case_id,
                "Caso": case.short_title,
                "Etapa": case.catalog.get("process_stage", "N/D"),
                "Ciclo de vida": case.lifecycle_status,
                "Validación": case.overall_status,
                "Versión": case.version,
                "Fenómenos": len(case.catalog.get("phenomena", [])),
                "Fuente": case.validation.get("actual_source", "N/D"),
            }
            for case in cases
        ]
    )


def status_counts(cases: list[CaseBundle]) -> pd.DataFrame:
    order = ["PASS", "CONDITIONAL", "FAIL", "NOT_RUN"]
    counts = pd.Series(
        [case.overall_status for case in cases], dtype="string"
    ).value_counts()
    records = [
        {"Estado": status, "Casos": int(counts.get(status, 0))}
        for status in order
        if counts.get(status, 0) > 0
    ]
    return pd.DataFrame.from_records(records)


def criterion_status_counts(cases: list[CaseBundle]) -> pd.DataFrame:
    frames = []
    for case in cases:
        frame = criteria_frame(case)
        if not frame.empty:
            frames.append(frame.assign(Caso=case.case_id))
    if not frames:
        return pd.DataFrame(columns=["Alcance", "Estado", "Criterios"])
    combined = pd.concat(frames, ignore_index=True)
    return (
        combined.groupby(["Alcance", "Estado"], dropna=False)
        .size()
        .rename("Criterios")
        .reset_index()
    )


def freshness_utc(cases: list[CaseBundle]) -> str:
    paths = [case.path / "validation_results.json" for case in cases]
    if not paths:
        return "N/D"
    timestamp = max(path.stat().st_mtime for path in paths)
    return datetime.fromtimestamp(timestamp, tz=UTC).strftime("%Y-%m-%d %H:%M UTC")
