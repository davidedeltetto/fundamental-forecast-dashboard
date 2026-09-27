import streamlit as st
import pandas as pd
import numpy as np
import os, glob
import datetime
import plotly.graph_objects as go

# ── I18N ─────────────────────────────────────────────────────────────────────
if "lang" not in st.session_state:
    st.session_state.lang = "it"

TR = {
    "it": {
        "app_title": "Piattaforma Previsioni Elettriche",
        "app_brand": "PREVISIONI ENERGIA",
        "nav_load": "CARICO",
        "nav_pv": "PV",
        "nav_comparison": "CONFRONTO",
        "nav_load_help": "Previsione carico elettrico zonale",
        "nav_pv_help": "Previsione produzione fotovoltaica zonale",
        "nav_comparison_help": "Confronto previsione vs reale e analisi accuratezza",
        "mode_suffix": "MODALITÀ",
        "err_missing_credentials": "credenziali mancanti",
        "err_client_creation": "errore creazione client: {e}",
        "err_no_run": "nessun run per model={model} zone={zone}",
        "err_zero_records": "run_id={run_id} esiste ma 0 record",
        "err_query": "errore query: {e}",
        "err_comparison_query": "errore query confronto: {e}",
        "quick_selection": "SELEZIONE RAPIDA",
        "italy_flag_label": "🇮🇹 ITALIA",
        "timeframe_label": "PERIODO",
        "timeframe_week": "Settimana",
        "timeframe_day": "Giorno",
        "weather_overlay_label": "OVERLAY METEO",
        "weather_overlay_csv_label": "OVERLAY METEO (CSV FEATURES)",
        "prev_year_label": "DATI ANNO PRECEDENTE",
        "map_not_found": "⚠️ Mappa non trovata: {path}",
        "map_not_available": "Mappa non disponibile: {path}",
        "src_label": "FONTE",
        "simulated_badge": "SIMULATO",
        "simulated_data": "dati simulati",
        "load_header_section": "CARICO",
        "load_header_subtitle": "PIATTAFORMA PREVISIONE CARICO ZONALE ITALIA",
        "load_info_strip_title": "PREVISIONE CARICO ELETTRICO ZONALE:",
        "kpi_max_forecast": "PREVISIONE MAX (GW)",
        "kpi_min_forecast": "PREVISIONE MIN (GW)",
        "kpi_avg_forecast": "PREVISIONE MEDIA (GW)",
        "chart_title_weekly_load": "PREVISIONE CARICO SETTIMANALE",
        "chart_title_daily_load": "PREVISIONE CARICO GIORNALIERA",
        "forecast_window_label": "FINESTRA DI PREVISIONE",
        "today_forecast_label": "PREVISIONE DI OGGI",
        "key_metrics_label": "METRICHE CHIAVE",
        "caption_forecast_vs_hist": "previsione vs media storica",
        "caption_avg_conf_interval": "intervallo di confidenza medio",
        "caption_model_fit": "accuratezza del modello",
        "yaxis_load": "Carico (GW)",
        "pv_header_section": "PV",
        "pv_header_subtitle": "PIATTAFORMA PREVISIONE PRODUZIONE FOTOVOLTAICA ITALIA",
        "installed_capacity_label": "CAPACITÀ INSTALLATA",
        "pv_info_strip_title": "PREVISIONE PRODUZIONE FOTOVOLTAICA:",
        "kpi_peak_forecast": "PICCO PREVISTO (GW)",
        "kpi_avg_production": "PRODUZIONE MEDIA (GW)",
        "kpi_total_energy": "ENERGIA TOTALE (GWh)",
        "chart_title_weekly_pv": "PREVISIONE PV SETTIMANALE",
        "chart_title_daily_pv": "PREVISIONE PV GIORNALIERA",
        "today_pv_forecast_label": "PREVISIONE PV DI OGGI",
        "key_metrics_pv_label": "METRICHE CHIAVE PV",
        "caption_capacity_factor": "capacity factor medio",
        "caption_installed_capacity": "capacità installata",
        "yaxis_production": "Produzione (GW)",
        "label_energy": "ENERGIA",
        "cmp_header_section": "CONFRONTO",
        "cmp_header_subtitle": "PREVISIONE VS REALE & ANALISI ACCURATEZZA",
        "resource_label": "RISORSA",
        "model_load_label": "⚡ CARICO",
        "model_pv_label": "☀️ PV",
        "time_horizon_label": "ORIZZONTE TEMPORALE",
        "lead_time_emissions_label": "LEAD TIME DELLE EMISSIONI",
        "insufficient_data_msg": (
            "📈 **Ancora poche emissioni storiche per questa analisi.** "
            "Al momento risultano **{n_runs} emissione/i** salvate per {model} · {zone} "
            "(prima: {first_dt}). Un forecast diventa confrontabile con il dato reale solo "
            "quando la sua data target è trascorsa ed è stata osservata da un run successivo — "
            "quindi serve almeno qualche giorno di emissioni consecutive prima che questa pagina "
            "si popoli. Torna a controllare tra un paio di giorni."
        ),
        "ts_comparison_title": "Confronto serie storica (mostra la settimana selezionata)",
        "error_metrics_title": "Metriche di errore (Accuracy Breakdown)",
        "no_obs_caption": "Nessuna osservazione ancora disponibile per i lead time selezionati.",
        "error_by_hour_title": "Errore per Ora del Giorno",
        "error_vs_lead_title": "Errore vs Lead Time",
        "hours_before_suffix": "h prima",
        "hour_hover_label": "Ora",
    },
    "en": {
        "app_title": "Electricity Forecast Platform",
        "app_brand": "ENERGY FORECAST",
        "nav_load": "LOAD",
        "nav_pv": "PV",
        "nav_comparison": "COMPARISON",
        "nav_load_help": "Zonal electric load forecast",
        "nav_pv_help": "Zonal photovoltaic production forecast",
        "nav_comparison_help": "Forecast vs actual comparison and accuracy analysis",
        "mode_suffix": "MODE",
        "err_missing_credentials": "missing credentials",
        "err_client_creation": "client creation error: {e}",
        "err_no_run": "no run found for model={model} zone={zone}",
        "err_zero_records": "run_id={run_id} exists but has 0 records",
        "err_query": "query error: {e}",
        "err_comparison_query": "comparison query error: {e}",
        "quick_selection": "QUICK SELECTION",
        "italy_flag_label": "🇮🇹 ITALY",
        "timeframe_label": "TIMEFRAME",
        "timeframe_week": "Week",
        "timeframe_day": "Day",
        "weather_overlay_label": "WEATHER OVERLAY",
        "weather_overlay_csv_label": "WEATHER OVERLAY (CSV FEATURES)",
        "prev_year_label": "PREVIOUS YEAR DATA",
        "map_not_found": "⚠️ Map not found: {path}",
        "map_not_available": "Map not available: {path}",
        "src_label": "SRC",
        "simulated_badge": "SIMULATED",
        "simulated_data": "simulated data",
        "load_header_section": "LOAD",
        "load_header_subtitle": "ZONAL ELECTRICITY LOAD FORECAST PLATFORM ITALY",
        "load_info_strip_title": "ZONAL ELECTRICITY LOAD FORECAST:",
        "kpi_max_forecast": "MAX FORECAST (GW)",
        "kpi_min_forecast": "MIN FORECAST (GW)",
        "kpi_avg_forecast": "AVG FORECAST (GW)",
        "chart_title_weekly_load": "WEEKLY LOAD FORECAST",
        "chart_title_daily_load": "DAILY LOAD FORECAST",
        "forecast_window_label": "FORECAST WINDOW",
        "today_forecast_label": "TODAY'S FORECAST",
        "key_metrics_label": "KEY METRICS",
        "caption_forecast_vs_hist": "forecast vs hist avg",
        "caption_avg_conf_interval": "avg conf. interval",
        "caption_model_fit": "model fit accuracy",
        "yaxis_load": "Load (GW)",
        "pv_header_section": "PV",
        "pv_header_subtitle": "ZONAL PHOTOVOLTAIC PRODUCTION FORECAST PLATFORM ITALY",
        "installed_capacity_label": "INSTALLED CAPACITY",
        "pv_info_strip_title": "PV PRODUCTION FORECAST:",
        "kpi_peak_forecast": "PEAK FORECAST (GW)",
        "kpi_avg_production": "AVG PRODUCTION (GW)",
        "kpi_total_energy": "TOTAL ENERGY (GWh)",
        "chart_title_weekly_pv": "WEEKLY PV FORECAST",
        "chart_title_daily_pv": "DAILY PV FORECAST",
        "today_pv_forecast_label": "TODAY'S PV FORECAST",
        "key_metrics_pv_label": "KEY METRICS PV",
        "caption_capacity_factor": "avg capacity factor",
        "caption_installed_capacity": "installed capacity",
        "yaxis_production": "Production (GW)",
        "label_energy": "ENERGY",
        "cmp_header_section": "COMPARISON",
        "cmp_header_subtitle": "FORECAST VS ACTUAL & ACCURACY ANALYSIS",
        "resource_label": "RESOURCE",
        "model_load_label": "⚡ LOAD",
        "model_pv_label": "☀️ PV",
        "time_horizon_label": "TIME HORIZON",
        "lead_time_emissions_label": "FORECAST LEAD TIME",
        "insufficient_data_msg": (
            "📈 **Not enough historical emissions yet for this analysis.** "
            "Right now there are **{n_runs} emission(s)** saved for {model} · {zone} "
            "(first: {first_dt}). A forecast becomes comparable to the actual value only "
            "once its target date has passed and it has been observed by a later run — "
            "so it takes at least a few days of consecutive emissions before this page "
            "fills in. Check back in a couple of days."
        ),
        "ts_comparison_title": "Time-series Comparison (shows selected week)",
        "error_metrics_title": "Error Metrics (Accuracy Breakdown)",
        "no_obs_caption": "No observations available yet for the selected lead times.",
        "error_by_hour_title": "Error by Hour of Day",
        "error_vs_lead_title": "Error vs Lead Time",
        "hours_before_suffix": "h before",
        "hour_hover_label": "Hour",
    },
}


def T(key: str, **kwargs) -> str:
    """Ritorna la stringa tradotta per la lingua attualmente selezionata."""
    template = TR.get(st.session_state.lang, TR["it"]).get(key)
    if template is None:
        template = TR["it"].get(key, key)
    return template.format(**kwargs) if kwargs else template


def L(options: dict, key: str) -> str:
    """Ritorna la label bilingue di un dizionario di opzioni (METEO_OPTIONS, ecc.)."""
    lbl = options[key]["label"]
    if isinstance(lbl, dict):
        return lbl.get(st.session_state.lang, lbl.get("it", key))
    return lbl


# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title=T("app_title"),
    page_icon="⚡",
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

PV_ZONE_COLORS = ZONE_COLORS

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")


# ── DATA LAYER – TURSO ────────────────────────────────────────────────────────
def _get_turso_client():
    """Client Turso sincrono. Ritorna None se le credenziali non sono configurate."""
    import libsql_client
    url   = st.secrets.get("TURSO_URL")   or os.environ.get("TURSO_URL")
    token = st.secrets.get("TURSO_TOKEN") or os.environ.get("TURSO_TOKEN")
    if not url or not token:
        st.session_state["_turso_error"] = ("err_missing_credentials", {})
        return None
    if url.startswith("libsql://"):
        url = "https://" + url[len("libsql://"):]
    elif url.startswith("wss://"):
        url = "https://" + url[len("wss://"):]
    st.session_state["_turso_url_used"] = url
    try:
        return libsql_client.create_client_sync(url=url, auth_token=token)
    except Exception as e:
        st.session_state["_turso_error"] = ("err_client_creation", {"e": str(e)})
        return None


def _load_from_db(model: str, zone: str) -> dict | None:
    """
    Legge da Turso l'ultimo run disponibile per model x zone.
    Ritorna None se le credenziali mancano o la zona non ha dati.
    """
    client = _get_turso_client()
    if client is None:
        return None

    target_zone = zone.upper()
    if target_zone in ["ITALY", "ITA", "IT"]:
        target_zone = "ITA" if model == "load" else "ITALY"

    try:
        res = client.execute(
            "SELECT id, source_file FROM forecast_runs "
            "WHERE model = ? AND zone = ? ORDER BY created_at DESC LIMIT 1",
            [model, target_zone],
        )
        if not res.rows:
            st.session_state["_turso_error"] = ("err_no_run", {"model": model, "zone": target_zone})
            return None

        run_id      = res.rows[0][0]
        source_file = res.rows[0][1] or ""

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
            st.session_state["_turso_error"] = ("err_zero_records", {"run_id": run_id})
            return None

        cols = [c.name if hasattr(c, "name") else c for c in res2.columns]
        df   = pd.DataFrame([dict(zip(cols, row)) for row in res2.rows])

        if df.empty:
            return None

        df["datetime"] = pd.to_datetime(df["datetime"], utc=True, errors="coerce")
        df["datetime"] = df["datetime"].dt.tz_localize(None)

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

        st.session_state["_turso_error"] = None
        return dict(
            hist=hist,
            fore=fore,
            filename=os.path.basename(source_file),
            is_dummy=False,
            from_db=True,
        )

    except Exception as e:
        st.session_state["_turso_error"] = ("err_query", {"e": str(e)})
        return None
    finally:
        client.close()


def _cmp_target_zone(model: str, zone: str) -> str:
    z = zone.upper()
    if z in ("ITALY", "ITA", "IT"):
        return "ITA" if model == "load" else "ITALY"
    return z


@st.cache_data(ttl=300, show_spinner=False)
def load_comparison_data(model: str, zone: str, lookback_days: int = 21) -> dict:
    """
    Ricostruisce, per model x zone, il confronto tra il valore reale (actual)
    e le previsioni emesse in run diversi per la stessa data target — con il
    lead time (D-1, D-2, ...) calcolato come differenza in giorni tra la
    data del run (created_at) e la data target (ts).

    Ritorna un dict con:
      merged        : DataFrame indicizzato su ts, colonne Actual + Forecast D-N
      metrics       : DataFrame errori (MAE, MAPE, RMSE, Max Error, Bias) per lead time
      n_runs        : numero di run distinti trovati
      run_dates     : lista (ordinata) delle date di emissione trovate
      max_lead_seen : lead massimo (giorni) effettivamente presente nei dati
    """
    empty = dict(merged=pd.DataFrame(), metrics=pd.DataFrame(),
                 n_runs=0, run_dates=[], max_lead_seen=0)

    client = _get_turso_client()
    if client is None:
        return empty

    target_zone = _cmp_target_zone(model, zone)
    cutoff = (pd.Timestamp.utcnow().normalize()
              - pd.Timedelta(days=lookback_days)).strftime("%Y-%m-%dT00:00:00Z")

    try:
        # Tutte le date di emissione disponibili (per il conteggio/diagnostica)
        res_runs = client.execute(
            "SELECT DISTINCT created_at FROM forecast_runs "
            "WHERE model = ? AND zone = ? ORDER BY created_at",
            [model, target_zone],
        )
        run_dates = [row[0] for row in res_runs.rows]

        if not run_dates:
            return empty

        # Valori reali (dalla sezione 'historical' di ciascun run, quella più
        # recente per ogni ts, così da avere l'ultima revisione disponibile)
        res_act = client.execute(
            "SELECT rec.ts, rec.actual_gw, fr.created_at "
            "FROM forecast_records rec JOIN forecast_runs fr ON fr.id = rec.run_id "
            "WHERE fr.model = ? AND fr.zone = ? AND rec.actual_gw IS NOT NULL "
            "  AND rec.ts >= ? ORDER BY fr.created_at DESC",
            [model, target_zone, cutoff],
        )
        actual_df = pd.DataFrame(res_act.rows, columns=["ts", "actual_gw", "run_created_at"])

        # Tutte le previsioni emesse (sezione 'forecast') nella finestra
        res_fc = client.execute(
            "SELECT fr.created_at AS run_created_at, rec.ts, rec.predicted_gw "
            "FROM forecast_records rec JOIN forecast_runs fr ON fr.id = rec.run_id "
            "WHERE fr.model = ? AND fr.zone = ? AND rec.section = 'forecast' "
            "  AND fr.created_at >= ? ORDER BY fr.created_at ASC, rec.ts ASC",
            [model, target_zone, cutoff],
        )
        fc_df = pd.DataFrame(res_fc.rows, columns=["run_created_at", "ts", "predicted_gw"])

        if fc_df.empty:
            return dict(merged=pd.DataFrame(), metrics=pd.DataFrame(),
                        n_runs=len(run_dates), run_dates=run_dates, max_lead_seen=0)

        for df_ in (actual_df, fc_df):
            df_["ts"] = pd.to_datetime(df_["ts"], utc=True, errors="coerce").dt.tz_localize(None)
            df_["run_created_at"] = pd.to_datetime(df_["run_created_at"], utc=True, errors="coerce").dt.tz_localize(None)

        if not actual_df.empty:
            actual_df = actual_df.sort_values("run_created_at", ascending=False)
            actual_df = actual_df.drop_duplicates(subset="ts", keep="first")
            actual_df = actual_df[["ts", "actual_gw"]]

        fc_df["lead_days"] = (fc_df["ts"].dt.normalize() - fc_df["run_created_at"].dt.normalize()).dt.days
        fc_df = fc_df[(fc_df["lead_days"] >= 1) & (fc_df["lead_days"] <= 7)]
        if fc_df.empty:
            return dict(merged=pd.DataFrame(), metrics=pd.DataFrame(),
                        n_runs=len(run_dates), run_dates=run_dates, max_lead_seen=0)

        # Se più run coprono lo stesso (ts, lead_days) tiene il più recente
        fc_df = fc_df.sort_values("run_created_at", ascending=False)
        fc_df = fc_df.drop_duplicates(subset=["ts", "lead_days"], keep="first")

        max_lead_seen = int(fc_df["lead_days"].max())

        pivot = fc_df.pivot_table(index="ts", columns="lead_days", values="predicted_gw", aggfunc="first")
        pivot = pivot.rename(columns={c: f"Forecast D-{int(c)}" for c in pivot.columns})
        pivot = pivot.sort_index()

        merged = pivot.copy()
        if not actual_df.empty:
            merged = merged.join(actual_df.set_index("ts")["actual_gw"], how="outer")
        merged = merged.rename(columns={"actual_gw": "Actual"})
        merged = merged.sort_index()

        # ── Metriche di errore per lead time (solo dove Actual è disponibile) ──
        metric_rows = []
        if "Actual" in merged.columns:
            for lead in sorted(fc_df["lead_days"].unique()):
                col = f"Forecast D-{int(lead)}"
                if col not in merged.columns:
                    continue
                sub = merged[[col, "Actual"]].dropna()
                if sub.empty:
                    continue
                err = sub[col] - sub["Actual"]
                mae = err.abs().mean()
                rmse = np.sqrt((err ** 2).mean())
                max_err = err.abs().max()
                bias = err.mean()
                # WMAPE: sum(|err|) / sum(actual) — robusto con valori vicini a zero
                actual_sum = sub["Actual"].sum()
                wmape_pct = (err.abs().sum() / actual_sum * 100) if actual_sum > 0 else np.nan
                metric_rows.append({
                    "Lead Time": f"D-{int(lead)} ({int(lead)*24}h prima)",
                    "lead_days": int(lead),
                    "MAE (MW)": round(mae * 1000, 0),
                    "WMAPE (%)": round(wmape_pct, 1) if pd.notna(wmape_pct) else np.nan,
                    "RMSE (MW)": round(rmse * 1000, 0),
                    "Max Error (MW)": round(max_err * 1000, 0),
                    "Bias (MW)": round(bias * 1000, 0),
                    "n_oss": len(sub),
                })
        metrics = pd.DataFrame(metric_rows)

        return dict(merged=merged, metrics=metrics, n_runs=len(run_dates),
                    run_dates=run_dates, max_lead_seen=max_lead_seen)

    except Exception as e:
        st.session_state["_turso_error"] = ("err_comparison_query", {"e": str(e)})
        return empty
    finally:
        client.close()


# ── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="stAppViewContainer"]   { background:#0d1117 !important; }
[data-testid="stHeader"]             { background:transparent !important; }
[data-testid="stMainBlockContainer"] { padding-top:0 !important; }
.block-container {
    padding:0 1rem 1rem !important;
    max-width: 100% !important;
}

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

/* KPI grid - Aggiornata a 3 colonne */
.t-kpi-container {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
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
    flex-wrap: wrap !important;
}
div[data-testid="stSegmentedControl"] > div {
    flex-wrap: wrap !important;
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
    st.session_state.dashboard_mode = "LOAD"
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
if "cmp_model" not in st.session_state:
    st.session_state.cmp_model = "load"
if "cmp_zone" not in st.session_state:
    st.session_state.cmp_zone = "NORD"
if "cmp_leadtimes" not in st.session_state:
    st.session_state.cmp_leadtimes = [1, 2, 3]
if "cmp_date_range" not in st.session_state:
    st.session_state.cmp_date_range = None

# ── SIDEBAR – MODE SWITCHER ───────────────────────────────────────────────────
with st.sidebar:
    lang_choice = st.segmented_control(
        label="lang_switch", options=["IT", "EN"],
        default=st.session_state.lang.upper(),
        selection_mode="single", key="lang_toggle",
        label_visibility="collapsed")
    if lang_choice is not None and lang_choice.lower() != st.session_state.lang:
        st.session_state.lang = lang_choice.lower()
        st.rerun()

    st.markdown(f"<div class='sb-logo'>{T('app_brand')}</div>", unsafe_allow_html=True)
    st.markdown("<hr class='sb-divider'>", unsafe_allow_html=True)

    mode = st.session_state.dashboard_mode

    if st.button(f"⚡\n{T('nav_load')}", key="sb_load", use_container_width=True,
                 help=T("nav_load_help")):
        st.session_state.dashboard_mode = "LOAD"
        st.rerun()

    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

    if st.button(f"☀️\n{T('nav_pv')}", key="sb_pv", use_container_width=True,
                 help=T("nav_pv_help")):
        st.session_state.dashboard_mode = "PV"
        st.rerun()

    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

    if st.button(f"📊\n{T('nav_comparison')}", key="sb_cmp", use_container_width=True,
                 help=T("nav_comparison_help")):
        st.session_state.dashboard_mode = "COMPARISON"
        st.rerun()

    st.markdown("<hr class='sb-divider' style='margin-top:16px'>", unsafe_allow_html=True)
    _icons  = {"LOAD": "⚡", "PV": "☀️", "COMPARISON": "📊"}
    _colors = {"LOAD": "#7be2ff", "PV": "#ffd700", "COMPARISON": "#ff8c42"}
    _labels = {"LOAD": T("nav_load"), "PV": T("nav_pv"), "COMPARISON": T("nav_comparison")}
    active_icon  = _icons.get(mode, "⚡")
    active_color = _colors.get(mode, "#7be2ff")
    active_label = _labels.get(mode, mode)
    st.markdown(
        f"<div style='font-family:Courier New,monospace;font-size:8px;color:{active_color};"
        f"text-align:center;padding:8px 4px;letter-spacing:.10em'>"
        f"{active_icon} {active_label} {T('mode_suffix')}</div>",
        unsafe_allow_html=True
    )


# ── DATA LAYER – LOAD ─────────────────────────────────────────────────────────
def _candidate_data_dirs() -> list[str]:
    dirs = [DATA_DIR, BASE_DIR]
    return list(dict.fromkeys(d for d in dirs if os.path.isdir(d)))


def find_latest_file(zone: str) -> str | None:
    files = []
    for directory in _candidate_data_dirs():
        files.extend(glob.glob(os.path.join(directory, f"forecast_load_{zone}_*.csv")))
    files = sorted(set(files), reverse=True)
    return files[0] if files else None


@st.cache_data(ttl=300, show_spinner=False)
def load_zone_data(zone: str) -> dict:
    # 1) Prova DB Turso
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

    # Fallback simulato
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


# ── DATA LAYER – PV ───────────────────────────────────────────────────────────
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


@st.cache_data(ttl=300, show_spinner=False)
def load_pv_data(zone: str) -> dict:
    # 1) Prova DB Turso
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
        raw["date"] = pd.to_datetime(raw["date"], errors="coerce")
        raw = raw.dropna(subset=["date"]).copy()

        hist = raw[raw["section"].eq("historical")].copy()
        fore = raw[raw["section"].eq("forecast")].copy()

        hist = hist.rename(columns={"PV_Production (GW)": "actual_pv", "date": "datetime"})
        fore = fore.rename(columns={"Predicted_PV (GW)": "predicted_pv", "date": "datetime"})

        for df, col in ((hist, "actual_pv"), (fore, "predicted_pv"),
                        (fore, "lower_bound"), (fore, "upper_bound")):
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        hist = hist.sort_values("datetime").reset_index(drop=True)
        fore = fore.sort_values("datetime").reset_index(drop=True)

        if "actual_pv" not in hist.columns:
            hist["actual_pv"] = np.nan

        return dict(hist=hist, fore=fore, filename=os.path.basename(path), is_dummy=False)

    # Fallback simulato
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


# ── OVERLAY OPTIONS ───────────────────────────────────────────────────────────
METEO_OPTIONS = {
    "temperature_2m (°C)": dict(label={"it": "Temp 2m", "en": "Temp 2m"}, unit="°C", color="#ff7f50"),
    "apparent_temperature (°C)": dict(label={"it": "Temp percepita", "en": "Apparent Temp"}, unit="°C", color="#ffa07a"),
    "cloud_cover (%)": dict(label={"it": "Copertura nuvole", "en": "Cloud Cover"}, unit="%", color="#a0a0c0"),
    "wind_speed_10m (km/h)": dict(label={"it": "Vento 10m", "en": "Wind 10m"}, unit="km/h", color="#90ee90"),
    "direct_radiation (W/m²)": dict(label={"it": "Radiazione", "en": "Radiation"}, unit="W/m²", color="#ffd700"),
    "relative_humidity_2m (%)": dict(label={"it": "Umidità", "en": "Humidity"}, unit="%", color="#87ceeb"),
}

PV_METEO_OPTIONS = {
    "shortwave_radiation": dict(label={"it": "Rad. Globale", "en": "Global Rad."}, unit="W/m²", color="#ffd700"),
    "direct_normal_irradiance": dict(label={"it": "DNI (Rad. Norm.)", "en": "DNI (Normal Rad.)"}, unit="W/m²", color="#ffae19"),
    "diffuse_radiation": dict(label={"it": "Rad. Diffusa", "en": "Diffuse Rad."}, unit="W/m²", color="#ff8c00"),
    "direct_radiation": dict(label={"it": "Rad. Diretta", "en": "Direct Rad."}, unit="W/m²", color="#ffa500"),
    "temperature_2m": dict(label={"it": "Temp 2m", "en": "Temp 2m"}, unit="°C", color="#ff7f50"),
    "apparent_temperature": dict(label={"it": "Temp Percepita", "en": "Apparent Temp"}, unit="°C", color="#ffa07a"),
    "wind_speed_10m": dict(label={"it": "Vento 10m", "en": "Wind 10m"}, unit="km/h", color="#90ee90"),
    "cloud_cover": dict(label={"it": "Nuvole Totali", "en": "Total Cloud"}, unit="%", color="#a0a0c0"),
    "cloud_cover_low": dict(label={"it": "Nuvole Basse", "en": "Low Cloud"}, unit="%", color="#87ceeb"),
    "cloud_cover_mid": dict(label={"it": "Nuvole Medie", "en": "Mid Cloud"}, unit="%", color="#70a1ff"),
    "cloud_cover_high": dict(label={"it": "Nuvole Alte", "en": "High Cloud"}, unit="%", color="#a4b0be"),
    "precipitation": dict(label={"it": "Precipitazioni", "en": "Precipitation"}, unit="mm", color="#1e90ff"),
    "snowfall": dict(label={"it": "Neve", "en": "Snowfall"}, unit="cm", color="#e0ffff"),
    "snow_depth": dict(label={"it": "Altezza Neve", "en": "Snow Depth"}, unit="m", color="#f0ffff"),
}

PREV_YEAR_OPTIONS = {
    "Prev_Year_Load (GW)": dict(label={"it": "Carico (GW)", "en": "Load (GW)"}, unit="GW", color="#6a9fb5", axis="y1"),
    "Prev_Year_Temp (°C)": dict(label={"it": "Temperatura (°C)", "en": "Temperature (°C)"}, unit="°C", color="#d28445", axis="y2"),
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
        mc_label = L(METEO_OPTIONS, meteo_var)
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
                name=mc_label,
                line=dict(color=mc["color"], width=1.4, dash="dot"),
                opacity=0.85,
                hovertemplate=f"%{{x|%d/%m %H:%M}}<br><b>%{{y:.1f}} {mc['unit']}</b><extra>{mc_label}</extra>",
                yaxis="y2",
            )
        )

    has_prev_temp = False
    for p_var in prev_year_vars:
        if p_var in hist.columns or p_var in fore.columns:
            pc = PREV_YEAR_OPTIONS[p_var]
            pc_label = L(PREV_YEAR_OPTIONS, p_var)
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
                    name=pc_label,
                    line=dict(color=pc["color"], width=1.5, dash="dash"),
                    opacity=0.85,
                    hovertemplate=f"%{{x|%d/%m %H:%M}}<br><b>%{{y:.2f}} {pc['unit']}</b><extra>{pc_label}</extra>",
                    yaxis=pc["axis"],
                )
            )

    show_axis_2 = has_meteo or has_prev_temp
    right_margin = 55 if show_axis_2 else 16
    y2_labels = []
    y2_color = "#8b949e"
    if has_meteo:
        y2_labels.append(
            f"{L(METEO_OPTIONS, meteo_var)} ({METEO_OPTIONS[meteo_var]['unit']})"
        )
        y2_color = METEO_OPTIONS[meteo_var]["color"]
    if has_prev_temp:
        pc_temp = PREV_YEAR_OPTIONS["Prev_Year_Temp (°C)"]
        y2_labels.append(f"{L(PREV_YEAR_OPTIONS, 'Prev_Year_Temp (°C)')} ({pc_temp['unit']})")
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
                text=T("yaxis_load"),
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
        mc_label = L(PV_METEO_OPTIONS, meteo_var)
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
                name=mc_label,
                line=dict(color=mc["color"], width=1.4, dash="dot"),
                opacity=0.85,
                hovertemplate=f"%{{x|%d/%m %H:%M}}<br><b>%{{y:.1f}} {mc['unit']}</b><extra>{mc_label}</extra>",
                yaxis="y2",
            )
        )

    show_axis_2 = has_meteo
    right_margin = 55 if show_axis_2 else 16
    y2_label = ""
    y2_color = "#8b949e"
    if has_meteo:
        mc_info = PV_METEO_OPTIONS[meteo_var]
        y2_label = f"{L(PV_METEO_OPTIONS, meteo_var)} ({mc_info['unit']})"
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
                text=T("yaxis_production"),
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
    st.markdown(f"""
    <div class="t-app-header">
      <div class="t-app-logo">
        <span>⚡</span> {T('load_header_section')} &nbsp;|&nbsp;
        <span style="font-weight:400;color:#8b949e">{T('load_header_subtitle')}</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    left_col, right_col = st.columns([4, 8], gap="small")

    with left_col:
        st.markdown(f"<p class='t-panel-title' style='margin-top:8px'>{T('quick_selection')}</p>",
                    unsafe_allow_html=True)

        zone_options = ["ITALY"] + ZONE_ORDER
        chosen_zone = st.segmented_control(
            label="selezione_zona",
            options=zone_options,
            format_func=lambda z: T("italy_flag_label") if z == "ITALY" else z,
            default=st.session_state.selected_zone,
            selection_mode="single",
            key="zone_toggle",
            label_visibility="collapsed",
        )
        if chosen_zone is not None and chosen_zone != st.session_state.selected_zone:
            st.session_state.selected_zone = chosen_zone
            st.rerun()
        elif chosen_zone is None:
            st.session_state.selected_zone = "ITALY"

        st.write("---")

        active_zone = st.session_state.selected_zone
        map_path = os.path.join(BASE_DIR, "maps", f"plot_{active_zone.lower()}.png")
        try:
            st.image(map_path, use_container_width=True)
        except Exception:
            st.error(T("map_not_found", path=map_path))

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

        lbl_sim = (f"<span class='t-tag' style='color:#e74c3c; border-color:#e74c3c'>⚠ {T('simulated_badge')}</span>"
                   if data["is_dummy"] else "")
        src_value = T("simulated_data") if data["is_dummy"] else data['filename']
        lbl_src = f"<span class='t-tag'>{T('src_label')}: {src_value}</span>"

        st.markdown(f"""
        <div class="t-info-strip">
          <div>{T('load_info_strip_title')} <span style="color:{zc}; font-weight:700;">{zone}</span></div>
          <div style="display:flex; align-items:center;">
            <span>📅 {date_start} – {date_end}</span>
            {lbl_src}{lbl_sim}
          </div>
        </div>
        """, unsafe_allow_html=True)

        ctrl_tf, ctrl_meteo, ctrl_prev = st.columns([3, 5, 4])

        with ctrl_tf:
            st.markdown(
                f"<p style='font-family:Courier New,monospace;font-size:9px;color:#8b949e;margin-bottom:2px'>{T('timeframe_label')}</p>",
                unsafe_allow_html=True)
            chosen_tf = st.segmented_control(
                label="timeframe", options=["Week", "Day"],
                format_func=lambda x: T("timeframe_week") if x == "Week" else T("timeframe_day"),
                default=st.session_state.timeframe,
                selection_mode="single", key="tf_toggle",
                label_visibility="collapsed")
            st.session_state.timeframe = chosen_tf if chosen_tf is not None else "Week"

        with ctrl_meteo:
            st.markdown(
                f"<p style='font-family:Courier New,monospace;font-size:9px;color:#8b949e;margin-bottom:2px'>{T('weather_overlay_label')}</p>",
                unsafe_allow_html=True)
            chosen = st.segmented_control(
                label="meteo", options=list(METEO_OPTIONS.keys()),
                format_func=lambda k: L(METEO_OPTIONS, k),
                default=st.session_state.meteo_var,
                selection_mode="single", key="meteo_toggle",
                label_visibility="collapsed")
            st.session_state.meteo_var = chosen

        with ctrl_prev:
            st.markdown(
                f"<p style='font-family:Courier New,monospace;font-size:9px;color:#8b949e;margin-bottom:2px'>{T('prev_year_label')}</p>",
                unsafe_allow_html=True)
            chosen_prev = st.segmented_control(
                label="prev_year", options=list(PREV_YEAR_OPTIONS.keys()),
                format_func=lambda k: L(PREV_YEAR_OPTIONS, k),
                default=st.session_state.prev_year_vars,
                selection_mode="multi", key="prev_year_toggle",
                label_visibility="collapsed")
            st.session_state.prev_year_vars = chosen_prev if chosen_prev is not None else []

        st.markdown("<hr>", unsafe_allow_html=True)

        p_max = fore["predicted_load"].max()
        p_min = fore["predicted_load"].min()
        p_avg = fore["predicted_load"].mean()
        interval_str = (f"±{(fore['upper_bound'] - fore['lower_bound']).mean() / 2:.2f}"
                        if "upper_bound" in fore.columns else "—")

        st.markdown(f"""
        <div class="t-kpi-container">
          <div class="t-kpi-card">
            <div class="t-kpi-label">{T('kpi_max_forecast')}</div>
            <div class="t-kpi-value" style="color:{zc}">{p_max:.1f}</div>
          </div>
          <div class="t-kpi-card">
            <div class="t-kpi-label">{T('kpi_min_forecast')}</div>
            <div class="t-kpi-value" style="color:{zc}">{p_min:.1f}</div>
          </div>
          <div class="t-kpi-card">
            <div class="t-kpi-label">{T('kpi_avg_forecast')}</div>
            <div class="t-kpi-value" style="color:{zc}">{p_avg:.1f}</div>
          </div>
        </div>""", unsafe_allow_html=True)

        tf = st.session_state.timeframe
        chart_title = T("chart_title_weekly_load") if tf == "Week" else T("chart_title_daily_load")
        st.markdown(
            f"<div class='t-chart-title'>{chart_title} ({zone})"
            f" · {T('forecast_window_label')}: {fore_start} – {fore_end}</div>",
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
            <div class="t-bottom-label">{T('today_forecast_label')} ({today_label}):</div>
            <div class="t-bottom-vals">
              MAX&nbsp;<b style="color:{zc}">{t_max:.1f}</b> GW &nbsp;|&nbsp;
              MIN&nbsp;<b style="color:{zc}">{t_min:.1f}</b> GW &nbsp;|&nbsp;
              AVG&nbsp;<b style="color:{zc}">{t_avg:.1f}</b> GW
            </div>
          </div>
          <div class="t-bottom-card">
            <div class="t-bottom-label">{T('key_metrics_label')} ({zone}):</div>
            <div class="t-metrics-flex">
              <div>
                <div class="t-flex-val {dw_cl}">{'+' if dw >= 0 else ''}{dw:.1f}%</div>
                <div class="t-flex-sub">{T('caption_forecast_vs_hist')}</div>
              </div>
              <div>
                <div class="t-flex-val" style="color:#8b949e">{interval_str} GW</div>
                <div class="t-flex-sub">{T('caption_avg_conf_interval')}</div>
              </div>
              <div>
                <div class="t-flex-val" style="color:{zc}">{r2_str}</div>
                <div class="t-flex-sub">{T('caption_model_fit')}</div>
              </div>
            </div>
          </div>
        </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  DASHBOARD – PV
# ══════════════════════════════════════════════════════════════════════════════
def render_pv_dashboard():
    st.markdown(f"""
    <div class="t-app-header">
      <div class="t-app-logo">
        <span class="pv">☀️</span> {T('pv_header_section')} &nbsp;|&nbsp;
        <span style="font-weight:400;color:#8b949e">{T('pv_header_subtitle')}</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    pv_capacity_data = load_pv_capacity()

    left_col, right_col = st.columns([4, 8], gap="small")

    with left_col:
        st.markdown(f"<p class='t-panel-title' style='margin-top:8px'>{T('quick_selection')}</p>",
                    unsafe_allow_html=True)

        zone_options = ["ITALY"] + ZONE_ORDER
        chosen_zone = st.segmented_control(
            label="selezione_zona_pv",
            options=zone_options,
            format_func=lambda z: T("italy_flag_label") if z == "ITALY" else z,
            default=st.session_state.pv_zone,
            selection_mode="single",
            key="pv_zone_toggle",
            label_visibility="collapsed",
        )
        if chosen_zone is not None and chosen_zone != st.session_state.pv_zone:
            st.session_state.pv_zone = chosen_zone
            st.rerun()
        elif chosen_zone is None:
            st.session_state.pv_zone = "ITALY"

        st.write("---")

        active_zone = st.session_state.pv_zone
        cap_gw = pv_capacity_data.get(active_zone, 0.0)
        pv_color = PV_ZONE_COLORS.get(active_zone, "#ffd700")
        st.markdown(f"""
        <div style="background:#161b22;border:1px solid #21262d;border-radius:5px;
                    padding:10px 12px;margin-bottom:8px;font-family:'Courier New',monospace">
          <div style="font-size:9px;color:#8b949e;letter-spacing:.08em;margin-bottom:4px">
            {T('installed_capacity_label')}</div>
          <div style="font-size:22px;font-weight:700;color:{pv_color}">{cap_gw:.1f} GW<sub style="font-size:12px;color:#8b949e">p</sub></div>
        </div>
        """, unsafe_allow_html=True)

        map_path = os.path.join(BASE_DIR, "maps", f"plot_{active_zone.lower()}.png")
        try:
            st.image(map_path, use_container_width=True)
        except Exception:
            st.warning(T("map_not_available", path=map_path))

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

        lbl_sim = (f"<span class='t-tag' style='color:#e74c3c; border-color:#e74c3c'>⚠ {T('simulated_badge')}</span>"
                   if data["is_dummy"] else "")
        src_value = T("simulated_data") if data["is_dummy"] else data['filename']
        lbl_src = f"<span class='t-tag'>{T('src_label')}: {src_value}</span>"

        st.markdown(f"""
        <div class="t-info-strip">
          <div>☀️ {T('pv_info_strip_title')} <span style="color:{zc}; font-weight:700;">{zone}</span></div>
          <div style="display:flex; align-items:center;">
            <span>📅 {date_start} – {date_end}</span>
            {lbl_src}{lbl_sim}
          </div>
        </div>
        """, unsafe_allow_html=True)

        ctrl_tf, ctrl_meteo = st.columns([3, 9])

        with ctrl_tf:
            st.markdown(
                f"<p style='font-family:Courier New,monospace;font-size:9px;color:#8b949e;margin-bottom:2px'>{T('timeframe_label')}</p>",
                unsafe_allow_html=True)
            chosen_tf = st.segmented_control(
                label="pv_timeframe", options=["Week", "Day"],
                format_func=lambda x: T("timeframe_week") if x == "Week" else T("timeframe_day"),
                default=st.session_state.pv_timeframe,
                selection_mode="single", key="pv_tf_toggle",
                label_visibility="collapsed")
            st.session_state.pv_timeframe = chosen_tf if chosen_tf is not None else "Week"

        with ctrl_meteo:
            st.markdown(
                f"<p style='font-family:Courier New,monospace;font-size:9px;color:#8b949e;margin-bottom:2px'>{T('weather_overlay_csv_label')}</p>",
                unsafe_allow_html=True)
            chosen_pv_meteo = st.segmented_control(
                label="pv_meteo", options=list(PV_METEO_OPTIONS.keys()),
                format_func=lambda k: L(PV_METEO_OPTIONS, k),
                default=st.session_state.pv_meteo_var,
                selection_mode="single", key="pv_meteo_toggle",
                label_visibility="collapsed")
            st.session_state.pv_meteo_var = chosen_pv_meteo

        st.markdown("<hr>", unsafe_allow_html=True)

        p_peak = fore["predicted_pv"].max()
        p_avg = fore["predicted_pv"].mean()
        e_tot = fore["predicted_pv"].sum() * 0.25

        st.markdown(f"""
        <div class="t-kpi-container">
          <div class="t-kpi-card">
            <div class="t-kpi-label">{T('kpi_peak_forecast')}</div>
            <div class="t-kpi-value" style="color:{zc}">{p_peak:.2f}</div>
          </div>
          <div class="t-kpi-card">
            <div class="t-kpi-label">{T('kpi_avg_production')}</div>
            <div class="t-kpi-value" style="color:{zc}">{p_avg:.2f}</div>
          </div>
          <div class="t-kpi-card">
            <div class="t-kpi-label">{T('kpi_total_energy')}</div>
            <div class="t-kpi-value" style="color:{zc}">{e_tot:.1f}</div>
          </div>
        </div>""", unsafe_allow_html=True)

        tf_pv = st.session_state.pv_timeframe
        chart_title_pv = T("chart_title_weekly_pv") if tf_pv == "Week" else T("chart_title_daily_pv")

        st.markdown(
            f"<div class='t-chart-title'>{chart_title_pv} ({zone})"
            f" · {T('forecast_window_label')}: {fore_start} – {fore_end}</div>",
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
            <div class="t-bottom-label">{T('today_pv_forecast_label')} ({today_label}):</div>
            <div class="t-bottom-vals">
              PEAK&nbsp;<b style="color:{zc}">{t_peak:.2f}</b> GW &nbsp;|&nbsp;
              AVG&nbsp;<b style="color:{zc}">{t_avg:.2f}</b> GW &nbsp;|&nbsp;
              {T('label_energy')}&nbsp;<b style="color:{zc}">{t_energy:.1f}</b> GWh
            </div>
          </div>
          <div class="t-bottom-card">
            <div class="t-bottom-label">{T('key_metrics_pv_label')} ({zone}):</div>
            <div class="t-metrics-flex">
              <div>
                <div class="t-flex-val" style="color:{zc}">{cf:.1f}%</div>
                <div class="t-flex-sub">{T('caption_capacity_factor')}</div>
              </div>
              <div>
                <div class="t-flex-val" style="color:#8b949e">{interval_str} GW</div>
                <div class="t-flex-sub">{T('caption_avg_conf_interval')}</div>
              </div>
              <div>
                <div class="t-flex-val" style="color:{zc}">{cap:.1f} GW<span style="font-size:10px">p</span></div>
                <div class="t-flex-sub">{T('caption_installed_capacity')}</div>
              </div>
            </div>
          </div>
        </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  CHART – COMPARISON
# ══════════════════════════════════════════════════════════════════════════════
_LEAD_LINE_STYLES = {
    1: dict(dash="solid",  width=2.0),
    2: dict(dash="dash",   width=1.6),
    3: dict(dash="dot",    width=1.6),
    4: dict(dash="dashdot", width=1.4),
    5: dict(dash="dash",   width=1.2),
    6: dict(dash="dot",    width=1.2),
    7: dict(dash="dashdot", width=1.0),
}
_LEAD_COLORS = ["#e67e22", "#3498db", "#9b59b6", "#2ecc71", "#e74c3c", "#f1c40f", "#1abc9c"]


def build_comparison_chart(merged: pd.DataFrame, leadtimes: list[int], unit: str = "GW") -> go.Figure:
    fig = go.Figure()

    if "Actual" in merged.columns:
        act = merged["Actual"].dropna()
        fig.add_trace(go.Scatter(
            x=act.index, y=act.values,
            name="Actual (Consuntivo)",
            line=dict(color="#f5f5f5", width=2.4),
            hovertemplate=f"%{{x|%d/%m %H:%M}}<br><b>%{{y:.2f}} {unit}</b><extra>Actual</extra>",
        ))

    for i, lead in enumerate(sorted(leadtimes)):
        col = f"Forecast D-{lead}"
        if col not in merged.columns:
            continue
        s = merged[col].dropna()
        if s.empty:
            continue
        style = _LEAD_LINE_STYLES.get(lead, dict(dash="dot", width=1.2))
        color = _LEAD_COLORS[i % len(_LEAD_COLORS)]
        fig.add_trace(go.Scatter(
            x=s.index, y=s.values,
            name=f"Forecast D-{lead}",
            line=dict(color=color, width=style["width"], dash=style["dash"]),
            hovertemplate=f"%{{x|%d/%m %H:%M}}<br><b>%{{y:.2f}} {unit}</b><extra>D-{lead}</extra>",
        ))

    fig.update_layout(
        paper_bgcolor="#10161d",
        plot_bgcolor="#10161d",
        margin=dict(l=50, r=16, t=14, b=36),
        height=380,
        hovermode="x unified",
        hoverlabel=dict(bgcolor="#161b22", bordercolor="#21262d",
                         font=dict(color="#e6edf3", size=11, family="Courier New, monospace")),
        legend=dict(orientation="h", yanchor="bottom", y=1.03, xanchor="right", x=1,
                    font=dict(color="#8b949e", size=10, family="Courier New, monospace"),
                    bgcolor="rgba(0,0,0,0)"),
        xaxis=dict(gridcolor="#1e2630", showgrid=True, zeroline=False,
                   tickformat="%d/%m\n%H:%M",
                   tickfont=dict(color="#8b949e", size=9, family="Courier New, monospace")),
        yaxis=dict(
            title=dict(text=f"Load ({unit})" if unit == "GW" else unit,
                       font=dict(color="#8b949e", size=10, family="Courier New, monospace")),
            gridcolor="#1e2630", showgrid=True, zeroline=False,
            tickfont=dict(color="#8b949e", size=9, family="Courier New, monospace"),
        ),
    )
    return fig


def compute_metrics_from_df(df: pd.DataFrame, leadtimes: list[int]) -> pd.DataFrame:
    """Ricalcola le metriche di errore su un DataFrame già filtrato."""
    if df.empty or "Actual" not in df.columns:
        return pd.DataFrame()
    rows = []
    for lead in sorted(leadtimes):
        col = f"Forecast D-{lead}"
        if col not in df.columns:
            continue
        sub = df[[col, "Actual"]].dropna()
        if sub.empty:
            continue
        err = sub[col] - sub["Actual"]
        mae = err.abs().mean()
        rmse = np.sqrt((err ** 2).mean())
        max_err = err.abs().max()
        bias = err.mean()
        actual_sum = sub["Actual"].sum()
        wmape_pct = (err.abs().sum() / actual_sum * 100) if actual_sum > 0 else np.nan
        rows.append({
            "lead_days": int(lead),
            "MAE (MW)": round(mae * 1000, 0),
            "WMAPE (%)": round(wmape_pct, 1) if pd.notna(wmape_pct) else np.nan,
            "RMSE (MW)": round(rmse * 1000, 0),
            "Max Error (MW)": round(max_err * 1000, 0),
            "Bias (MW)": round(bias * 1000, 0),
            "n_oss": len(sub),
        })
    return pd.DataFrame(rows)


# Metriche disponibili nel grafico per ora del giorno
HOUR_METRICS = {
    "MAE (GW)":   "mae",
    "RMSE (GW)":  "rmse",
    "Bias (GW)":  "bias",
    "WMAPE (%)":  "wmape",
}

def build_error_by_hour_chart(merged: pd.DataFrame, leadtimes: list[int],
                               metric_key: str = "MAE (GW)") -> go.Figure:
    """Grafico errore medio per ora del giorno, metrica selezionabile.

    Le ore in cui l'actual è < 10 % del picco giornaliero vengono escluse
    per evitare l'esplosione degli errori relativi (WMAPE) nelle ore notturne
    o a bassa produzione.
    """
    if "Actual" not in merged.columns:
        return go.Figure()

    NIGHT_THRESHOLD_FRAC = 0.10
    col_id = HOUR_METRICS.get(metric_key, "mae")

    rows = []
    for lead in leadtimes:
        col = f"Forecast D-{lead}"
        if col not in merged.columns:
            continue
        sub = merged[[col, "Actual"]].dropna().copy()
        if sub.empty:
            continue
        sub["hour"] = sub.index.hour
        sub["date"] = sub.index.date
        daily_peak = sub.groupby("date")["Actual"].transform("max")
        mask = sub["Actual"] >= daily_peak * NIGHT_THRESHOLD_FRAC
        sub = sub[mask]
        if sub.empty:
            continue
        err = sub[col] - sub["Actual"]
        if col_id == "mae":
            values = err.abs()
        elif col_id == "rmse":
            values = err ** 2          # media poi sqrt sotto
        elif col_id == "bias":
            values = err
        elif col_id == "wmape":
            # per ora: |err| / actual * 100
            nz = sub["Actual"].replace(0, np.nan)
            values = err.abs() / nz * 100
        else:
            values = err.abs()
        rows.append(pd.DataFrame({"hour": sub["hour"].values, "val": values.values}))

    if not rows:
        return go.Figure()

    all_df = pd.concat(rows, ignore_index=True).dropna()
    if col_id == "rmse":
        by_hour = all_df.groupby("hour")["val"].mean().apply(np.sqrt).reindex(range(24))
    else:
        by_hour = all_df.groupby("hour")["val"].mean().reindex(range(24))

    # colore: rosso per bias negativo, arancio altrimenti
    if col_id == "bias":
        colors = ["#e74c3c" if (pd.notna(v) and v < 0) else "#e67e22" if pd.notna(v) else "rgba(0,0,0,0)"
                  for v in by_hour.values]
    else:
        colors = ["#e67e22" if pd.notna(v) else "rgba(0,0,0,0)" for v in by_hour.values]

    unit_label = "%" if col_id == "wmape" else "GW"
    fmt = ".1f" if col_id == "wmape" else ".3f"

    fig = go.Figure(go.Bar(
        x=by_hour.index,
        y=by_hour.fillna(0).values,
        marker_color=colors,
        hovertemplate=f"{T('hour_hover_label')} %{{x}}:00<br><b>%{{y:{fmt}}} {unit_label}</b><extra></extra>",
    ))
    fig.update_layout(
        paper_bgcolor="#10161d", plot_bgcolor="#10161d",
        margin=dict(l=40, r=10, t=10, b=30), height=230,
        xaxis=dict(gridcolor="#1e2630", tickfont=dict(color="#8b949e", size=9, family="Courier New, monospace"),
                   dtick=4),
        yaxis=dict(title=dict(text=f"{metric_key}*",
                              font=dict(color="#8b949e", size=9, family="Courier New, monospace")),
                   gridcolor="#1e2630", tickfont=dict(color="#8b949e", size=9, family="Courier New, monospace")),
        annotations=[dict(
            text="* ore notturne/bassa prod. escluse (< 10 % picco giornaliero)",
            xref="paper", yref="paper", x=0, y=-0.18,
            showarrow=False, font=dict(color="#555e6b", size=8, family="Courier New, monospace"),
            align="left",
        )],
    )
    return fig


# Metriche disponibili nel grafico vs lead time (colonne già presenti in metrics)
LEAD_METRICS = {
    "MAE (MW)":         ("MAE (MW)",         "MAE (MW)",    "#e67e22", False),
    "WMAPE (%)":        ("WMAPE (%)",         "WMAPE (%)",   "#3498db", False),
    "RMSE (MW)":        ("RMSE (MW)",         "RMSE (MW)",   "#9b59b6", False),
    "Bias (MW)":        ("Bias (MW)",         "Bias (MW)",   "#8b949e", True),
    "Max Error (MW)":   ("Max Error (MW)",    "Max (MW)",    "#e74c3c", False),
}

def build_error_vs_lead_chart(metrics: pd.DataFrame,
                               metric_key: str = "Bias (MW)") -> go.Figure:
    if metrics.empty:
        return go.Figure()

    col, ylabel, color, zeroline = LEAD_METRICS.get(
        metric_key, ("Bias (MW)", "Bias (MW)", "#8b949e", True)
    )
    if col not in metrics.columns:
        return go.Figure()

    y_vals = metrics[col]
    is_pct = "%" in metric_key

    if col == "Bias (MW)":
        point_colors = ["#e74c3c" if v < 0 else "#e67e22" for v in y_vals]
    else:
        point_colors = color

    fmt = ".1f" if is_pct else ".0f"
    unit = "%" if is_pct else " MW"

    fig = go.Figure(go.Scatter(
        x=metrics["lead_days"], y=y_vals,
        mode="markers", marker=dict(size=10, color=point_colors),
        hovertemplate=f"D-%{{x}}<br>{metric_key}: <b>%{{y:{fmt}}}{unit}</b><extra></extra>",
    ))
    fig.update_layout(
        paper_bgcolor="#10161d", plot_bgcolor="#10161d",
        margin=dict(l=40, r=10, t=10, b=30), height=230,
        xaxis=dict(
            gridcolor="#1e2630",
            title=dict(text="Lead Time", font=dict(color="#8b949e", size=9, family="Courier New, monospace")),
            tickvals=metrics["lead_days"], ticktext=[f"D-{d}" for d in metrics["lead_days"]],
            tickfont=dict(color="#8b949e", size=9, family="Courier New, monospace"),
        ),
        yaxis=dict(
            title=dict(text=ylabel, font=dict(color="#8b949e", size=9, family="Courier New, monospace")),
            gridcolor="#1e2630", zeroline=zeroline, zerolinecolor="#30363d",
            tickfont=dict(color="#8b949e", size=9, family="Courier New, monospace"),
        ),
    )
    return fig


# ══════════════════════════════════════════════════════════════════════════════
#  DASHBOARD – COMPARISON
# ══════════════════════════════════════════════════════════════════════════════
def render_comparison_dashboard():
    st.markdown(f"""
    <div class="t-app-header">
      <div class="t-app-logo">
        <span style="color:#ff8c42">📊</span> {T('cmp_header_section')} &nbsp;|&nbsp;
        <span style="font-weight:400;color:#8b949e">{T('cmp_header_subtitle')}</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

    ctrl_res, ctrl_zone, ctrl_range, ctrl_lead = st.columns([2, 5, 3, 4])

    with ctrl_res:
        st.markdown(f"<p class='t-panel-title'>{T('resource_label')}</p>", unsafe_allow_html=True)
        chosen_model = st.segmented_control(
            label="cmp_model", options=["load", "pv"],
            format_func=lambda m: T("model_load_label") if m == "load" else T("model_pv_label"),
            default=st.session_state.cmp_model, selection_mode="single",
            key="cmp_model_toggle", label_visibility="collapsed")
        st.session_state.cmp_model = chosen_model if chosen_model is not None else "load"

    with ctrl_zone:
        st.markdown(f"<p class='t-panel-title'>{T('quick_selection')}</p>", unsafe_allow_html=True)
        zone_options = ["ITALY"] + ZONE_ORDER
        chosen_zone = st.segmented_control(
            label="cmp_zone", options=zone_options,
            format_func=lambda z: T("italy_flag_label") if z == "ITALY" else z,
            default=st.session_state.cmp_zone, selection_mode="single",
            key="cmp_zone_toggle", label_visibility="collapsed")
        st.session_state.cmp_zone = chosen_zone if chosen_zone is not None else "ITALY"

    model = st.session_state.cmp_model
    zone = st.session_state.cmp_zone
    data = load_comparison_data(model, zone)

    with ctrl_range:
        st.markdown(f"<p class='t-panel-title'>{T('time_horizon_label')}</p>", unsafe_allow_html=True)
        _min_date = datetime.date(2026, 9, 21)
        if not data["merged"].empty:
            idx = data["merged"].index
            default_start = max(idx.min().date(), _min_date)
            default_end = idx.max().date()
        else:
            default_end = pd.Timestamp.utcnow().date()
            default_start = max(default_end - pd.Timedelta(days=7), _min_date)
        chosen_range = st.date_input(
            "cmp_range", value=(default_start, default_end),
            min_value=_min_date,
            key="cmp_range_input", label_visibility="collapsed")

    with ctrl_lead:
        st.markdown(f"<p class='t-panel-title'>{T('lead_time_emissions_label')}</p>", unsafe_allow_html=True)
        lead_options = list(range(1, max(data["max_lead_seen"], 3) + 1))
        chosen_leads = st.multiselect(
            "cmp_leads", options=lead_options,
            format_func=lambda d: f"Forecast D-{d}",
            default=[d for d in st.session_state.cmp_leadtimes if d in lead_options] or lead_options[:3],
            key="cmp_lead_select", label_visibility="collapsed")
        st.session_state.cmp_leadtimes = chosen_leads if chosen_leads else lead_options[:3]

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Stato: dati insufficienti ───────────────────────────────────────────
    if data["merged"].empty or "Actual" not in data["merged"].columns:
        n_runs = data["n_runs"]
        first_dt = data["run_dates"][0][:10] if data["run_dates"] else "—"
        st.info(T("insufficient_data_msg", n_runs=n_runs, model=model.upper(), zone=zone, first_dt=first_dt))
        return

    merged = data["merged"]
    leadtimes = sorted(st.session_state.cmp_leadtimes)

    if isinstance(chosen_range, tuple) and len(chosen_range) == 2:
        start_d, end_d = chosen_range
        mask = (merged.index.date >= start_d) & (merged.index.date <= end_d)
        view = merged.loc[mask]
    else:
        view = merged

    unit = "GW" if model == "load" else "GW"
    zc = ZONE_COLORS.get(zone, "#ff8c42")

    st.markdown(
        f"<div class='t-chart-title'>{T('ts_comparison_title')} · "
        f"<span style='color:{zc}'>{model.upper()} · {zone}</span></div>",
        unsafe_allow_html=True,
    )
    st.plotly_chart(
        build_comparison_chart(view, leadtimes, unit),
        use_container_width=True, config={"displayModeBar": False},
    )

    # ── Metriche di errore ───────────────────────────────────────────────────

    # Data massima in cui esiste il consuntivo (Actual non NaN)
    actual_col = merged["Actual"].dropna()
    last_actual_date = actual_col.index.date.max() if not actual_col.empty else None

    # Selettore scope metriche
    scope_options = ["Tutto il dataset", "Range selezionato"]
    metrics_scope = st.segmented_control(
        label="metrics_scope",
        options=scope_options,
        default="Tutto il dataset",
        selection_mode="single",
        key="metrics_scope_toggle",
        label_visibility="collapsed",
    )
    metrics_scope = metrics_scope if metrics_scope is not None else "Tutto il dataset"

    # Dataframe su cui calcolare le metriche
    if metrics_scope == "Range selezionato" and isinstance(chosen_range, tuple) and len(chosen_range) == 2:
        start_d, end_d = chosen_range
        # Cappa end_d alla data massima del consuntivo
        if last_actual_date is not None:
            end_d = min(end_d, last_actual_date)
        mask_m = (merged.index.date >= start_d) & (merged.index.date <= end_d)
        metrics_df = merged.loc[mask_m]
        metrics_raw = compute_metrics_from_df(metrics_df, leadtimes)
        scope_label = f"{start_d.strftime('%d/%m/%Y')} → {end_d.strftime('%d/%m/%Y')}"
    else:
        metrics_df = merged
        metrics_raw = data["metrics"]
        if last_actual_date is not None:
            first_actual_date = actual_col.index.date.min()
            scope_label = f"{first_actual_date.strftime('%d/%m/%Y')} → {last_actual_date.strftime('%d/%m/%Y')}"
        else:
            scope_label = "tutto il dataset"

    metrics_view = metrics_raw[metrics_raw["lead_days"].isin(leadtimes)].copy() if not metrics_raw.empty else pd.DataFrame()
    if not metrics_view.empty:
        metrics_view["Lead Time"] = metrics_view["lead_days"].apply(
            lambda d: f"D-{int(d)} ({int(d) * 24}{T('hours_before_suffix')})"
        )

    col_tbl, col_hour, col_lead = st.columns([5, 3, 3])

    with col_tbl:
        st.markdown(f"<div class='t-chart-title'>{T('error_metrics_title')}</div>", unsafe_allow_html=True)
        if metrics_view.empty:
            st.caption(T("no_obs_caption"))
        else:
            show_cols = ["Lead Time", "MAE (MW)", "WMAPE (%)", "RMSE (MW)", "Max Error (MW)", "Bias (MW)"]
            st.dataframe(
                metrics_view[show_cols].set_index("Lead Time"),
                use_container_width=True, height=38 * (len(metrics_view) + 1),
            )

    with col_hour:
        h_title_col, h_sel_col = st.columns([3, 2])
        with h_title_col:
            st.markdown(f"<div class='t-chart-title'>{T('error_by_hour_title')}</div>", unsafe_allow_html=True)
        with h_sel_col:
            selected_hour_metric = st.selectbox(
                "hour_metric_sel",
                options=list(HOUR_METRICS.keys()),
                index=0,
                key="hour_metric_selector",
                label_visibility="collapsed",
            )
        if metrics_view.empty:
            st.caption("—")
        else:
            st.plotly_chart(
                build_error_by_hour_chart(metrics_df, leadtimes, metric_key=selected_hour_metric),
                use_container_width=True, config={"displayModeBar": False},
            )

    with col_lead:
        l_title_col, l_sel_col = st.columns([3, 2])
        with l_title_col:
            st.markdown(f"<div class='t-chart-title'>{T('error_vs_lead_title')}</div>", unsafe_allow_html=True)
        with l_sel_col:
            selected_lead_metric = st.selectbox(
                "lead_metric_sel",
                options=list(LEAD_METRICS.keys()),
                index=list(LEAD_METRICS.keys()).index("Bias (MW)"),
                key="lead_metric_selector",
                label_visibility="collapsed",
            )
        if metrics_view.empty:
            st.caption("—")
        else:
            st.plotly_chart(
                build_error_vs_lead_chart(metrics_view, metric_key=selected_lead_metric),
                use_container_width=True, config={"displayModeBar": False},
            )

    st.caption(f"ℹ️ Metriche calcolate su: {scope_label}. Il range è cappato all'ultima data con consuntivo disponibile.")


# ══════════════════════════════════════════════════════════════════════════════
#  ROUTER PRINCIPALE
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.dashboard_mode == "LOAD":
    render_load_dashboard()
elif st.session_state.dashboard_mode == "PV":
    render_pv_dashboard()
else:
    render_comparison_dashboard()
