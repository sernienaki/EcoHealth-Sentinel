"""Visuals for EcoHealth Sentinel: bullet charts, heatmap matrix, risk shaded map, weekly trend with alert line."""
import os
import json
import zlib
import datetime
import numpy as np
from agents import SCENARIOS, DEFAULT_CTX, assess, checks_for, pipe_checks, _off, _missed
from packs import HERE

PERCENT = {"mal_pos", "llin", "anc4", "sba", "sam", "fic", "penta_drop", "htn", "dm", "cervical", "tobacco", "stockout", "oop"}
LABEL_KEY = {"mal": "malaria"}
BULLET_KEYS = ["mal", "cholera", "mmr", "imr", "anc4", "sba", "fic", "penta_drop", "stockout", "hw", "htn", "oop"]
ALL_KEYS = ["mal", "mal_pos", "cholera", "tb", "llin", "mmr", "imr", "anc4", "sba", "sam", "fic", "penta_drop", "htn", "dm", "cervical", "tobacco", "stockout", "hw", "oop"]
SHORT = {"mal": ("Malaria", "Malaria"), "mal_pos": ("Malaria positivity", "Malaria chanya"), "cholera": ("Cholera", "Kipindupindu"), "tb": ("TB", "TB"),
         "llin": ("Bed nets", "Vyandarua"), "mmr": ("Maternal deaths", "Vifo vya mama"), "imr": ("Infant deaths", "Vifo vya watoto"), "anc4": ("ANC 4+", "ANC 4+"),
         "sba": ("Skilled birth", "Mtaalamu"), "sam": ("Malnutrition", "Utapiamlo"), "fic": ("Fully immunized", "Chanjo kamili"), "penta_drop": ("Penta3 dropout", "Penta3 kushuka"),
         "htn": ("BP screening", "Shinikizo"), "dm": ("Diabetes screening", "Kisukari"), "cervical": ("Cervical screening", "Shingo ya kizazi"), "tobacco": ("Tobacco", "Tumbaku"),
         "stockout": ("Stockout", "Uhaba wa dawa"), "hw": ("Health workers", "Watumishi"), "oop": ("Out of pocket", "Gharama mfukoni")}
SEV_COL = ["#2e9e5b", "#f0b429", "#f08a29", "#d64545"]
SEV_NAME = {"en": ["on target", "within 5%", "off target", "far off"], "sw": ["kwenye lengo", "ndani ya 5%", "nje ya lengo", "mbali sana"]}
RISK_COL = {"LOW": "#2e9e5b", "MEDIUM": "#f0b429", "HIGH": "#d64545"}
BAND = {"good": "rgba(46,158,91,0.25)", "watch": "rgba(240,180,41,0.30)", "poor": "rgba(214,69,69,0.30)"}

TXT = {
    "en": {"bul_cap": "Bar color: 🟩 on target, 🟨 within 5%, 🟧 off target, 🟥 far off. Black line is the national target. Shaded bands show good, watch and poor zones.",
           "bul_sent": "{region}: {k} of {n} key indicators are off target{names}.", "heat_h": "Regions by indicator", "heat_cap": "🟩 on target  🟨 within 5%  🟧 off target  🟥 far off. Worst indicators are at the top. Black frame is the selected region.",
           "heat_sent": "Most often off target: {ind} ({c} of {n} regions).", "heat_none": "Every region is on target for every indicator.",
           "map_h": "Risk map", "layer": "Map layer", "overall": "Overall regional risk", "risk_word": "risk", "tap": "Tap a region to filter the whole dashboard.",
           "proxy": "Circles are proxy shading. Add a boundary file to the country pack for true region shapes.", "noclick": "Install streamlit-folium to enable tap to filter. Use the sidebar meanwhile.",
           "sel": "Selected region", "leg_risk": "🟩 LOW  🟨 MEDIUM  🟥 HIGH", "leg_sev": "🟩 on target  🟨 within 5%  🟧 off target  🟥 far off", "unm": "Boundary names not matched",
           "trend_h": "Weekly trend with alert line", "ind": "Indicator", "sim": "SIMULATED weekly data for demonstration. Add real weekly counts under 'weekly' in the country pack to replace it.",
           "alert_s": "Alert: the latest week ({v}) is above the alert threshold ({thr}). {n} alert week(s) in the last 8 weeks.", "ok_s": "The latest week ({v}) is within the expected range (alert threshold {thr}).",
           "method": "Alert line = average of the previous 8 weeks plus 2 standard deviations.", "avg": "4 week average", "thr": "Alert threshold", "wk": "Weekly value", "al": "Alert weeks"},
    "sw": {"bul_cap": "Rangi ya mstari: 🟩 kwenye lengo, 🟨 ndani ya 5%, 🟧 nje ya lengo, 🟥 mbali sana. Mstari mweusi ni lengo la taifa. Maeneo yenye kivuli yanaonyesha nzuri, angalia na hafifu.",
           "bul_sent": "{region}: viashiria {k} kati ya {n} vya msingi viko nje ya lengo{names}.", "heat_h": "Mikoa kwa kiashiria", "heat_cap": "🟩 kwenye lengo  🟨 ndani ya 5%  🟧 nje ya lengo  🟥 mbali sana. Viashiria vibaya zaidi viko juu. Fremu nyeusi ni mkoa uliochaguliwa.",
           "heat_sent": "Mara nyingi nje ya lengo: {ind} (mikoa {c} kati ya {n}).", "heat_none": "Kila mkoa uko kwenye lengo kwa kila kiashiria.",
           "map_h": "Ramani ya hatari", "layer": "Tabaka la ramani", "overall": "Hatari ya jumla ya mkoa", "risk_word": "hatari", "tap": "Gusa mkoa kuchuja dashibodi nzima.",
           "proxy": "Miduara ni kivuli cha mfano. Ongeza faili la mipaka kwenye kifurushi cha nchi kupata maumbo halisi ya mikoa.", "noclick": "Sakinisha streamlit-folium kuwezesha kuchuja kwa kugusa. Tumia menyu ya pembeni kwa sasa.",
           "sel": "Mkoa uliochaguliwa", "leg_risk": "🟩 CHINI  🟨 WASTANI  🟥 JUU", "leg_sev": "🟩 kwenye lengo  🟨 ndani ya 5%  🟧 nje ya lengo  🟥 mbali sana", "unm": "Majina ya mipaka yasiyolingana",
           "trend_h": "Mwenendo wa kila wiki na mstari wa tahadhari", "ind": "Kiashiria", "sim": "DATA YA MFANO ya kila wiki kwa maonyesho. Ongeza data halisi ya kila wiki chini ya 'weekly' kwenye kifurushi cha nchi kuibadilisha.",
           "alert_s": "Tahadhari: wiki ya mwisho ({v}) iko juu ya kiwango cha tahadhari ({thr}). Wiki {n} za tahadhari katika wiki 8 zilizopita.", "ok_s": "Wiki ya mwisho ({v}) iko ndani ya kiwango kinachotarajiwa (kiwango cha tahadhari {thr}).",
           "method": "Mstari wa tahadhari = wastani wa wiki 8 zilizopita pamoja na mikengeuko 2 ya kawaida.", "avg": "Wastani wa wiki 4", "thr": "Kiwango cha tahadhari", "wk": "Thamani ya wiki", "al": "Wiki za tahadhari"},
}


# ------------------------------------------------------------------ helpers
def _ctx(ctx):
    return ctx or DEFAULT_CTX


def severity(key, v, t, d, alert):
    """0 on target, 1 within 5% tolerance, 2 off target, 3 far off."""
    if not _off(v, t, d):
        return 1 if _missed(v, t, d) else 0
    if t == 0:
        return 3 if (key == "cholera" and v > alert) else 2
    ratio = v / t if d == "lower" else (t / v if v > 0 else 9)
    return 2 if ratio <= 1.5 else 3


def _label(L, key):
    return L[LABEL_KEY.get(key, key)]


def _short(lang, key):
    return SHORT[key][0 if lang == "en" else 1]


def _fmt(key, v):
    v = float(v)
    return f"{v:.2f}" if key == "hw" else (f"{v:.0f}" if v >= 100 or v.is_integer() else f"{v:.1f}")


def _style(fig, theme):
    color = "#fafafa" if theme == "dark" else "#262730"
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color=color, size=12))
    return fig


# ------------------------------------------------------------------ 1. bullet charts
def render_bullets(L, lang, region, data, ctx, theme):
    import streamlit as st
    import plotly.graph_objects as go
    ctx = _ctx(ctx)
    alert, x = ctx["cholera_alert"], TXT[lang]
    n, fig, sevs = len(BULLET_KEYS), go.Figure(), {}
    for i, k in enumerate(BULLET_KEYS):
        t, d = ctx["targets"][k]
        v = float(data[k])
        s = sevs[k] = severity(k, v, t, d, alert)
        pct = k in PERCENT
        if d == "lower":
            mx = max(v * 1.2, 1.0) if t == 0 else max(v, t * 2) * 1.05
            mx = min(mx, 100) if pct else mx
            cut = lambda a, b: [min(a, mx), min(b, mx)]
            steps = [{"range": [0, mx], "color": BAND["poor"]}] if t == 0 else [
                {"range": cut(0, t * 1.05), "color": BAND["good"]}, {"range": cut(t * 1.05, t * 1.5), "color": BAND["watch"]}, {"range": cut(t * 1.5, mx), "color": BAND["poor"]}]
        else:
            mx = 100 if pct else max(v, t) * 1.4
            steps = [{"range": [0, t * 0.7], "color": BAND["poor"]}, {"range": [t * 0.7, t * 0.95], "color": BAND["watch"]}, {"range": [t * 0.95, mx], "color": BAND["good"]}]
        y1 = 1 - i / n
        fig.add_trace(go.Indicator(
            mode="number+gauge", value=v, domain={"x": [0.38, 1], "y": [y1 - 1 / n + 0.015, y1 - 0.015]},
            title={"text": _short(lang, k), "font": {"size": 12}},
            number={"font": {"size": 14}, "suffix": "%" if pct else "", "valueformat": ".2f" if k == "hw" else (".0f" if v >= 100 or v.is_integer() else ".1f")},
            gauge={"shape": "bullet", "axis": {"range": [0, mx], "tickfont": {"size": 9}}, "bar": {"color": SEV_COL[s], "thickness": 0.55},
                   "steps": steps, "threshold": {"line": {"color": "#111111" if theme != "dark" else "#ffffff", "width": 3}, "thickness": 0.85, "value": t}}))
    fig.update_layout(height=56 * n + 30, margin=dict(l=5, r=25, t=10, b=10))
    st.plotly_chart(_style(fig, theme), use_container_width=True, theme=None, key="bullets_chart")
    off = [k for k in BULLET_KEYS if sevs[k] >= 2]
    names = ": " + ", ".join(_short(lang, k) for k in sorted(off, key=lambda k: -sevs[k])[:3]) if off else ""
    st.write(x["bul_sent"].format(region=region, k=len(off), n=n, names=names))
    st.caption(x["bul_cap"])


# ------------------------------------------------------------------ 2. heatmap matrix
def render_heatmap(L, lang, regions, ctx, region, theme):
    import streamlit as st
    import plotly.graph_objects as go
    ctx = _ctx(ctx)
    alert, x = ctx["cholera_alert"], TXT[lang]
    names = list(regions)
    sev = {k: [severity(k, float(regions[r][k]), *ctx["targets"][k], alert) for r in names] for k in ALL_KEYS}
    order = sorted(ALL_KEYS, key=lambda k: -sum(s >= 2 for s in sev[k]))
    z = [sev[k] for k in order]
    text = [[_fmt(k, regions[r][k]) for r in names] for k in order]
    c = SEV_COL
    scale = [[0, c[0]], [1 / 6, c[0]], [1 / 6, c[1]], [.5, c[1]], [.5, c[2]], [5 / 6, c[2]], [5 / 6, c[3]], [1, c[3]]]
    fig = go.Figure(go.Heatmap(z=z, x=names, y=[_short(lang, k) for k in order], text=text, texttemplate="%{text}", textfont={"size": 11, "color": "#111111"},
                               colorscale=scale, zmin=0, zmax=3, showscale=False, xgap=2, ygap=2, hovertemplate="%{y}<br>%{x}: %{text}<extra></extra>"))
    if region in names:
        i = names.index(region)
        fig.add_shape(type="rect", x0=i - 0.5, x1=i + 0.5, y0=-0.5, y1=len(order) - 0.5, line=dict(color="#111111" if theme != "dark" else "#ffffff", width=3))
    fig.update_layout(height=24 * len(order) + 90, margin=dict(l=5, r=5, t=40, b=5), yaxis=dict(autorange="reversed"), xaxis=dict(side="top"))
    st.subheader(x["heat_h"])
    st.plotly_chart(_style(fig, theme), use_container_width=True, theme=None, key="heat_chart")
    top = order[0]
    cnt = sum(s >= 2 for s in sev[top])
    st.write(x["heat_sent"].format(ind=_short(lang, top), c=cnt, n=len(names)) if cnt else x["heat_none"])
    st.caption(x["heat_cap"])


# ------------------------------------------------------------------ 3. risk shaded map with click to filter
def layer_levels(choice, regions, ctx, lang, L):
    ctx = _ctx(ctx)
    alert, out = ctx["cholera_alert"], {}
    for name, row in regions.items():
        if choice == "overall" or choice in SCENARIOS:
            a = assess(pipe_checks(ctx) if choice == "overall" else checks_for(choice, ctx), row, alert)
            out[name] = {"color": RISK_COL[a["level"]], "text": f"{a['level']} ({a['off']}/{a['n']})"}
        else:
            t, d = ctx["targets"][choice]
            s = severity(choice, float(row[choice]), t, d, alert)
            out[name] = {"color": SEV_COL[s], "text": f"{_fmt(choice, row[choice])} ({SEV_NAME[lang][s]})"}
    return out


def _load_boundaries(pack, names):
    """Return (features, matched, unmatched) from the pack's optional GeoJSON boundary file."""
    if not pack or not pack.get("boundaries"):
        return None, [], []
    try:
        gj = json.load(open(os.path.join(HERE, pack["boundaries"]), encoding="utf-8"))
    except Exception:
        return None, [], []
    field = pack.get("boundary_name_field", "shapeName")
    lookup = {n.lower().strip(): n for n in names}
    feats, matched = [], set()
    for f in gj.get("features", []):
        raw = str(f.get("properties", {}).get(field, "")).lower().strip()
        feats.append((f, lookup.get(raw)))
        if raw in lookup:
            matched.add(lookup[raw])
    return feats, sorted(matched), sorted(set(names) - matched)


def render_risk_map(L, lang, pack, regions, ctx, region, theme):
    import streamlit as st
    import folium
    import streamlit.components.v1 as components
    try:
        from streamlit_folium import st_folium
    except Exception:
        st_folium = None
    ctx = _ctx(ctx)
    x = TXT[lang]
    st.subheader(f"🗺️ {x['map_h']}")
    layers = ["overall"] + list(SCENARIOS) + ALL_KEYS
    name_of = lambda c: x["overall"] if c == "overall" else (f"{SCENARIOS[c][lang]} ({x['risk_word']})" if c in SCENARIOS else _label(L, c))
    choice = st.selectbox(x["layer"], layers, format_func=name_of, key="map_layer")
    lv = layer_levels(choice, regions, ctx, lang, L)
    lat = [r["lat"] for r in regions.values()]
    lon = [r["lon"] for r in regions.values()]
    m = folium.Map(location=[float(np.mean(lat)), float(np.mean(lon))], zoom_start=6, tiles="OpenStreetMap")
    if len(regions) > 1:
        m.fit_bounds([[min(lat) - 0.5, min(lon) - 0.5], [max(lat) + 0.5, max(lon) + 0.5]])
    feats, matched, unmatched = _load_boundaries(pack, list(regions))
    if feats:
        for f, nm in feats:
            info = lv.get(nm)
            col = info["color"] if info else "#9aa0a6"
            tip = f"{nm}: {info['text']}" if info else str(next(iter(f.get("properties", {}).values()), ""))
            folium.GeoJson(f, tooltip=tip, style_function=lambda _f, col=col, sel=(nm == region): {
                "fillColor": col, "color": "#111111" if sel else "#555555", "weight": 4 if sel else 1, "fillOpacity": 0.6 if col != "#9aa0a6" else 0.1}).add_to(m)
        if unmatched:
            st.caption(f"{x['unm']}: {', '.join(unmatched)}")
    else:
        km = (pack or {}).get("circle_km", 45 if pack else 150) * 1000
        for nm, row in regions.items():
            info = lv[nm]
            folium.Circle([row["lat"], row["lon"]], radius=km, color="#111111" if nm == region else info["color"], weight=4 if nm == region else 1,
                          fill=True, fill_color=info["color"], fill_opacity=0.55, tooltip=f"{nm}: {info['text']}").add_to(m)
        st.caption(x["proxy"])
    st.caption(x["leg_risk"] if (choice == "overall" or choice in SCENARIOS) else x["leg_sev"])
    n = st.session_state.get("_map_n", 0)
    if st_folium:
        st.caption(x["tap"])
        out = st_folium(m, height=420, use_container_width=True, returned_objects=["last_object_clicked_tooltip"], key=f"riskmap_{ctx['code']}_{n}")
        tip = (out or {}).get("last_object_clicked_tooltip")
        hit = [r for r in regions if tip and r.lower() in str(tip).lower()]
        if hit:
            st.session_state["_map_n"] = n + 1  # new component instance, so a stale click cannot override the sidebar later
            pick = max(hit, key=len)
            if pick != region:
                st.session_state["_pending_region"] = pick
            st.rerun()
    else:
        components.html(m._repr_html_(), height=420)
        st.info(x["noclick"])
    a = assess(pipe_checks(ctx), regions[region], ctx["cholera_alert"]) if region in regions else None
    if a:
        st.write(f"**{x['sel']}:** {region} | {x['overall']}: **{a['level']}** ({a['off']}/{a['n']})")


# ------------------------------------------------------------------ 4. weekly trend with alert line
def weekly_series(code, region, key, value, ramp, pack=None, weeks=26):
    """Return (values, simulated). Uses pack['weekly'][region][key] when present."""
    real = ((pack or {}).get("weekly", {}) or {}).get(region, {}).get(key)
    if real:
        return np.array(real, dtype=float), False
    rng = np.random.default_rng(zlib.crc32(f"{code}|{region}|{key}".encode()))
    t = np.arange(weeks)
    base = max(float(value) / 8, 1.0) if key == "cholera" else max(float(value), 1.0)
    s = base * (1 + 0.15 * np.sin(2 * np.pi * t / 26)) * rng.lognormal(0, 0.15, weeks)
    if ramp:
        s[-5:] *= np.array([1.15, 1.4, 1.8, 2.3, 2.9])
    if key in PERCENT:
        s = np.minimum(s, 100)
    return (np.round(s) if key == "cholera" else np.round(s, 1)), True


def ears_threshold(series, window=8, k=2.0):
    """Alert line: mean of the previous `window` weeks plus k standard deviations."""
    thr = np.full(len(series), np.nan)
    for i in range(window, len(series)):
        base = series[i - window:i]
        m = base.mean()
        thr[i] = m + k * max(base.std(ddof=1), 1.0 if m >= 1 else 0.1)
    return thr


def render_trend(L, lang, pack, ctx, region, data, theme):
    import streamlit as st
    import plotly.graph_objects as go
    ctx = _ctx(ctx)
    x = TXT[lang]
    st.subheader(x["trend_h"])
    key = st.radio(x["ind"], ["cholera", "mal", "mal_pos"], format_func=lambda k: _label(L, k), horizontal=True, key="trend_key")
    v = float(data[key])
    t, d = ctx["targets"][key]
    ramp = v > ctx["cholera_alert"] if key == "cholera" else (d == "lower" and t > 0 and v > 1.5 * t)
    s, simulated = weekly_series(ctx["code"], region, key, v, ramp, pack)
    thr = ears_threshold(s)
    last_monday = datetime.date.today() - datetime.timedelta(days=datetime.date.today().weekday())
    dates = [last_monday - datetime.timedelta(weeks=len(s) - 1 - i) for i in range(len(s))]
    avg = np.array([s[max(0, i - 3):i + 1].mean() if i >= 3 else np.nan for i in range(len(s))])
    alerts = [i for i in range(len(s)) if not np.isnan(thr[i]) and s[i] > thr[i]]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dates, y=s, mode="lines+markers", name=x["wk"], line=dict(color="#1f77b4", width=2), marker=dict(size=5)))
    fig.add_trace(go.Scatter(x=dates, y=avg, mode="lines", name=x["avg"], line=dict(color="#7f7f7f", width=2, dash="dot")))
    fig.add_trace(go.Scatter(x=dates, y=thr, mode="lines", name=x["thr"], line=dict(color="#d64545", width=2, dash="dash", shape="hv")))
    if alerts:
        fig.add_trace(go.Scatter(x=[dates[i] for i in alerts], y=[s[i] for i in alerts], mode="markers", name=x["al"], marker=dict(color="#d64545", size=11, symbol="diamond")))
    fig.update_layout(height=340, margin=dict(l=5, r=10, t=10, b=5), legend=dict(orientation="h", y=-0.2), yaxis_title=_short(lang, key))
    st.plotly_chart(_style(fig, theme), use_container_width=True, theme=None, key="trend_chart")
    recent = sum(1 for i in alerts if i >= len(s) - 8)
    last_thr = thr[-1]
    if s[-1] > last_thr:
        st.error(x["alert_s"].format(v=_fmt(key, s[-1]), thr=_fmt(key, last_thr), n=recent))
    else:
        st.success(x["ok_s"].format(v=_fmt(key, s[-1]), thr=_fmt(key, last_thr)))
    st.caption(x["method"])
    if simulated:
        st.warning(f"🧪 {x['sim']}")
