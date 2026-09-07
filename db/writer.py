"""
db/writer.py — Persistenza forecast su Turso (libSQL/SQLite cloud)

Variabili d'ambiente richieste (o file .env):
    TURSO_URL    
    TURSO_TOKEN  

Uso diretto:
    from db.writer import write_to_db
    write_to_db(summary, horizon_days=7)

Backfill manuale:
    python -m db.writer --csv forecast_load_NORD_20260905_1444.csv --model load --zone NORD
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator

import pandas as pd

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Mapping colonne CSV → nomi canonici nel DB
# ---------------------------------------------------------------------------
_TS_MAP       = ["date", "ts", "timestamp", "datetime", "time"]
_SECTION_MAP  = ["section"]
_ACTUAL_MAP   = ["total load (gw)", "pv_production (gw)", "actual_mw", "actual_gw",
                 "value_mw", "value_gw", "value", "load_gw", "load_mw"]
_PREDICTED_MAP= ["predicted_load (gw)", "predicted_pv (gw)", "predicted_load",
                 "predicted_pv", "predicted_gw", "predicted_mw",
                 "raw_load (gw)", "raw_pv (gw)"]
_LOWER_MAP    = ["lower_bound", "lower_mw", "lower_gw", "lower", "q10", "p10"]
_UPPER_MAP    = ["upper_bound", "upper_mw", "upper_gw", "upper", "q90", "p90"]

_WEATHER_MAP  = {
    "temperature_2m (°c)":        "weather_temperature_2m",
    "temperature_2m":             "weather_temperature_2m",
    "apparent_temperature (°c)":  "weather_apparent_temperature",
    "apparent_temperature":       "weather_apparent_temperature",
    "prev_year_temp (°c)":        "weather_prev_year_temperature",
    "relative_humidity_2m (%)":   "weather_relative_humidity_2m",
    "relative_humidity_2m":       "weather_relative_humidity_2m",
    "wind_speed_10m (km/h)":      "weather_wind_speed_10m",
    "wind_speed_10m":             "weather_wind_speed_10m",
    "wind_direction_10m":         "weather_wind_direction_10m",
    "direct_radiation (w/m²)":    "weather_direct_radiation",
    "direct_radiation":           "weather_direct_radiation",
    "shortwave_radiation":        "weather_shortwave_radiation",
    "direct_normal_irradiance":   "weather_direct_normal_irradiance",
    "diffuse_radiation":          "weather_diffuse_radiation",
    "cloud_cover (%)":            "weather_cloud_cover",
    "cloud_cover":                "weather_cloud_cover",
    "cloud_cover_low":            "weather_cloud_cover_low",
    "cloud_cover_mid":            "weather_cloud_cover_mid",
    "cloud_cover_high":           "weather_cloud_cover_high",
    "precipitation":              "weather_precipitation",
    "snowfall":                   "weather_snowfall",
    "snow_depth":                 "weather_snow_depth",
}

# ---------------------------------------------------------------------------
# DDL — identico allo schema SQLite, Turso è compatibile 1:1
# ---------------------------------------------------------------------------
_DDL_STATEMENTS = [
    """CREATE TABLE IF NOT EXISTS forecast_runs (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        model         TEXT    NOT NULL,
        zone          TEXT    NOT NULL,
        created_at    TEXT    NOT NULL,
        horizon_days  INTEGER,
        source_file   TEXT,
        UNIQUE(model, zone, created_at)
    )""",
    """CREATE TABLE IF NOT EXISTS forecast_records (
        id                              INTEGER PRIMARY KEY AUTOINCREMENT,
        run_id                          INTEGER NOT NULL,
        section                         TEXT    NOT NULL,
        ts                              TEXT    NOT NULL,
        actual_gw                       REAL,
        predicted_gw                    REAL,
        lower_bound                     REAL,
        upper_bound                     REAL,
        weather_temperature_2m          REAL,
        weather_apparent_temperature    REAL,
        weather_prev_year_temperature   REAL,
        weather_relative_humidity_2m    REAL,
        weather_wind_speed_10m          REAL,
        weather_wind_direction_10m      REAL,
        weather_direct_radiation        REAL,
        weather_shortwave_radiation     REAL,
        weather_direct_normal_irradiance REAL,
        weather_diffuse_radiation       REAL,
        weather_cloud_cover             REAL,
        weather_cloud_cover_low         REAL,
        weather_cloud_cover_mid         REAL,
        weather_cloud_cover_high        REAL,
        weather_precipitation           REAL,
        weather_snowfall                REAL,
        weather_snow_depth              REAL,
        extra                           TEXT
    )""",
    """CREATE TABLE IF NOT EXISTS forecast_metrics (
        run_id  INTEGER PRIMARY KEY,
        mape    REAL,
        rmse    REAL,
        mae     REAL
    )""",
    "CREATE INDEX IF NOT EXISTS idx_fr_zone    ON forecast_runs(zone)",
    "CREATE INDEX IF NOT EXISTS idx_fr_model   ON forecast_runs(model)",
    "CREATE INDEX IF NOT EXISTS idx_rec_run    ON forecast_records(run_id)",
    "CREATE INDEX IF NOT EXISTS idx_rec_ts     ON forecast_records(ts)",
    "CREATE INDEX IF NOT EXISTS idx_rec_sec    ON forecast_records(section)",
]

# ---------------------------------------------------------------------------
# Connessione Turso
# ---------------------------------------------------------------------------

def _get_client():
    """Crea un client Turso sincrono dalle variabili d'ambiente."""
    import libsql_client

    url   = os.environ.get("TURSO_URL")
    token = os.environ.get("TURSO_TOKEN")

    if not url:
        raise RuntimeError(
            "TURSO_URL non trovata. Aggiungila al file .env o alle variabili d'ambiente."
        )
    if not token:
        raise RuntimeError(
            "TURSO_TOKEN non trovato. Aggiungila al file .env o alle variabili d'ambiente."
        )

    return libsql_client.create_client_sync(url=url, auth_token=token)


def init_db() -> None:
    """Crea le tabelle se non esistono ancora."""
    client = _get_client()
    try:
        client.batch(_DDL_STATEMENTS)
        logger.debug("DB Turso inizializzato.")
    finally:
        client.close()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _find_col(df: pd.DataFrame, candidates: list[str]) -> str | None:
    cols_lower = {c.lower(): c for c in df.columns}
    for c in candidates:
        if c.lower() in cols_lower:
            return cols_lower[c.lower()]
    return None


def _weather_cols(df: pd.DataFrame) -> dict[str, str]:
    cols_lower = {c.lower(): c for c in df.columns}
    result = {}
    for alias, canonical in _WEATHER_MAP.items():
        if alias.lower() in cols_lower and canonical not in result:
            result[canonical] = cols_lower[alias.lower()]
    return result


def _parse_stamp(path: Path) -> str:
    m = re.search(r"(\d{8})_(\d{4})", path.stem)
    if m:
        try:
            dt = datetime.strptime(m.group(1) + m.group(2), "%Y%m%d%H%M")
            return dt.replace(tzinfo=timezone.utc).isoformat()
        except ValueError:
            pass
    m2 = re.search(r"(\d{4}-\d{2}-\d{2})", path.stem)
    if m2:
        try:
            dt = datetime.strptime(m2.group(1), "%Y-%m-%d")
            return dt.replace(tzinfo=timezone.utc).isoformat()
        except ValueError:
            pass
    return datetime.now(timezone.utc).isoformat()


def _read_csv(path: Path) -> pd.DataFrame:
    for sep in (",", ";", "\t"):
        try:
            df = pd.read_csv(path, sep=sep, encoding="utf-8-sig", low_memory=False)
            if len(df.columns) > 1:
                return df
        except Exception:
            continue
    raise ValueError(f"Impossibile parsare {path}")


def _cleanup_old_runs(client, model: str, zone: str, keep: int = 30) -> None:
    """Elimina i run più vecchi tenendo solo gli ultimi `keep` per model×zone."""
    client.execute(
        """DELETE FROM forecast_runs
           WHERE model = ? AND zone = ?
           AND id NOT IN (
               SELECT id FROM forecast_runs
               WHERE model = ? AND zone = ?
               ORDER BY created_at DESC
               LIMIT ?
           )""",
        [model, zone, model, zone, keep],
    )
    logger.debug("Cleanup: tenuti ultimi %d run per %s/%s", keep, model, zone)


# ---------------------------------------------------------------------------
# Insert singolo CSV
# ---------------------------------------------------------------------------

def insert_csv(
    csv_path: Path,
    model: str,
    zone: str,
    horizon_days: int | None = None,
    keep_runs: int = 30,
) -> int:
    """
    Legge csv_path e inserisce tutti i dati su Turso.
    Ritorna il run_id. Idempotente: se il run esiste già, non duplica.
    """
    init_db()
    df = _read_csv(csv_path)
    logger.debug("CSV: %d righe × %d colonne", len(df), len(df.columns))

    ts_col        = _find_col(df, _TS_MAP)
    section_col   = _find_col(df, _SECTION_MAP)
    actual_col    = _find_col(df, _ACTUAL_MAP)
    predicted_col = _find_col(df, _PREDICTED_MAP)
    lower_col     = _find_col(df, _LOWER_MAP)
    upper_col     = _find_col(df, _UPPER_MAP)
    weather       = _weather_cols(df)

    if ts_col is None:
        raise ValueError(f"Nessuna colonna timestamp in {csv_path.name}. Colonne: {list(df.columns)}")

    used = {ts_col}
    for col in [section_col, actual_col, predicted_col, lower_col, upper_col]:
        if col:
            used.add(col)
    used.update(weather.values())
    extra_cols = [c for c in df.columns if c not in used]

    df[ts_col] = pd.to_datetime(df[ts_col], utc=True, errors="coerce").dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    df = df.dropna(subset=[ts_col])

    if section_col is None:
        df["_section"] = "forecast"
        section_col = "_section"

    created_at = _parse_stamp(csv_path)
    client = _get_client()

    try:
        # ── Controlla se il run esiste già ──────────────────────────────
        res = client.execute(
            "SELECT id FROM forecast_runs WHERE model=? AND zone=? AND created_at=?",
            [model, zone.upper(), created_at],
        )
        if res.rows:
            run_id = res.rows[0][0]
            logger.info("Run già presente (id=%d), dati non re-inseriti.", run_id)
            return run_id

        # ── Insert forecast_runs ─────────────────────────────────────────
        client.execute(
            "INSERT INTO forecast_runs (model, zone, created_at, horizon_days, source_file) VALUES (?,?,?,?,?)",
            [model, zone.upper(), created_at, horizon_days, str(csv_path)],
        )
        res = client.execute(
            "SELECT id FROM forecast_runs WHERE model=? AND zone=? AND created_at=?",
            [model, zone.upper(), created_at],
        )
        run_id = res.rows[0][0]

        # ── Bulk insert forecast_records (batch da 100 righe) ────────────
        # Turso ha un limite sulla dimensione dei batch → inseriamo a gruppi
        INSERT_SQL = """INSERT INTO forecast_records (
            run_id, section, ts,
            actual_gw, predicted_gw, lower_bound, upper_bound,
            weather_temperature_2m, weather_apparent_temperature,
            weather_prev_year_temperature, weather_relative_humidity_2m,
            weather_wind_speed_10m, weather_wind_direction_10m,
            weather_direct_radiation, weather_shortwave_radiation,
            weather_direct_normal_irradiance, weather_diffuse_radiation,
            weather_cloud_cover, weather_cloud_cover_low,
            weather_cloud_cover_mid, weather_cloud_cover_high,
            weather_precipitation, weather_snowfall, weather_snow_depth,
            extra
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"""

        def _v(col):
            if col is None:
                return None
            val = r[col]
            return None if pd.isna(val) else float(val)

        BATCH_SIZE = 100
        batch = []

        for _, r in df.iterrows():
            extra_dict = {}
            for ec in extra_cols:
                val = r[ec]
                if pd.notna(val):
                    extra_dict[ec] = val if isinstance(val, (str, bool)) else float(val)
            extra_json = json.dumps(extra_dict, ensure_ascii=False) if extra_dict else None

            row_vals = [
                run_id,
                str(r[section_col]),
                r[ts_col],
                _v(actual_col),
                _v(predicted_col),
                _v(lower_col),
                _v(upper_col),
                _v(weather.get("weather_temperature_2m")),
                _v(weather.get("weather_apparent_temperature")),
                _v(weather.get("weather_prev_year_temperature")),
                _v(weather.get("weather_relative_humidity_2m")),
                _v(weather.get("weather_wind_speed_10m")),
                _v(weather.get("weather_wind_direction_10m")),
                _v(weather.get("weather_direct_radiation")),
                _v(weather.get("weather_shortwave_radiation")),
                _v(weather.get("weather_direct_normal_irradiance")),
                _v(weather.get("weather_diffuse_radiation")),
                _v(weather.get("weather_cloud_cover")),
                _v(weather.get("weather_cloud_cover_low")),
                _v(weather.get("weather_cloud_cover_mid")),
                _v(weather.get("weather_cloud_cover_high")),
                _v(weather.get("weather_precipitation")),
                _v(weather.get("weather_snowfall")),
                _v(weather.get("weather_snow_depth")),
                extra_json,
            ]
            batch.append({"sql": INSERT_SQL, "args": row_vals})

            if len(batch) >= BATCH_SIZE:
                client.batch(batch)
                batch = []

        if batch:
            client.batch(batch)

        # ── Cleanup run vecchi ───────────────────────────────────────────
        _cleanup_old_runs(client, model, zone.upper(), keep=keep_runs)

        sections = df[section_col].value_counts().to_dict()
        logger.info(
            "✓ Turso insert | model=%-4s zone=%-6s run_id=%d righe=%d sezioni=%s",
            model, zone, run_id, len(df), sections,
        )
        return run_id

    finally:
        client.close()


# ---------------------------------------------------------------------------
# Entry point: write_to_db(summary)
# ---------------------------------------------------------------------------

def write_to_db(
    summary: dict[str, dict[str, Path]],
    horizon_days: int | None = None,
    keep_runs: int = 30,
) -> None:
    """
    Scrive su Turso tutti i CSV presenti in summary.

    summary = {
        "load": {"NORD": Path("…/forecast_load_NORD_….csv"), …},
        "pv":   {"ITALY": Path("…/ITALIA/"),                 …},
    }
    """
    logger.info("Scrittura su Turso DB")

    for model, zone_results in summary.items():
        if model not in ("load", "pv"):
            logger.warning("Modello '%s' non riconosciuto, skip.", model)
            continue

        for zone, path in zone_results.items():
            path = Path(path)
            if path.is_dir():
                csv_files = sorted(path.glob("*.csv"))
                if not csv_files:
                    logger.warning("Nessun CSV in %s, skip.", path)
                    continue
                csv_path = csv_files[-1]
            elif path.is_file() and path.suffix == ".csv":
                csv_path = path
            else:
                logger.warning("Path non valido per %s/%s: %s", model, zone, path)
                continue

            try:
                insert_csv(csv_path, model, zone, horizon_days, keep_runs)
            except Exception as e:
                logger.error("✗ Turso insert FALLITO | %s/%s: %s", model, zone, e, exc_info=True)


# ---------------------------------------------------------------------------
# CLI backfill
# ---------------------------------------------------------------------------

def _cli() -> None:
    p = argparse.ArgumentParser(description="Backfill manuale: importa un CSV su Turso")
    p.add_argument("--csv",      required=True)
    p.add_argument("--model",    required=True, choices=["load", "pv"])
    p.add_argument("--zone",     required=True)
    p.add_argument("--horizon",  type=int, default=None)
    p.add_argument("--keep",     type=int, default=30, help="Max run da tenere per zona (default 30)")
    args = p.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")

    from dotenv import load_dotenv
    load_dotenv()

    csv_path = Path(args.csv)
    if not csv_path.exists():
        p.error(f"File non trovato: {csv_path}")

    run_id = insert_csv(csv_path, args.model, args.zone, args.horizon, args.keep)
    print(f"Inserito run_id={run_id} su Turso")


if __name__ == "__main__":
    _cli()
