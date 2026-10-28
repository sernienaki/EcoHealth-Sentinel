"""Outbreak trend monitoring. Demo values are synthetic; no alerts are generated."""
import datetime as dt
import pandas as pd
import plotly.express as px
import streamlit as st

PRIORITY_CONDITIONS = ["Cholera", "Acute watery diarrhoea", "Malaria", "Dengue", "Measles", "Unusual severe febrile illness"]
REQUIRED = ["epi_week", "condition", "region", "cases", "deaths", "reports_expected", "reports_received", "period_type", "source_name", "source_date", "data_status"]


def _week_date(value):
    try:
        return dt.datetime.strptime(str(value).strip().upper(), "%G-W%V").date()
    except (ValueError, TypeError):
        return None


def _synthetic():
    rows = []
    start = dt.date(2026, 1, 5)
    conditions = {
        "Cholera": [2, 3, 2, 4, 3, 5, 4, 6],
        "Acute watery diarrhoea": [42, 45, 40, 48, 46, 53, 51, 57],
        "Malaria": [80, 77, 85, 82, 90, 87, 94, 96],
        "Dengue": [1, 0, 2, 1, 2, 3, 2, 4],
        "Measles": [0, 1, 0, 1, 0, 1, 2, 1],
        "Unusual severe febrile illness": [3, 4, 3, 5, 4, 6, 5, 7],
    }
    regions = ["Mwanza", "Arusha", "Kilimanjaro", "Dodoma"]
    for ci, (condition, values) in enumerate(conditions.items()):
        for wi, value in enumerate(values):
            iso = (start + dt.timedelta(weeks=wi)).isocalendar()
            week = f"{iso.year}-W{iso.week:02d}"
            region = regions[(wi + ci) % len(regions)]
            for period, cases in [("baseline", max(0, value - (wi % 3))), ("current", value)]:
                rows.append({"epi_week": week, "condition": condition, "region": region, "cases": cases,
                    "deaths": 0, "reports_expected": 20, "reports_received": 18 + wi % 3,
                    "period_type": period, "source_name": "Synthetic demo generator",
                    "source_date": dt.date.today().isoformat(), "data_status": "synthetic"})
    return pd.DataFrame(rows)


def _read_upload(upload):
    try:
        df = pd.read_csv(upload) if upload.name.lower().endswith(".csv") else pd.read_excel(upload)
    except Exception as exc:
        return None, [f"Could not read file: {exc}"]
    df.columns = [str(c).strip().lower() for c in df.columns]
    missing = [c for c in REQUIRED if c not in df.columns]
    if missing:
        return None, ["Missing required columns: " + ", ".join(missing)]
    if df.empty:
        return None, ["The uploaded file has no rows."]
    df["epi_week"] = df["epi_week"].astype(str).str.strip().str.upper()
    df["week_date"] = df["epi_week"].map(_week_date)
    errors = []
    if df["week_date"].isna().any():
        errors.append("Invalid epi_week. Use ISO labels such as 2026-W04.")
    for col in ["cases", "deaths", "reports_expected", "reports_received"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        if df[col].isna().any() or (df[col] < 0).any():
            errors.append(f"{col} must contain non-negative numeric values.")
    if ((df["reports_received"] > df["reports_expected"]) & df["reports_expected"].notna()).any():
        errors.append("reports_received exceeds reports_expected in one or more rows.")
    df["period_type"] = df["period_type"].astype(str).str.strip().str.lower()
    if not df["period_type"].isin(["current", "baseline"]).all():
        errors.append("period_type must be current or baseline.")
    df["data_status"] = df["data_status"].astype(str).str.strip().str.lower()
    if not df["data_status"].isin(["official", "synthetic", "illustrative"]).all():
        errors.append("data_status must be official, synthetic or illustrative.")
    for col in ["condition", "region", "source_name", "source_date"]:
        df[col] = df[col].fillna("").astype(str).str.strip()
        if (df[col] == "").any():
            errors.append(f"{col} must not be blank.")
    if df.duplicated(["epi_week", "condition", "region", "period_type"]).any():
        errors.append("Duplicate epi_week + condition + region + period_type rows; aggregate or deduplicate first.")
    return (None, errors) if errors else (df, [])


def render_outbreak_trends_tab(lang="en"):
    sw = lang == "sw"
    tr = lambda en, sw_text: sw_text if sw else en
    st.header(tr("Outbreak Trend Monitoring", "Ufuatiliaji wa Mwenendo wa Milipuko"))
    st.error(tr(
        "DATA GOVERNANCE: No outbreak alerts are generated. Demo data are synthetic. Uploaded data must be authorized and verified before operational interpretation.",
        "USIMAMIZI WA DATA: Hakuna tahadhari za milipuko zinazotolewa. Data za mfano ni za kuiga. Data zilizopakiwa lazima ziidhinishwe na kuthibitishwa kabla ya matumizi ya kiutendaji."
    ))
    st.caption(tr(
        "Explore epidemiological-week trends, reporting completeness, geographic distribution and descriptive comparison with a supplied baseline. Approved national case definitions and thresholds are not configured in this prototype.",
        "Chunguza mwenendo kwa wiki za epidemiolojia, ukamilifu wa taarifa, usambazaji wa kijiografia na ulinganisho na data za msingi. Ufafanuzi na vizingiti vya kitaifa vilivyoidhinishwa havijawekwa kwenye mfano huu."
    ))
    st.markdown("**Priority conditions:** " + ", ".join(PRIORITY_CONDITIONS))
    st.markdown(tr(
        "Required columns: epi_week, condition, region, cases, deaths, reports_expected, reports_received, period_type, source_name, source_date, data_status. One row per week, condition, region and period type. Baseline rows should use comparable weeks, case definitions and geography.",
        "Safu zinazohitajika: epi_week, condition, region, cases, deaths, reports_expected, reports_received, period_type, source_name, source_date, data_status. Mstari mmoja kwa wiki, hali, mkoa na aina ya kipindi. Data za msingi zitumie wiki, ufafanuzi wa visa na maeneo yanayolingana."
    ))
    template = pd.DataFrame([
        {"epi_week":"2026-W04","condition":"Cholera","region":"Example region","cases":0,"deaths":0,"reports_expected":0,"reports_received":0,"period_type":"current","source_name":"Enter verified source","source_date":"YYYY-MM-DD","data_status":"official"},
        {"epi_week":"2026-W04","condition":"Cholera","region":"Example region","cases":0,"deaths":0,"reports_expected":0,"reports_received":0,"period_type":"baseline","source_name":"Enter verified baseline source","source_date":"YYYY-MM-DD","data_status":"official"}])
    with st.expander(tr("Download CSV template", "Pakua kiolezo cha CSV")):
        st.download_button(tr("Download template", "Pakua kiolezo"), template.to_csv(index=False).encode("utf-8"),
            file_name="ecohealth_outbreak_trends_template.csv", mime="text/csv")
    mode = st.radio(tr("Data source", "Chanzo cha data"),
        [tr("Synthetic demonstration", "Maonyesho ya data za kuiga"), tr("Upload authorized dataset", "Pakia data zilizoidhinishwa")],
        horizontal=True, key="outbreak_trends_mode")
    if mode == tr("Synthetic demonstration", "Maonyesho ya data za kuiga"):
        df = _synthetic()
        st.warning(tr("SIMULATION ONLY — all values are fabricated for interface testing. No real-world inference or alerting.",
                      "MAJARIBIO PEKEE — thamani zote zimebuniwa kwa kujaribu kiolesura. Hakuna hitimisho la hali halisi au tahadhari."))
    else:
        upload = st.file_uploader(tr("Upload CSV or Excel", "Pakia CSV au Excel"), type=["csv", "xlsx"], key="outbreak_trends_upload")
        if upload is None:
            st.info(tr("Upload a dataset to view trends. No example values are substituted.", "Pakia data kuona mwenendo. Hakuna thamani za mfano zitakazotumika badala yake."))
            return
        df, errors = _read_upload(upload)
        if errors:
            st.error(tr("File validation failed:", "Ukaguzi wa faili umeshindwa:") + "\n- " + "\n- ".join(errors))
            return
        if not df["data_status"].eq("official").all():
            st.warning(tr("Synthetic or illustrative rows are present. Results are descriptive only; no alerts are generated.",
                          "Kuna mistari ya kuiga au ya maonyesho. Matokeo ni ya maelezo tu; hakuna tahadhari zinazotolewa."))
        elif df["source_name"].str.contains("demo|synthetic|illustrative", case=False, regex=True).any():
            st.warning(tr("Source labels suggest demo data. Verify provenance before interpreting results.", "Lebo za chanzo zinaashiria data za maonyesho. Thibitisha chanzo kabla ya kutafsiri matokeo."))
    if "week_date" not in df:
        df["week_date"] = df["epi_week"].map(_week_date)
    conditions = sorted(df["condition"].dropna().unique().tolist())
    regions = sorted(df["region"].dropna().unique().tolist())
    a, b = st.columns(2)
    with a:
        selected_conditions = st.multiselect(tr("Conditions", "Hali"), conditions,
            default=[c for c in PRIORITY_CONDITIONS if c in conditions] or conditions[:1])
    with b:
        selected_regions = st.multiselect(tr("Regions", "Mikoa"), regions, default=regions)
    periods = [p for p in ["current", "baseline"] if p in df["period_type"].unique()]
    selected_periods = st.multiselect(tr("Periods", "Vipindi"), periods, default=periods)
    view = df[df["condition"].isin(selected_conditions) & df["region"].isin(selected_regions) & df["period_type"].isin(selected_periods)].copy()
    if view.empty:
        st.info(tr("No rows match these filters.", "Hakuna mistari inayolingana na vichujio hivi."))
        return
    valid = view[view["reports_expected"] > 0].copy()
    valid["completeness_pct"] = valid["reports_received"] / valid["reports_expected"] * 100
    k1, k2, k3, k4 = st.columns(4)
    k1.metric(tr("Rows", "Mistari"), len(view))
    k2.metric(tr("Reported cases", "Visa vilivyoripotiwa"), int(view["cases"].sum()))
    k3.metric(tr("Reported deaths", "Vifo vilivyoripotiwa"), int(view["deaths"].sum()))
    k4.metric(tr("Mean reporting completeness", "Wastani wa ukamilifu"),
        f"{valid['completeness_pct'].mean():.1f}%" if not valid.empty else tr("Not available", "Haipatikani"))
    if valid.empty:
        st.info(tr("Completeness cannot be calculated because reports_expected is zero.", "Ukamilifu hauwezi kuhesabiwa kwa sababu reports_expected ni sifuri."))
    st.subheader(tr("Weekly case trends", "Mwenendo wa visa kwa wiki"))
    weekly = view.groupby(["week_date", "epi_week", "condition", "period_type"], as_index=False).agg(cases=("cases", "sum"))
    fig = px.line(weekly.sort_values("week_date"), x="week_date", y="cases", color="condition", line_dash="period_type",
        markers=True, hover_data=["epi_week", "period_type"],
        labels={"week_date":"Epidemiological week","cases":"Reported cases","condition":"Condition","period_type":"Period"})
    st.plotly_chart(fig, use_container_width=True)
    st.subheader(tr("Geographic distribution", "Usambazaji wa kijiografia"))
    geo = view[view["period_type"] == "current"].groupby(["region", "condition"], as_index=False).agg(cases=("cases","sum"), deaths=("deaths","sum"))
    if not geo.empty:
        st.plotly_chart(px.bar(geo, x="region", y="cases", color="condition", barmode="group", hover_data=["deaths"],
            labels={"region":"Region","cases":"Reported cases","condition":"Condition"}), use_container_width=True)
    st.subheader(tr("Reporting completeness by epidemiological week", "Ukamilifu wa taarifa kwa wiki"))
    if not valid.empty:
        comp = valid.groupby(["week_date", "epi_week", "period_type"], as_index=False).agg(
            reports_received=("reports_received","sum"), reports_expected=("reports_expected","sum"))
        comp["completeness_pct"] = comp["reports_received"] / comp["reports_expected"] * 100
        st.plotly_chart(px.line(comp.sort_values("week_date"), x="week_date", y="completeness_pct", color="period_type", markers=True,
            labels={"week_date":"Epidemiological week","completeness_pct":"Completeness (%)","period_type":"Period"}), use_container_width=True)
    st.subheader(tr("Descriptive baseline comparison", "Ulinganisho wa maelezo na data za msingi"))
    current = df[df["period_type"] == "current"]
    baseline = df[df["period_type"] == "baseline"]
    if current.empty or baseline.empty:
        st.info(tr("Comparison requires both current and baseline rows.", "Ulinganisho unahitaji data za sasa na za msingi."))
    else:
        base = baseline.groupby(["condition","region","epi_week"], as_index=False).agg(baseline_mean=("cases","mean"))
        compare = current.merge(base, on=["condition","region","epi_week"], how="left")
        compare["difference_cases"] = compare["cases"] - compare["baseline_mean"]
        compare["difference_pct"] = compare.apply(lambda r: (r["difference_cases"] / r["baseline_mean"] * 100)
            if pd.notna(r["baseline_mean"]) and r["baseline_mean"] != 0 else None, axis=1)
        compare = compare[compare["condition"].isin(selected_conditions) & compare["region"].isin(selected_regions)]
        st.dataframe(compare[["epi_week","condition","region","cases","baseline_mean","difference_cases","difference_pct","source_name","source_date","data_status"]],
            use_container_width=True, hide_index=True)
        st.caption(tr("Differences are descriptive only. No outbreak threshold is applied and no alert is generated. Qualified surveillance staff must review baseline suitability, definitions, reporting coverage and source authorization.",
            "Tofauti ni za maelezo tu. Hakuna kizingiti cha mlipuko kinachotumika wala tahadhari inayotolewa. Wataalamu wa ufuatiliaji lazima wakague ufaafu wa msingi, ufafanuzi, ukamilifu wa taarifa na idhini ya chanzo."))
    with st.expander(tr("Data provenance and quality checks", "Chanzo cha data na ukaguzi wa ubora")):
        st.dataframe(df[["source_name","source_date","data_status"]].drop_duplicates(), use_container_width=True, hide_index=True)
        st.write(tr("Validate case definitions, reporting unit, denominators, baseline period, completeness and authorization before operational use.",
            "Thibitisha ufafanuzi wa visa, kitengo cha taarifa, denominators, kipindi cha msingi, ukamilifu na idhini kabla ya matumizi ya kiutendaji."))
    st.download_button(tr("Download filtered data", "Pakua data zilizochujwa"), view.drop(columns=["week_date"], errors="ignore").to_csv(index=False).encode("utf-8"),
        file_name="ecohealth_outbreak_trends_filtered.csv", mime="text/csv")
