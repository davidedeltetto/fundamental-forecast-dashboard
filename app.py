import streamlit as st
import pandas as pd
import numpy as np
import os, glob
import plotly.graph_objects as go

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="TERNA | OPERATIVE FORECAST PLATFORM",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CONFIG / COSTANTI ─────────────────────────────────────────────────────────
ZONE_ORDER = ["NORD", "CNOR", "CSUD", "SUD", "CALA", "SICI", "SARD"]

ZONE_COLORS = {
    "NORD":  "#7be2ff",   # Ciano
    "CNOR":  "#f39c12",   # Arancione
    "CSUD":  "#2ecc71",   # Verde
    "SUD":   "#9b59b6",   # Viola
    "CALA":  "#3498db",   # Blu elettrico
    "SICI":  "#f1c40f",   # Giallo
    "SARD":  "#e74c3c",   # Rosso
    "ITALY": "#ffffff",
}

# PV chart usa gli stessi colori per coerenza
PV_ZONE_COLORS = ZONE_COLORS

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

# ── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="stAppViewContainer"]   { background:#0d1117 !important; }
[data-testid="stHeader"]             { background:transparent !important; }
[data-testid="stMainBlockContainer"] { padding-top:0 !important; }
.block-container                     { padding:0 1rem 1rem !important; }

/* Sidebar styling */
[data-testid="stSidebar"] {
    background: #0d1117 !important;
    border-right: 1px solid #21262d !important;
    min-width: 130px !important;
    max-width: 130px !important;
}
[data-testid="stSidebar"] > div:first-child {
    padding: 0 !important;
}

/* Sidebar Nav Buttons */
.sb-nav-btn {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    width: 100%;
    padding: 20px 8px 16px;
    border: none;
    background: transparent;
    cursor: pointer;
    border-left: 3px solid transparent;
    transition: all 0.15s;
    gap: 6px;
}
.sb-nav-btn:hover { background: #161b22; }
.sb-nav-btn.active {
    background: #10161d;
    border-left-color: #7be2ff;
}
.sb-nav-btn.active-pv {
    background: #10161d;
    border-left-color: #ffd700;
}
.sb-icon { font-size: 28px; line-height: 1; }
.sb-label {
    font-family: 'Courier New', monospace;
    font-size: 9px;
    font-weight: 700;
    letter-spacing: .10em;
    color: #8b949e;
}
.sb-label.active   { color: #7be2ff; }
.sb-label.active-pv { color: #ffd700; }
.sb-divider {
    border: none;
    border-top: 1px solid #21262d;
    margin: 4px 12px;
}
.sb-logo {
    font-family: 'Courier New', monospace;
    font-size: 9px;
    font-weight: 700;
    color: #21262d;
    letter-spacing: .12em;
    text-align: center;
    padding: 14px 4px 10px;
}

/* Header */
.t-app-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: #0d1117;
    border-bottom: 1px solid #21262d;
    padding: 10px 16px;
    margin-bottom: 4px;
}
.t-app-logo {
    font-family: 'Courier New', monospace;
    font-size: 14px;
    font-weight: 700;
    color: #e6edf3;
    letter-spacing: .1em;
}
.t-app-logo span { color: #7be2ff; }
.t-app-logo span.pv { color: #ffd700; }

/* Info strip */
.t-info-strip {
    background: #10161d;
    border: 1px solid #21262d;
    border-radius: 4px;
    padding: 6px 14px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    font-family: 'Courier New', monospace;
    font-size: 10px;
    color: #8b949e;
    margin-bottom: 10px;
}

/* KPI grid */
.t-kpi-container {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 8px;
    margin-bottom: 8px;
}
.t-kpi-card {
    background: #161b22;
    border: 1px solid #21262d;
    border-radius: 5px;
    padding: 8px 12px;
}
.t-kpi-label {
    font-family: 'Courier New', monospace;
    font-size: 9px;
    color: #8b949e;
    letter-spacing: .07em;
    margin-bottom: 3px;
}
.t-kpi-value {
    font-family: 'Courier New', monospace;
    font-size: 18px;
    font-weight: 700;
    color: #e6edf3;
}
.pos { color: #2ecc71; }
.neg { color: #e74c3c; }

/* Bottom stats */
.t-bottom-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
    margin-top: 6px;
}
.t-bottom-card {
    background: #161b22;
    border: 1px solid #21262d;
    border-radius: 5px;
    padding: 8px 14px;
}
.t-bottom-label {
    font-family: 'Courier New', monospace;
    font-size: 9px;
    color: #8b949e;
    letter-spacing: .07em;
    margin-bottom: 5px;
}
.t-bottom-vals {
    font-family: 'Courier New', monospace;
    font-size: 11px;
    color: #8b949e;
}
.t-bottom-vals b { font-size: 14px; font-weight: 700; }
.t-metrics-flex { display: flex; gap: 20px; align-items: center; }
.t-flex-val { font-family: 'Courier New', monospace; font-size: 16px; font-weight: 700; }
.t-flex-sub { font-family: 'Courier New', monospace; font-size: 9px; color: #8b949e; }

.t-chart-title {
    font-family: 'Courier New', monospace;
    font-size: 9px;
    color: #8b949e;
    letter-spacing: .05em;
    border-bottom: 1px solid #21262d;
    padding-bottom: 4px;
    margin-bottom: 4px;
}
.t-panel-title {
    font-family: 'Courier New', monospace;
    font-size: 10px;
    color: #8b949e;
    letter-spacing: .08em;
    margin-bottom: 6px;
}
.t-tag {
    font-family: 'Courier New', monospace;
    font-size: 8px;
    background: #0d1117;
    border: 1px solid #21262d;
    border-radius: 3px;
    padding: 2px 6px;
    color: #8b949e;
    margin-left: 6px;
}

/* Buttons */
.stButton > button {
    font-family: 'Courier New', monospace !important;
    font-size: 10px !important;
    font-weight: 700 !important;
    border-radius: 3px !important;
    border: 1px solid #21262d !important;
    background: #161b22 !important;
    color: #8b949e !important;
    padding: 3px 10px !important;
}
.stButton > button:hover { border-color: #7be2ff !important; color: #e6edf3 !important; }
hr { border-color: #21262d !important; margin: 8px 0 !important; }

[data-testid="stHorizontalBlock"] { align-items: stretch !important; }
[data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:first-child { display: flex; flex-direction: column; }
[data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:first-child > [data-testid="stVerticalBlock"] {
    flex: 1;
    background: #10161d;
    border-right: 1px solid #21262d;
    padding: 0 8px 12px 4px;
}

/* Segmented control */
div[data-testid="stSegmentedControl"] {
    background: #0d1117 !important;
    border: 1px solid #21262d !important;
    border-radius: 4px !important;
    gap: 2px !important;
    padding: 2px !important;
}
div[data-testid="stSegmentedControl"] label {
    font-family: 'Courier New', monospace !important;
    font-size: 9px !important;
    color: #8b949e !important;
    border-radius: 3px !important;
    padding: 3px 8px !important;
    transition: all 0.15s !important;
}
div[data-testid="stSegmentedControl"] label:hover { color: #e6edf3 !important; background: #1e2630 !important; }
div[data-testid="stSegmentedControl"] [aria-selected="true"] {
    background: #21262d !important;
    color: #e6edf3 !important;
    border: 1px solid #30363d !important;
}

button[title="View fullscreen"] { display: none !important; }
</style>
""", unsafe_allow_html=True)

# ── SESSION STATE ─────────────────────────────────────────────────────────────
if "dashboard_mode" not in st.session_state:
    st.session_state.dashboard_mode = "LOAD"  # "LOAD" | "PV"
if "selected_zone" not in st.session_state:
    st.session_state.selected_zone = "NORD"
if "timeframe" not in st.session_state:
    st.session_state.timeframe = "Week"
if "meteo_var" not in st.session_state:
    st.session_state.meteo_var = None
if "prev_year_vars" not in st.session_state:
    st.session_state.prev_year_vars = []
if "pv_zone" not in st.session_state:
    st.session_state.pv_zone = "NORD"
if "pv_timeframe" not in st.session_state:
    st.session_state.pv_timeframe = "Week"
if "pv_meteo_var" not in st.session_state:
    st.session_state.pv_meteo_var = None

# ── SIDEBAR – MODE SWITCHER ───────────────────────────────────────────────────
with st.sidebar:
    st.markdown("<div class='sb-logo'>TERNA</div>", unsafe_allow_html=True)
    st.markdown("<hr class='sb-divider'>", unsafe_allow_html=True)

    mode = st.session_state.dashboard_mode

    if st.button("⚡\nLOAD", key="sb_load", use_container_width=True,
                 help="Previsione carico elettrico zonale"):
        st.session_state.dashboard_mode = "LOAD"
        st.rerun()

    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

    if st.button("☀️\nPV", key="sb_pv", use_container_width=True,
                 help="Previsione produzione fotovoltaica zonale"):
        st.session_state.dashboard_mode = "PV"
        st.rerun()

    st.markdown("<hr class='sb-divider' style='margin-top:16px'>", unsafe_allow_html=True)
    active_icon = "⚡" if mode == "LOAD" else "☀️"
    active_color = "#7be2ff" if mode == "LOAD" else "#ffd700"
    active_label = "LOAD" if mode == "LOAD" else "PV"
    st.markdown(
        f"<div style='font-family:Courier New,monospace;font-size:8px;color:{active_color};"
        f"text-align:center;padding:8px 4px;letter-spacing:.10em'>"
        f"{active_icon} {active_label} MODE</div>",
        unsafe_allow_html=True
    )


# ── DATA LAYER – TURSO ────────────────────────────────────────────────────────

def _get_turso_client():
    """Client Turso sincrono. Ritorna None se le credenziali non sono configurate."""
    try:
        import libsql_client
        url   = st.secrets.get("TURSO_URL")   or os.environ.get("TURSO_URL")
        token = st.secrets.get("TURSO_TOKEN") or os.environ.get("TURSO_TOKEN")
        if not url or not token:
            return None
        return libsql_client.create_client_sync(url=url, auth_token=token)
    except Exception:
        return None


def _load_from_db(model: str, zone: str) -> dict | None:
    """
    Legge da Turso l'ultimo run disponibile per model×zone.
    Ritorna None se le credenziali mancano o la zona non ha dati.
    """
    client = _get_turso_client()
    if client is None:
        return None

    try:
        # Recupera l'ultimo run per questa zona/modello
        res = client.execute(
            "SELECT id, source_file FROM forecast_runs "
            "WHERE model = ? AND zone = ? ORDER BY created_at DESC LIMIT 1",
            [model, zone.upper()],
        )
        if not res.rows:
            return None

        run_id      = res.rows[0][0]
        source_file = res.rows[0][1] or ""

        # Legge tutti i record di quel run
        res2 = client.execute(
            """SELECT section, ts AS datetime,
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
               FROM forecast_records WHERE run_id = ? ORDER BY datetime""",
            [run_id],
        )

        if not res2.rows:
            return None

        cols = [c.name for c in res2.columns]
        df   = pd.DataFrame([dict(zip(cols, row)) for row in res2.rows])

        if df.empty:
            return None

        df["datetime"] = pd.to_datetime(df["datetime"], utc=True, errors="coerce")
        df["datetime"] = df["datetime"].dt.tz_localize(None)

        # Espande la colonna extra (JSON) → colonne separate
        import json as _json
        extra_rows = []
        for raw in df["extra"]:
            try:
                extra_rows.append(_json.loads(raw) if raw else {})
            except Exception:
                extra_rows.append({})
        if any(extra_rows):
            extra_df = pd.DataFrame(extra_rows, index=df.index)
            df = pd.concat([df.drop(columns=["extra"]), extra_df], axis=1)
        else:
            df = df.drop(columns=["extra"])

        hist = df[df["section"] == "historical"].copy().reset_index(drop=True)
        fore = df[df["section"] == "forecast"].copy().reset_index(drop=True)

        return dict(
            hist=hist,
            fore=fore,
            filename=os.path.basename(source_file),
            is_dummy=False,
            from_db=True,
        )

    except Exception:
        return None
    finally:
        client.close()


# ── DATA LAYER – LOAD (CSV fallback) ─────────────────────────────────────────
def _candidate_data_dirs() -> list[str]:
    dirs = [DATA_DIR, BASE_DIR]
    return list(dict.fromkeys(d for d in dirs if os.path.isdir(d)))


def find_latest_file(zone: str) -> str | None:
    files = []
    for directory in _candidate_data_dirs():
        files.extend(glob.glob(os.path.join(directory, f"forecast_load_{zone}_*.csv")))
    files = sorted(set(files), reverse=True)
    return files[0] if files else None


@st.cache_data(ttl=120, show_spinner=False)
def load_zone_data(zone: str) -> dict:
    # 1) Prova DB SQLite
    db_data = _load_from_db("load", zone)
    if db_data is not None:
        hist = db_data["hist"].rename(columns={
            "actual_gw":    "actual_load",
            "predicted_gw": "predicted_load",
            "weather_temperature_2m":         "temperature_2m (°C)",
            "weather_apparent_temperature":   "apparent_temperature (°C)",
            "weather_relative_humidity_2m":   "relative_humidity_2m (%)",
            "weather_wind_speed_10m":         "wind_speed_10m (km/h)",
            "weather_direct_radiation":       "direct_radiation (W/m²)",
            "weather_cloud_cover":            "cloud_cover (%)",
            "weather_prev_year_temperature":  "Prev_Year_Temp (°C)",
        })
        fore = db_data["fore"].rename(columns={
            "actual_gw":    "actual_load",
            "predicted_gw": "predicted_load",
            "weather_temperature_2m":         "temperature_2m (°C)",
            "weather_apparent_temperature":   "apparent_temperature (°C)",
            "weather_relative_humidity_2m":   "relative_humidity_2m (%)",
            "weather_wind_speed_10m":         "wind_speed_10m (km/h)",
            "weather_direct_radiation":       "direct_radiation (W/m²)",
            "weather_cloud_cover":            "cloud_cover (%)",
            "weather_prev_year_temperature":  "Prev_Year_Temp (°C)",
        })
        # Day_Type può stare in extra → viene già espansa come colonna
        if "Day_Type" in fore.columns and "day_type" not in fore.columns:
            fore = fore.rename(columns={"Day_Type": "day_type"})
        return dict(hist=hist, fore=fore,
                    filename=db_data["filename"], is_dummy=False)

    # 2) Fallback CSV
    path = find_latest_file(zone)
    if path:
        raw = pd.read_csv(path, parse_dates=["date"])
        hist = raw[raw["section"] == "historical"].copy()
        fore = raw[raw["section"] == "forecast"].copy()
        hist = hist.rename(columns={"Total Load (GW)": "actual_load", "date": "datetime"})
        fore = fore.rename(columns={"Predicted_Load (GW)": "predicted_load",
                                    "lower_bound": "lower_bound",
                                    "upper_bound": "upper_bound",
                                    "Day_Type": "day_type",
                                    "date": "datetime"})
        hist = hist.sort_values("datetime").reset_index(drop=True)
        fore = fore.sort_values("datetime").reset_index(drop=True)
        return dict(hist=hist, fore=fore, filename=os.path.basename(path), is_dummy=False)

    rng = np.random.default_rng(seed=abs(hash(zone)) % 2 ** 32)
    base = {"NORD": 23, "CNOR": 13, "CSUD": 12, "SUD": 13, "CALA": 4, "SICI": 5, "SARD": 3, "ITALY": 78}.get(zone, 12.0)
    dates_h = pd.date_range("2026-06-27", periods=672, freq="15min")
    dates_f = pd.date_range("2026-07-04", periods=672, freq="15min")
    h = np.arange(672) % 96
    curve = lambda d: (
            base + 2.5 * np.exp(-((h / 4 - 9) ** 2) / 18) + 3.0 * np.exp(-((h / 4 - 20) ** 2) / 12)
            - 1.8 * np.exp(-((h / 4 - 4) ** 2) / 10))
    cv_h = curve(dates_h)
    cv_f = curve(dates_f)
    hist_df = pd.DataFrame({
        "datetime": dates_h,
        "actual_load": np.clip(cv_h + rng.normal(0, base * 0.018, 672), 0, None).round(3),
        "temperature_2m (°C)": rng.uniform(18, 32, 672).round(2),
        "relative_humidity_2m (%)": rng.uniform(40, 80, 672).round(1),
        "Prev_Year_Load (GW)": np.clip(cv_h + rng.normal(0, base * 0.04, 672), 0, None).round(3),
        "Prev_Year_Temp (°C)": rng.uniform(17, 31, 672).round(2),
    })
    fore_df = pd.DataFrame({
        "datetime": dates_f,
        "predicted_load": np.clip(cv_f + rng.normal(0, base * 0.012, 672), 0, None).round(3),
        "lower_bound": np.clip(cv_f * 0.94, 0, None).round(3),
        "upper_bound": np.clip(cv_f * 1.06, 0, None).round(3),
        "day_type": ["festivo" if d.weekday() >= 5 else "feriale" for d in dates_f],
        "Prev_Year_Load (GW)": np.clip(cv_f + rng.normal(0, base * 0.04, 672), 0, None).round(3),
        "Prev_Year_Temp (°C)": rng.uniform(17, 31, 672).round(2),
    })
    return dict(hist=hist_df, fore=fore_df, filename="[SIMULATO]", is_dummy=True)


@st.cache_data(ttl=120, show_spinner=False)
def get_gw_labels() -> dict:
    out = {}
    for z in ZONE_ORDER + ["ITALY"]:
        d = load_zone_data(z)
        val = d["fore"]["predicted_load"].mean()
        out[z] = f"{val:.1f} GW"
    return out


# ── DATA LAYER – PV CAPACITY (CSV TERNA) ──────────────────────────────────────
@st.cache_data(ttl=120, show_spinner=False)
def load_pv_capacity() -> dict:
    csv_path = os.path.join(BASE_DIR, "capacity_zona_mensile.csv")
    if not os.path.exists(csv_path):
        csv_path = "capacity_zona_mensile.csv"

    if os.path.exists(csv_path):
        try:
            df = pd.read_csv(csv_path)
            latest_anno = df["anno"].max()
            latest_mese = df[df["anno"] == latest_anno]["mese"].max()
            latest_df = df[(df["anno"] == latest_anno) & (df["mese"] == latest_mese)].copy()

            cap_dict = {}
            for _, row in latest_df.iterrows():
                zone = str(row["zona_mercato"]).strip().upper()
                gw = float(row["capacity_mw"]) / 1000.0
                cap_dict[zone] = round(gw, 1)

            totale_italia_gw = float(latest_df["capacity_mw"].sum()) / 1000.0
            cap_dict["ITALY"] = round(totale_italia_gw, 1)
            return cap_dict
        except Exception:
            pass

    # Fallback se il CSV non è presente
    return {
        "NORD": 22.0, "CNOR": 3.6, "CSUD": 8.4, "SUD": 5.3,
        "CALA": 1.0, "SICI": 4.1, "SARD": 2.1, "ITALY": 46.6,
    }


def find_latest_pv_file(zone: str) -> str | None:
    files = []
    for directory in _candidate_data_dirs():
        files.extend(glob.glob(os.path.join(directory, f"pv_forecast_{zone}_*.csv")))
    files = sorted(set(files), reverse=True)
    return files[0] if files else None


@st.cache_data(ttl=120, show_spinner=False)
def load_pv_data(zone: str) -> dict:
    # 1) Prova DB SQLite
    db_data = _load_from_db("pv", zone)
    if db_data is not None:
        hist = db_data["hist"].rename(columns={
            "actual_gw":    "actual_pv",
            "predicted_gw": "predicted_pv",
            "weather_shortwave_radiation":        "shortwave_radiation",
            "weather_direct_normal_irradiance":   "direct_normal_irradiance",
            "weather_diffuse_radiation":          "diffuse_radiation",
            "weather_direct_radiation":           "direct_radiation",
            "weather_temperature_2m":             "temperature_2m",
            "weather_apparent_temperature":       "apparent_temperature",
            "weather_wind_speed_10m":             "wind_speed_10m",
            "weather_wind_direction_10m":         "wind_direction_10m",
            "weather_cloud_cover":                "cloud_cover",
            "weather_cloud_cover_low":            "cloud_cover_low",
            "weather_cloud_cover_mid":            "cloud_cover_mid",
            "weather_cloud_cover_high":           "cloud_cover_high",
            "weather_precipitation":              "precipitation",
            "weather_snowfall":                   "snowfall",
            "weather_snow_depth":                 "snow_depth",
        })
        fore = db_data["fore"].rename(columns={
            "actual_gw":    "actual_pv",
            "predicted_gw": "predicted_pv",
            "weather_shortwave_radiation":        "shortwave_radiation",
            "weather_direct_normal_irradiance":   "direct_normal_irradiance",
            "weather_diffuse_radiation":          "diffuse_radiation",
            "weather_direct_radiation":           "direct_radiation",
            "weather_temperature_2m":             "temperature_2m",
            "weather_apparent_temperature":       "apparent_temperature",
            "weather_wind_speed_10m":             "wind_speed_10m",
            "weather_wind_direction_10m":         "wind_direction_10m",
            "weather_cloud_cover":                "cloud_cover",
            "weather_cloud_cover_low":            "cloud_cover_low",
            "weather_cloud_cover_mid":            "cloud_cover_mid",
            "weather_cloud_cover_high":           "cloud_cover_high",
            "weather_precipitation":              "precipitation",
            "weather_snowfall":                   "snowfall",
            "weather_snow_depth":                 "snow_depth",
        })
        if "actual_pv" not in hist.columns:
            hist["actual_pv"] = np.nan
        return dict(hist=hist, fore=fore,
                    filename=db_data["filename"], is_dummy=False)

    # 2) Fallback CSV
    path = find_latest_pv_file(zone)
    if path:
        raw = pd.read_csv(path)
        required = {"section", "date"}
        missing = required - set(raw.columns)
        if missing:
            raise ValueError(
                f"CSV PV {os.path.basename(path)} non valido: colonne mancanti {sorted(missing)}"
            )

        raw["date"] = pd.to_datetime(raw["date"], errors="coerce")
        raw = raw.dropna(subset=["date"]).copy()

        hist = raw[raw["section"].eq("historical")].copy()
        fore = raw[raw["section"].eq("forecast")].copy()

        hist = hist.rename(columns={
            "PV_Production (GW)": "actual_pv",
            "date": "datetime",
        })
        fore = fore.rename(columns={
            "Predicted_PV (GW)": "predicted_pv",
            "date": "datetime",
        })

        for df, col in ((hist, "actual_pv"), (fore, "predicted_pv"),
                        (fore, "lower_bound"), (fore, "upper_bound")):
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        hist = hist.sort_values("datetime").reset_index(drop=True)
        fore = fore.sort_values("datetime").reset_index(drop=True)

        if "predicted_pv" not in fore.columns:
            raise ValueError(
                f"CSV PV {os.path.basename(path)} non contiene 'Predicted_PV (GW)'."
            )
        if "actual_pv" not in hist.columns:
            hist["actual_pv"] = np.nan

        return dict(
            hist=hist,
            fore=fore,
            filename=os.path.basename(path),
            is_dummy=False,
        )

    # Dati simulati fallback
    rng = np.random.default_rng(seed=abs(hash(zone)) % 2 ** 32)
    cap_dict = load_pv_capacity()
    cap = cap_dict.get(zone, 10.0)
    dates_h = pd.date_range("2026-06-27", periods=672, freq="15min")
    dates_f = pd.date_range("2026-07-04", periods=672, freq="15min")
    h_idx = np.arange(672) % 96

    noon, width, peak = 48, 20, cap * 0.65
    curve = peak * np.exp(-((h_idx - noon) ** 2) / (2 * width ** 2))
    curve[h_idx < 16] = 0.0
    curve[h_idx > 80] = 0.0

    cv_h = np.clip(curve + rng.normal(0, cap * 0.01, 672), 0, None).round(3)
    cv_f = np.clip(curve + rng.normal(0, cap * 0.01, 672), 0, None).round(3)

    hist_df = pd.DataFrame({"datetime": dates_h, "actual_pv": cv_h})
    fore_df = pd.DataFrame({
        "datetime": dates_f,
        "predicted_pv": cv_f,
        "lower_bound": np.clip(cv_f * 0.90, 0, None).round(3),
        "upper_bound": np.clip(cv_f * 1.10, 0, None).round(3),
        "day_type": ["festivo" if d.weekday() >= 5 else "feriale" for d in dates_f],
    })
    return dict(hist=hist_df, fore=fore_df, filename="[SIMULATO]", is_dummy=True)


@st.cache_data(ttl=120, show_spinner=False)
def get_pv_labels() -> dict:
    out = {}
    for z in ZONE_ORDER + ["ITALY"]:
        d = load_pv_data(z)
        val = d["fore"]["predicted_pv"].max()
        out[z] = f"{val:.1f} GW"
    return out


# ── OVERLAY OPTIONS ───────────────────────────────────────────────────────────
METEO_OPTIONS = {
    "temperature_2m (°C)": dict(label="Temp 2m", unit="°C", color="#ff7f50"),
    "apparent_temperature (°C)": dict(label="Temp percepita", unit="°C", color="#ffa07a"),
    "cloud_cover (%)": dict(label="Copertura nuvole", unit="%", color="#a0a0c0"),
    "wind_speed_10m (km/h)": dict(label="Vento 10m", unit="km/h", color="#90ee90"),
    "direct_radiation (W/m²)": dict(label="Radiazione", unit="W/m²", color="#ffd700"),
    "relative_humidity_2m (%)": dict(label="Umidità", unit="%", color="#87ceeb"),
}

PV_METEO_OPTIONS = {
    "shortwave_radiation": dict(label="Rad. Globale", unit="W/m²", color="#ffd700"),
    "direct_normal_irradiance": dict(label="DNI (Rad. Norm.)", unit="W/m²", color="#ffae19"),
    "diffuse_radiation": dict(label="Rad. Diffusa", unit="W/m²", color="#ff8c00"),
    "direct_radiation": dict(label="Rad. Diretta", unit="W/m²", color="#ffa500"),
    "temperature_2m": dict(label="Temp 2m", unit="°C", color="#ff7f50"),
    "apparent_temperature": dict(label="Temp Percepita", unit="°C", color="#ffa07a"),
    "wind_speed_10m": dict(label="Vento 10m", unit="km/h", color="#90ee90"),
    "cloud_cover": dict(label="Nuvole Totali", unit="%", color="#a0a0c0"),
    "cloud_cover_low": dict(label="Nuvole Basse", unit="%", color="#87ceeb"),
    "cloud_cover_mid": dict(label="Nuvole Medie", unit="%", color="#70a1ff"),
    "cloud_cover_high": dict(label="Nuvole Alte", unit="%", color="#a4b0be"),
    "precipitation": dict(label="Precipitazioni", unit="mm", color="#1e90ff"),
    "snowfall": dict(label="Neve", unit="cm", color="#e0ffff"),
    "snow_depth": dict(label="Altezza Neve", unit="m", color="#f0ffff"),
}

PREV_YEAR_OPTIONS = {
    "Prev_Year_Load (GW)": dict(label="Carico (GW)", unit="GW", color="#6a9fb5", axis="y1"),
    "Prev_Year_Temp (°C)": dict(label="Temperatura (°C)", unit="°C", color="#d28445", axis="y2"),
}


# ── CHART BUILDERS ────────────────────────────────────────────────────────────
def build_chart(
    data: dict,
    zone: str,
    timeframe: str,
    meteo_var: str = None,
    prev_year_vars: list = None,
) -> go.Figure:
    if prev_year_vars is None:
        prev_year_vars = []

    # Recupera il colore dal dizionario ZONE_COLORS
    zc = ZONE_COLORS.get(zone, "#7be2ff")

    if zone == "ITALY":
        color_actual = "#a1a1aa"
        color_forecast = "#ffffff"
        r_band, g_band, b_band = 255, 255, 255
    else:
        color_actual = zc
        color_forecast = zc
        r_band, g_band, b_band = (
            int(zc[1:3], 16),
            int(zc[3:5], 16),
            int(zc[5:7], 16),
        )

    hist = data["hist"].copy()
    fore = data["fore"].copy()
    has_meteo = meteo_var is not None and (
        meteo_var in hist.columns or meteo_var in fore.columns
    )

    if timeframe == "Day":
        hist = hist[hist["datetime"].dt.date == hist["datetime"].dt.date.max()]
        fore = fore[fore["datetime"].dt.date == fore["datetime"].dt.date.min()]

    fig = go.Figure()

    if "day_type" in fore.columns and timeframe == "Week":
        for _, grp in fore.groupby(fore["datetime"].dt.date):
            if grp["day_type"].iloc[0] in ("sabato", "domenica", "festivo"):
                fig.add_vrect(
                    x0=grp["datetime"].iloc[0],
                    x1=grp["datetime"].iloc[-1],
                    fillcolor="rgba(100,80,30,0.10)",
                    line_width=0,
                    layer="below",
                )

    if "lower_bound" in fore.columns and "upper_bound" in fore.columns:
        fig.add_trace(
            go.Scatter(
                x=pd.concat([fore["datetime"], fore["datetime"].iloc[::-1]]),
                y=pd.concat(
                    [fore["upper_bound"], fore["lower_bound"].iloc[::-1]]
                ),
                fill="toself",
                fillcolor=f"rgba({r_band},{g_band},{b_band},0.12)",
                line=dict(color="rgba(0,0,0,0)"),
                hoverinfo="skip",
                name="Conf. band",
                showlegend=True,
                yaxis="y1",
            )
        )

    if "actual_load" in hist.columns:
        fig.add_trace(
            go.Scatter(
                x=hist["datetime"],
                y=hist["actual_load"],
                name="Actual Load",
                line=dict(color=color_actual, width=1.6),
                hovertemplate="%{x|%d/%m %H:%M}<br><b>%{y:.2f} GW</b><extra>Actual</extra>",
                yaxis="y1",
            )
        )

    if not hist.empty and not fore.empty:
        fig.add_vline(
            x=fore["datetime"].iloc[0],
            line_width=1,
            line_dash="dash",
            line_color="rgba(255,255,255,0.15)",
        )
        fig.add_annotation(
            x=fore["datetime"].iloc[0],
            y=1,
            yref="paper",
            text="NOW",
            showarrow=False,
            font=dict(
                color="rgba(255,255,255,0.30)",
                size=8,
                family="Courier New, monospace",
            ),
            xanchor="left",
            yanchor="top",
        )

    fig.add_trace(
        go.Scatter(
            x=fore["datetime"],
            y=fore["predicted_load"],
            name="Forecast Load",
            line=dict(color=color_forecast, width=2.5),
            hovertemplate="%{x|%d/%m %H:%M}<br><b>%{y:.2f} GW</b><extra>Forecast</extra>",
            yaxis="y1",
        )
    )

    if not fore.empty:
        idx = fore["predicted_load"].idxmax()
        pval = fore["predicted_load"].max()
        fig.add_annotation(
            x=fore.loc[idx, "datetime"],
            y=pval,
            text=f"<b>{pval:.1f} GW</b>",
            showarrow=True,
            arrowhead=2,
            arrowcolor=color_forecast,
            arrowwidth=1.2,
            ax=0,
            ay=-28,
            font=dict(
                color=color_forecast, size=10, family="Courier New, monospace"
            ),
            bgcolor="rgba(0,0,0,0.65)",
            bordercolor=color_forecast,
            borderwidth=1,
            borderpad=3,
            yref="y1",
        )

    if has_meteo:
        mc = METEO_OPTIONS[meteo_var]
        m_hist = (
            hist[["datetime", meteo_var]].dropna()
            if meteo_var in hist.columns
            else pd.DataFrame()
        )
        m_fore = (
            fore[["datetime", meteo_var]].dropna()
            if meteo_var in fore.columns
            else pd.DataFrame()
        )
        m_all = pd.concat([m_hist, m_fore]).sort_values("datetime")
        fig.add_trace(
            go.Scatter(
                x=m_all["datetime"],
                y=m_all[meteo_var],
                name=mc["label"],
                line=dict(color=mc["color"], width=1.4, dash="dot"),
                opacity=0.85,
                hovertemplate=f"%{{x|%d/%m %H:%M}}<br><b>%{{y:.1f}} {mc['unit']}</b><extra>{mc['label']}</extra>",
                yaxis="y2",
            )
        )

    has_prev_temp = False
    for p_var in prev_year_vars:
        if p_var in hist.columns or p_var in fore.columns:
            pc = PREV_YEAR_OPTIONS[p_var]
            p_hist = (
                hist[["datetime", p_var]].dropna()
                if p_var in hist.columns
                else pd.DataFrame()
            )
            p_fore = (
                fore[["datetime", p_var]].dropna()
                if p_var in fore.columns
                else pd.DataFrame()
            )
            p_all = pd.concat([p_hist, p_fore]).sort_values("datetime")
            if pc["axis"] == "y2":
                has_prev_temp = True
            fig.add_trace(
                go.Scatter(
                    x=p_all["datetime"],
                    y=p_all[p_var],
                    name=pc["label"],
                    line=dict(color=pc["color"], width=1.5, dash="dash"),
                    opacity=0.85,
                    hovertemplate=f"%{{x|%d/%m %H:%M}}<br><b>%{{y:.2f}} {pc['unit']}</b><extra>{pc['label']}</extra>",
                    yaxis=pc["axis"],
                )
            )

    show_axis_2 = has_meteo or has_prev_temp
    right_margin = 55 if show_axis_2 else 16
    y2_labels = []
    y2_color = "#8b949e"
    if has_meteo:
        y2_labels.append(
            f"{METEO_OPTIONS[meteo_var]['label']} ({METEO_OPTIONS[meteo_var]['unit']})"
        )
        y2_color = METEO_OPTIONS[meteo_var]["color"]
    if has_prev_temp:
        pc_temp = PREV_YEAR_OPTIONS["Prev_Year_Temp (°C)"]
        y2_labels.append(f"{pc_temp['label']} ({pc_temp['unit']})")
        if not has_meteo:
            y2_color = pc_temp["color"]

    fig.update_layout(
        paper_bgcolor="#10161d",
        plot_bgcolor="#10161d",
        margin=dict(l=50, r=right_margin, t=14, b=36),
        height=330,
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor="#161b22",
            bordercolor="#21262d",
            font=dict(
                color="#e6edf3", size=11, family="Courier New, monospace"
            ),
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.03,
            xanchor="right",
            x=1,
            font=dict(color="#8b949e", size=10, family="Courier New, monospace"),
            bgcolor="rgba(0,0,0,0)",
        ),
        xaxis=dict(
            gridcolor="#1e2630",
            showgrid=True,
            zeroline=False,
            tickformat="%d/%m\n%H:%M",
            tickfont=dict(
                color="#8b949e", size=9, family="Courier New, monospace"
            ),
        ),
        yaxis=dict(
            title=dict(
                text="Load (GW)",
                font=dict(
                    color="#8b949e", size=10, family="Courier New, monospace"
                ),
            ),
            gridcolor="#1e2630",
            showgrid=True,
            zeroline=False,
            tickfont=dict(
                color="#8b949e", size=9, family="Courier New, monospace"
            ),
        ),
        yaxis2=dict(
            title=dict(
                text=" / ".join(y2_labels) if show_axis_2 else "",
                font=dict(
                    color=y2_color, size=10, family="Courier New, monospace"
                ),
            ),
            overlaying="y",
            side="right",
            showgrid=False,
            zeroline=False,
            tickfont=dict(
                color=y2_color, size=9, family="Courier New, monospace"
            ),
            visible=show_axis_2,
        ),
    )
    return fig


def build_pv_chart(
    data: dict, zone: str, timeframe: str, meteo_var: str = None
) -> go.Figure:
    # Usa rigorosamente ZONE_COLORS
    zc = ZONE_COLORS.get(zone, "#7be2ff")

    if zone == "ITALY":
        color_actual = "#a1a1aa"
        color_forecast = "#ffffff"
        r_band, g_band, b_band = 255, 255, 255
    else:
        color_actual = zc
        color_forecast = zc
        r_band, g_band, b_band = (
            int(zc[1:3], 16),
            int(zc[3:5], 16),
            int(zc[5:7], 16),
        )

    hist = data["hist"].copy()
    fore = data["fore"].copy()
    has_meteo = meteo_var is not None and (
        meteo_var in hist.columns or meteo_var in fore.columns
    )

    if timeframe == "Day":
        hist = hist[hist["datetime"].dt.date == hist["datetime"].dt.date.max()]
        fore = fore[fore["datetime"].dt.date == fore["datetime"].dt.date.min()]

    fig = go.Figure()

    if "day_type" in fore.columns and timeframe == "Week":
        for _, grp in fore.groupby(fore["datetime"].dt.date):
            if grp["day_type"].iloc[0] in ("sabato", "domenica", "festivo"):
                fig.add_vrect(
                    x0=grp["datetime"].iloc[0],
                    x1=grp["datetime"].iloc[-1],
                    fillcolor="rgba(80,70,10,0.12)",
                    line_width=0,
                    layer="below",
                )

    if "lower_bound" in fore.columns and "upper_bound" in fore.columns:
        fig.add_trace(
            go.Scatter(
                x=pd.concat([fore["datetime"], fore["datetime"].iloc[::-1]]),
                y=pd.concat(
                    [fore["upper_bound"], fore["lower_bound"].iloc[::-1]]
                ),
                fill="toself",
                fillcolor=f"rgba({r_band},{g_band},{b_band},0.12)",
                line=dict(color="rgba(0,0,0,0)"),
                hoverinfo="skip",
                name="Conf. band",
                showlegend=True,
                yaxis="y1",
            )
        )

    if "actual_pv" in hist.columns:
        fig.add_trace(
            go.Scatter(
                x=hist["datetime"],
                y=hist["actual_pv"],
                name="Actual PV",
                line=dict(color=color_actual, width=1.6),
                hovertemplate="%{x|%d/%m %H:%M}<br><b>%{y:.3f} GW</b><extra>Actual PV</extra>",
                yaxis="y1",
            )
        )

    if not hist.empty and not fore.empty:
        fig.add_vline(
            x=fore["datetime"].iloc[0],
            line_width=1,
            line_dash="dash",
            line_color="rgba(255,255,255,0.15)",
        )
        fig.add_annotation(
            x=fore["datetime"].iloc[0],
            y=1,
            yref="paper",
            text="NOW",
            showarrow=False,
            font=dict(
                color="rgba(255,255,255,0.30)",
                size=8,
                family="Courier New, monospace",
            ),
            xanchor="left",
            yanchor="top",
        )

    fig.add_trace(
        go.Scatter(
            x=fore["datetime"],
            y=fore["predicted_pv"],
            name="Forecast PV",
            line=dict(color=color_forecast, width=2.5),
            hovertemplate="%{x|%d/%m %H:%M}<br><b>%{y:.3f} GW</b><extra>Forecast PV</extra>",
            yaxis="y1",
        )
    )

    if not fore.empty and fore["predicted_pv"].max() > 0:
        idx = fore["predicted_pv"].idxmax()
        pval = fore["predicted_pv"].max()
        fig.add_annotation(
            x=fore.loc[idx, "datetime"],
            y=pval,
            text=f"<b>{pval:.2f} GW</b>",
            showarrow=True,
            arrowhead=2,
            arrowcolor=color_forecast,
            arrowwidth=1.2,
            ax=0,
            ay=-28,
            font=dict(
                color=color_forecast, size=10, family="Courier New, monospace"
            ),
            bgcolor="rgba(0,0,0,0.65)",
            bordercolor=color_forecast,
            borderwidth=1,
            borderpad=3,
            yref="y1",
        )

    if has_meteo:
        mc = PV_METEO_OPTIONS[meteo_var]
        m_hist = (
            hist[["datetime", meteo_var]].dropna()
            if meteo_var in hist.columns
            else pd.DataFrame()
        )
        m_fore = (
            fore[["datetime", meteo_var]].dropna()
            if meteo_var in fore.columns
            else pd.DataFrame()
        )
        m_all = pd.concat([m_hist, m_fore]).sort_values("datetime")
        fig.add_trace(
            go.Scatter(
                x=m_all["datetime"],
                y=m_all[meteo_var],
                name=mc["label"],
                line=dict(color=mc["color"], width=1.4, dash="dot"),
                opacity=0.85,
                hovertemplate=f"%{{x|%d/%m %H:%M}}<br><b>%{{y:.1f}} {mc['unit']}</b><extra>{mc['label']}</extra>",
                yaxis="y2",
            )
        )

    show_axis_2 = has_meteo
    right_margin = 55 if show_axis_2 else 16
    y2_label = ""
    y2_color = "#8b949e"
    if has_meteo:
        mc_info = PV_METEO_OPTIONS[meteo_var]
        y2_label = f"{mc_info['label']} ({mc_info['unit']})"
        y2_color = mc_info["color"]

    fig.update_layout(
        paper_bgcolor="#10161d",
        plot_bgcolor="#10161d",
        margin=dict(l=50, r=right_margin, t=14, b=36),
        height=330,
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor="#161b22",
            bordercolor="#21262d",
            font=dict(
                color="#e6edf3", size=11, family="Courier New, monospace"
            ),
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.03,
            xanchor="right",
            x=1,
            font=dict(color="#8b949e", size=10, family="Courier New, monospace"),
            bgcolor="rgba(0,0,0,0)",
        ),
        xaxis=dict(
            gridcolor="#1e2630",
            showgrid=True,
            zeroline=False,
            tickformat="%d/%m\n%H:%M",
            tickfont=dict(
                color="#8b949e", size=9, family="Courier New, monospace"
            ),
        ),
        yaxis=dict(
            title=dict(
                text="Production (GW)",
                font=dict(
                    color="#8b949e", size=10, family="Courier New, monospace"
                ),
            ),
            gridcolor="#1e2630",
            showgrid=True,
            zeroline=False,
            rangemode="tozero",
            tickfont=dict(
                color="#8b949e", size=9, family="Courier New, monospace"
            ),
        ),
        yaxis2=dict(
            title=dict(
                text=y2_label,
                font=dict(
                    color=y2_color, size=10, family="Courier New, monospace"
                ),
            ),
            overlaying="y",
            side="right",
            showgrid=False,
            zeroline=False,
            tickfont=dict(
                color=y2_color, size=9, family="Courier New, monospace"
            ),
            visible=show_axis_2,
        ),
    )
    return fig

# ══════════════════════════════════════════════════════════════════════════════
#  DASHBOARD – LOAD
# ══════════════════════════════════════════════════════════════════════════════
def render_load_dashboard():
    st.markdown("""
    <div class="t-app-header">
      <div class="t-app-logo">
        <span>⚡</span> TERNA &nbsp;|&nbsp;
        <span style="font-weight:400;color:#8b949e">PIATTAFORMA PREVISIONE CARICO ZONALE ITALIA</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    left_col, right_col = st.columns([4, 8], gap="small")

    with left_col:
        st.markdown("<p class='t-panel-title' style='margin-top:8px'>SELEZIONE RAPIDA</p>",
                    unsafe_allow_html=True)

        zone_options = ["ITALY"] + ZONE_ORDER
        chosen_zone = st.segmented_control(
            label="selezione_zona",
            options=zone_options,
            format_func=lambda z: "🇮🇹 ITALIA" if z == "ITALY" else z,
            default=st.session_state.selected_zone,
            selection_mode="single",
            key="zone_toggle",
            label_visibility="collapsed",
        )
        if chosen_zone is not None:
            st.session_state.selected_zone = chosen_zone
        else:
            st.session_state.selected_zone = "ITALY"

        st.write("---")

        active_zone = st.session_state.selected_zone
        map_path = os.path.join(BASE_DIR, "maps", f"plot_{active_zone.lower()}.png")
        try:
            st.image(map_path, use_container_width=True)
        except Exception:
            st.error(f"⚠️ Mappa non trovata: {map_path}")

    with right_col:
        zone = st.session_state.selected_zone
        zc = ZONE_COLORS.get(zone, "#7be2ff")
        data = load_zone_data(zone)
        hist = data["hist"]
        fore = data["fore"]

        all_dates = pd.concat([hist["datetime"], fore["datetime"]])
        date_start = all_dates.min().strftime("%b %d")
        date_end = all_dates.max().strftime("%b %d, %Y")
        fore_start = fore["datetime"].min().strftime("%b %d")
        fore_end = fore["datetime"].max().strftime("%b %d")

        lbl_sim = (f"<span class='t-tag' style='color:#e74c3c; border-color:#e74c3c'>⚠ SIMULATO</span>"
                   if data["is_dummy"] else "")
        lbl_src = f"<span class='t-tag'>SRC: {data['filename']}</span>"

        st.markdown(f"""
        <div class="t-info-strip">
          <div>ZONAL ELECTRICITY LOAD FORECAST: <span style="color:{zc}; font-weight:700;">{zone}</span></div>
          <div style="display:flex; align-items:center;">
            <span>📅 {date_start} – {date_end}</span>
            {lbl_src}{lbl_sim}
          </div>
        </div>
        """, unsafe_allow_html=True)

        ctrl_tf, ctrl_meteo, ctrl_prev = st.columns([3, 5, 4])

        with ctrl_tf:
            st.markdown(
                "<p style='font-family:Courier New,monospace;font-size:9px;color:#8b949e;margin-bottom:2px'>TIMEFRAME</p>",
                unsafe_allow_html=True)
            chosen_tf = st.segmented_control(
                label="timeframe", options=["Week", "Day"],
                default=st.session_state.timeframe,
                selection_mode="single", key="tf_toggle",
                label_visibility="collapsed")
            st.session_state.timeframe = chosen_tf if chosen_tf is not None else "Week"

        with ctrl_meteo:
            st.markdown(
                "<p style='font-family:Courier New,monospace;font-size:9px;color:#8b949e;margin-bottom:2px'>OVERLAY METEO</p>",
                unsafe_allow_html=True)
            chosen = st.segmented_control(
                label="meteo", options=list(METEO_OPTIONS.keys()),
                format_func=lambda k: METEO_OPTIONS[k]["label"],
                default=st.session_state.meteo_var,
                selection_mode="single", key="meteo_toggle",
                label_visibility="collapsed")
            st.session_state.meteo_var = chosen

        with ctrl_prev:
            st.markdown(
                "<p style='font-family:Courier New,monospace;font-size:9px;color:#8b949e;margin-bottom:2px'>PREVIOUS YEAR DATA</p>",
                unsafe_allow_html=True)
            chosen_prev = st.segmented_control(
                label="prev_year", options=list(PREV_YEAR_OPTIONS.keys()),
                format_func=lambda k: PREV_YEAR_OPTIONS[k]["label"],
                default=st.session_state.prev_year_vars,
                selection_mode="multi", key="prev_year_toggle",
                label_visibility="collapsed")
            st.session_state.prev_year_vars = chosen_prev if chosen_prev is not None else []

        st.markdown("<hr>", unsafe_allow_html=True)

        p_max = fore["predicted_load"].max()
        p_min = fore["predicted_load"].min()
        p_avg = fore["predicted_load"].mean()
        last_actual = hist["actual_load"].dropna().iloc[-1] if not hist.empty else None
        first_fore = fore["predicted_load"].iloc[0]
        delta = (last_actual - first_fore) if last_actual is not None else 0.0
        d_cl = "pos" if delta >= 0 else "neg"
        d_s = f"{'+' if delta >= 0 else ''}{delta:.2f}"
        interval_str = (f"±{(fore['upper_bound'] - fore['lower_bound']).mean() / 2:.2f}"
                        if "upper_bound" in fore.columns else "—")

        st.markdown(f"""
        <div class="t-kpi-container">
          <div class="t-kpi-card">
            <div class="t-kpi-label">MAX FORECAST (GW)</div>
            <div class="t-kpi-value" style="color:{zc}">{p_max:.1f}</div>
          </div>
          <div class="t-kpi-card">
            <div class="t-kpi-label">MIN FORECAST (GW)</div>
            <div class="t-kpi-value" style="color:{zc}">{p_min:.1f}</div>
          </div>
          <div class="t-kpi-card">
            <div class="t-kpi-label">AVG FORECAST (GW)</div>
            <div class="t-kpi-value" style="color:{zc}">{p_avg:.1f}</div>
          </div>
          <div class="t-kpi-card">
            <div class="t-kpi-label">ACTUAL vs FORECAST</div>
            <div class="t-kpi-value"><span class="{d_cl}">{d_s}</span><span style="font-size:11px;color:#8b949e"> GW</span></div>
          </div>
        </div>""", unsafe_allow_html=True)

        tf = st.session_state.timeframe
        st.markdown(
            f"<div class='t-chart-title'>{'WEEKLY' if tf == 'Week' else 'DAILY'} LOAD FORECAST ({zone})"
            f" · FORECAST WINDOW: {fore_start} – {fore_end}</div>",
            unsafe_allow_html=True)

        st.plotly_chart(
            build_chart(data, zone, tf, st.session_state.meteo_var, st.session_state.prev_year_vars),
            use_container_width=True, config={"displayModeBar": False})

        today_dt = fore["datetime"].dt.date.min()
        fore_today = fore[fore["datetime"].dt.date == today_dt]
        t_max = fore_today["predicted_load"].max()
        t_min = fore_today["predicted_load"].min()
        t_avg = fore_today["predicted_load"].mean()
        today_label = fore_today["datetime"].iloc[0].strftime("%b %d").upper()

        hist_avg = hist["actual_load"].mean() if not hist.empty else p_avg
        dw = (p_avg / hist_avg - 1) * 100 if hist_avg > 0 else 0.0
        dw_cl = "pos" if dw >= 0 else "neg"

        merged = pd.merge(hist[["datetime", "actual_load"]].dropna(),
                          fore[["datetime", "predicted_load"]], on="datetime", how="inner")
        if len(merged) > 5:
            ss_res = ((merged["actual_load"] - merged["predicted_load"]) ** 2).sum()
            ss_tot = ((merged["actual_load"] - merged["actual_load"].mean()) ** 2).sum()
            r2_val = max(0, 1 - ss_res / ss_tot) if ss_tot > 0 else float("nan")
            r2_str = f"R²: {r2_val:.3f}"
        else:
            r2_str = "—"

        st.markdown(f"""
        <div class="t-bottom-grid">
          <div class="t-bottom-card">
            <div class="t-bottom-label">TODAY'S FORECAST ({today_label}):</div>
            <div class="t-bottom-vals">
              MAX&nbsp;<b style="color:{zc}">{t_max:.1f}</b> GW &nbsp;|&nbsp;
              MIN&nbsp;<b style="color:{zc}">{t_min:.1f}</b> GW &nbsp;|&nbsp;
              AVG&nbsp;<b style="color:{zc}">{t_avg:.1f}</b> GW
            </div>
          </div>
          <div class="t-bottom-card">
            <div class="t-bottom-label">KEY METRICS ({zone}):</div>
            <div class="t-metrics-flex">
              <div>
                <div class="t-flex-val {dw_cl}">{'+' if dw >= 0 else ''}{dw:.1f}%</div>
                <div class="t-flex-sub">forecast vs hist avg</div>
              </div>
              <div>
                <div class="t-flex-val" style="color:#8b949e">{interval_str} GW</div>
                <div class="t-flex-sub">avg conf. interval</div>
              </div>
              <div>
                <div class="t-flex-val" style="color:{zc}">{r2_str}</div>
                <div class="t-flex-sub">model fit accuracy</div>
              </div>
            </div>
          </div>
        </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  DASHBOARD – PV
# ══════════════════════════════════════════════════════════════════════════════
def render_pv_dashboard():
    st.markdown("""
    <div class="t-app-header">
      <div class="t-app-logo">
        <span class="pv">☀️</span> TERNA &nbsp;|&nbsp;
        <span style="font-weight:400;color:#8b949e">PIATTAFORMA PREVISIONE PRODUZIONE FOTOVOLTAICA ITALIA</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    pv_capacity_data = load_pv_capacity()

    left_col, right_col = st.columns([4, 8], gap="small")

    with left_col:
        st.markdown("<p class='t-panel-title' style='margin-top:8px'>SELEZIONE RAPIDA</p>",
                    unsafe_allow_html=True)

        zone_options = ["ITALY"] + ZONE_ORDER
        chosen_zone = st.segmented_control(
            label="selezione_zona_pv",
            options=zone_options,
            format_func=lambda z: "🇮🇹 ITALIA" if z == "ITALY" else z,
            default=st.session_state.pv_zone,
            selection_mode="single",
            key="pv_zone_toggle",
            label_visibility="collapsed",
        )
        if chosen_zone is not None:
            st.session_state.pv_zone = chosen_zone
        else:
            st.session_state.pv_zone = "ITALY"

        st.write("---")

        active_zone = st.session_state.pv_zone
        cap_gw = pv_capacity_data.get(active_zone, 0.0)
        pv_color = PV_ZONE_COLORS.get(active_zone, "#ffd700")
        st.markdown(f"""
        <div style="background:#161b22;border:1px solid #21262d;border-radius:5px;
                    padding:10px 12px;margin-bottom:8px;font-family:'Courier New',monospace">
          <div style="font-size:9px;color:#8b949e;letter-spacing:.08em;margin-bottom:4px">
            CAPACITÀ INSTALLATA</div>
          <div style="font-size:22px;font-weight:700;color:{pv_color}">{cap_gw:.1f} GW<sub style="font-size:12px;color:#8b949e">p</sub></div>
          <div style="font-size:8px;color:#8b949e;margin-top:2px">fonte: TERNA</div>
        </div>
        """, unsafe_allow_html=True)

        map_path = os.path.join(BASE_DIR, "maps", f"plot_{active_zone.lower()}.png")
        try:
            st.image(map_path, use_container_width=True)
        except Exception:
            st.warning(f"Mappa non disponibile: {map_path}")

    with right_col:
        zone = st.session_state.pv_zone
        zc = PV_ZONE_COLORS.get(zone, "#ffd700")
        data = load_pv_data(zone)
        hist = data["hist"]
        fore = data["fore"]

        all_dates = pd.concat([hist["datetime"], fore["datetime"]])
        date_start = all_dates.min().strftime("%b %d")
        date_end = all_dates.max().strftime("%b %d, %Y")
        fore_start = fore["datetime"].min().strftime("%b %d")
        fore_end = fore["datetime"].max().strftime("%b %d")

        lbl_sim = (f"<span class='t-tag' style='color:#e74c3c; border-color:#e74c3c'>⚠ SIMULATO</span>"
                   if data["is_dummy"] else "")
        lbl_src = f"<span class='t-tag'>SRC: {data['filename']}</span>"

        st.markdown(f"""
        <div class="t-info-strip">
          <div>☀️ PV PRODUCTION FORECAST: <span style="color:{zc}; font-weight:700;">{zone}</span></div>
          <div style="display:flex; align-items:center;">
            <span>📅 {date_start} – {date_end}</span>
            {lbl_src}{lbl_sim}
          </div>
        </div>
        """, unsafe_allow_html=True)

        ctrl_tf, ctrl_meteo = st.columns([3, 9])

        with ctrl_tf:
            st.markdown(
                "<p style='font-family:Courier New,monospace;font-size:9px;color:#8b949e;margin-bottom:2px'>TIMEFRAME</p>",
                unsafe_allow_html=True)
            chosen_tf = st.segmented_control(
                label="pv_timeframe", options=["Week", "Day"],
                default=st.session_state.pv_timeframe,
                selection_mode="single", key="pv_tf_toggle",
                label_visibility="collapsed")
            st.session_state.pv_timeframe = chosen_tf if chosen_tf is not None else "Week"

        with ctrl_meteo:
            st.markdown(
                "<p style='font-family:Courier New,monospace;font-size:9px;color:#8b949e;margin-bottom:2px'>OVERLAY METEO (CSV FEATURES)</p>",
                unsafe_allow_html=True)
            chosen_pv_meteo = st.segmented_control(
                label="pv_meteo", options=list(PV_METEO_OPTIONS.keys()),
                format_func=lambda k: PV_METEO_OPTIONS[k]["label"],
                default=st.session_state.pv_meteo_var,
                selection_mode="single", key="pv_meteo_toggle",
                label_visibility="collapsed")
            st.session_state.pv_meteo_var = chosen_pv_meteo

        st.markdown("<hr>", unsafe_allow_html=True)

        p_peak = fore["predicted_pv"].max()
        p_avg = fore["predicted_pv"].mean()
        e_tot = fore["predicted_pv"].sum() * 0.25
        last_actual_pv = hist["actual_pv"].dropna().iloc[-1] if not hist.empty else None
        first_fore_pv = fore["predicted_pv"].iloc[0]
        delta_pv = (last_actual_pv - first_fore_pv) if last_actual_pv is not None else 0.0
        d_cl_pv = "pos" if delta_pv >= 0 else "neg"
        d_s_pv = f"{'+' if delta_pv >= 0 else ''}{delta_pv:.3f}"

        st.markdown(f"""
        <div class="t-kpi-container">
          <div class="t-kpi-card">
            <div class="t-kpi-label">PEAK FORECAST (GW)</div>
            <div class="t-kpi-value" style="color:{zc}">{p_peak:.2f}</div>
          </div>
          <div class="t-kpi-card">
            <div class="t-kpi-label">AVG PRODUCTION (GW)</div>
            <div class="t-kpi-value" style="color:{zc}">{p_avg:.2f}</div>
          </div>
          <div class="t-kpi-card">
            <div class="t-kpi-label">ENERGIA TOTALE (GWh)</div>
            <div class="t-kpi-value" style="color:{zc}">{e_tot:.1f}</div>
          </div>
          <div class="t-kpi-card">
            <div class="t-kpi-label">ACTUAL vs FORECAST</div>
            <div class="t-kpi-value"><span class="{d_cl_pv}">{d_s_pv}</span><span style="font-size:11px;color:#8b949e"> GW</span></div>
          </div>
        </div>""", unsafe_allow_html=True)

        tf_pv = st.session_state.pv_timeframe

        st.markdown(
            f"<div class='t-chart-title'>{'WEEKLY' if tf_pv == 'Week' else 'DAILY'} PV FORECAST ({zone})"
            f" · FORECAST WINDOW: {fore_start} – {fore_end}</div>",
            unsafe_allow_html=True)

        st.plotly_chart(
            build_pv_chart(data, zone, tf_pv, st.session_state.pv_meteo_var),
            use_container_width=True, config={"displayModeBar": False})

        today_dt = fore["datetime"].dt.date.min()
        fore_today = fore[fore["datetime"].dt.date == today_dt]
        t_peak = fore_today["predicted_pv"].max()
        t_avg = fore_today["predicted_pv"].mean()
        t_energy = fore_today["predicted_pv"].sum() * 0.25
        today_label = fore_today["datetime"].iloc[0].strftime("%b %d").upper()

        interval_str = (f"±{(fore['upper_bound'] - fore['lower_bound']).mean() / 2:.3f}"
                        if "upper_bound" in fore.columns else "—")

        cap = pv_capacity_data.get(zone, 1.0)
        cf = (p_avg / cap * 100) if cap > 0 else 0.0

        st.markdown(f"""
        <div class="t-bottom-grid">
          <div class="t-bottom-card">
            <div class="t-bottom-label">TODAY'S PV FORECAST ({today_label}):</div>
            <div class="t-bottom-vals">
              PEAK&nbsp;<b style="color:{zc}">{t_peak:.2f}</b> GW &nbsp;|&nbsp;
              AVG&nbsp;<b style="color:{zc}">{t_avg:.2f}</b> GW &nbsp;|&nbsp;
              ENERGIA&nbsp;<b style="color:{zc}">{t_energy:.1f}</b> GWh
            </div>
          </div>
          <div class="t-bottom-card">
            <div class="t-bottom-label">KEY METRICS PV ({zone}):</div>
            <div class="t-metrics-flex">
              <div>
                <div class="t-flex-val" style="color:{zc}">{cf:.1f}%</div>
                <div class="t-flex-sub">capacity factor medio</div>
              </div>
              <div>
                <div class="t-flex-val" style="color:#8b949e">{interval_str} GW</div>
                <div class="t-flex-sub">avg conf. interval</div>
              </div>
              <div>
                <div class="t-flex-val" style="color:{zc}">{cap:.1f} GW<span style="font-size:10px">p</span></div>
                <div class="t-flex-sub">capacità installata</div>
              </div>
            </div>
          </div>
        </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  ROUTER PRINCIPALE
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.dashboard_mode == "LOAD":
    render_load_dashboard()
else:
    render_pv_dashboard()