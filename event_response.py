"""Event & Response Management module for EcoHealth Sentinel.

Prototype only: seeded events are synthetic. State is stored in Streamlit session memory,
not a durable database. Do not enter patient-identifiable information.
"""
from __future__ import annotations

import datetime as dt
import pandas as pd
import streamlit as st

SIMULATION_LABEL = "SIMULATION DATA — synthetic examples only; not live Ministry of Health surveillance data."
STATUS = {
    "reported": {"en": "Reported", "sw": "Imepokelewa"},
    "under_review": {"en": "Under review", "sw": "Inakaguliwa"},
    "verified": {"en": "Verified", "sw": "Imethibitishwa"},
    "not_verified": {"en": "Not verified", "sw": "Haijathibitishwa"},
    "response_active": {"en": "Response active", "sw": "Hatua za kukabiliana zinaendelea"},
    "closed": {"en": "Closed", "sw": "Imefungwa"},
}
NEXT = {
    "reported": ["under_review"],
    "under_review": ["verified", "not_verified"],
    "verified": ["response_active", "closed"],
    "response_active": ["closed"],
    "not_verified": ["closed"],
    "closed": [],
}
PRIORITIES = ["Low", "Moderate", "High", "Urgent"]
SIGNAL_TYPES = [
    "Unusual illness cluster", "Suspected priority disease", "Unusual deaths",
    "Animal health signal", "Environmental / WASH event", "Laboratory signal", "Other public health event"
]


def _now():
    return dt.datetime.now().astimezone().replace(microsecond=0).isoformat()


def _parse(value):
    if not value:
        return None
    try:
        return dt.datetime.fromisoformat(value)
    except (TypeError, ValueError):
        return None


def _seed_events():
    now = dt.datetime.now().astimezone().replace(microsecond=0)
    one = (now - dt.timedelta(days=2)).isoformat()
    two = (now - dt.timedelta(days=1, hours=3)).isoformat()
    three = (now - dt.timedelta(hours=6)).isoformat()
    return [
        {
            "event_id": "SIM-001", "title": "Unusual watery diarrhoea reports",
            "signal_type": "Unusual illness cluster", "region": "Mwanza",
            "district": "SIMULATED district", "location_detail": "SIMULATED community",
            "description": "Synthetic example for testing intake, review and response tracking.",
            "source_type": "Community report (simulated)", "priority": "High",
            "status": "reported", "reported_at": one, "onset_at": None, "detected_at": one,
            "notified_at": None, "response_started_at": None, "verified_at": None,
            "closed_at": None, "assigned_to": "Demo surveillance officer",
            "verification_note": "", "simulation": True,
            "tasks": [{"task_id": "SIM-001-T1", "task": "Contact the reporting focal point (simulation)",
                      "owner": "Demo reviewer", "due_at": (now + dt.timedelta(days=1)).date().isoformat(),
                      "status": "Open", "created_at": one, "completed_at": None}],
        },
        {
            "event_id": "SIM-002", "title": "Unusual fever cluster near a market",
            "signal_type": "Unusual illness cluster", "region": "Arusha",
            "district": "SIMULATED district", "location_detail": "SIMULATED market area",
            "description": "Synthetic example only; not a real event or alert.",
            "source_type": "Health facility report (simulated)", "priority": "Moderate",
            "status": "under_review", "reported_at": two, "onset_at": None, "detected_at": two,
            "notified_at": None, "response_started_at": None, "verified_at": None,
            "closed_at": None, "assigned_to": "Demo reviewer",
            "verification_note": "", "simulation": True, "tasks": [],
        },
        {
            "event_id": "SIM-003", "title": "Unusual animal deaths reported",
            "signal_type": "Animal health signal", "region": "Kilimanjaro",
            "district": "SIMULATED district", "location_detail": "SIMULATED village",
            "description": "Synthetic One Health example for workflow demonstration.",
            "source_type": "Community report (simulated)", "priority": "Low",
            "status": "not_verified", "reported_at": three, "onset_at": None, "detected_at": three,
            "notified_at": None, "response_started_at": None, "verified_at": None,
            "closed_at": None, "assigned_to": "Demo reviewer",
            "verification_note": "Synthetic example marked not verified.", "simulation": True, "tasks": [],
        },
    ]


def _init_state():
    if "event_response_records" not in st.session_state:
        st.session_state.event_response_records = _seed_events()
    if "event_response_audit" not in st.session_state:
        st.session_state.event_response_audit = [{
            "timestamp": _now(), "actor": "Prototype", "event_id": "SYSTEM",
            "action": "INITIALIZE_SIMULATION", "details": "Loaded synthetic sample events; no live surveillance data."
        }]


def _audit(event_id, action, details, actor="Prototype user"):
    st.session_state.event_response_audit.append({
        "timestamp": _now(), "actor": actor, "event_id": event_id,
        "action": action, "details": str(details)[:500],
    })


def _event_frame(events, lang):
    rows = []
    for e in events:
        rows.append({
            "Event ID": e["event_id"],
            "Signal": e["title"],
            "Region": e["region"],
            "Priority": e["priority"],
            "Status": STATUS[e["status"]][lang],
            "Reported at": e["reported_at"],
            "Assigned to": e.get("assigned_to") or "Unassigned",
            "Tasks open": sum(t["status"] == "Open" for t in e.get("tasks", [])),
        })
    return pd.DataFrame(rows)


def _elapsed(start, end=None):
    a, b = _parse(start), _parse(end) if end else dt.datetime.now().astimezone()
    if not a:
        return None
    return max(0, int((b - a).total_seconds() // 3600))


def _seven_one_seven(event):
    detected = event.get("detected_at")
    notified = event.get("notified_at")
    response = event.get("response_started_at")
    onset_to_detection = _elapsed(event.get("onset_at"), detected) if event.get("onset_at") and detected else None
    notify_hours = _elapsed(detected, notified) if notified else None
    response_hours = _elapsed(notified, response) if notified and response else None
    return [
        {"Milestone": "Onset → detection", "Hours": onset_to_detection,
         "Target": "≤168 h (7 days)", "Status": "Not recorded" if onset_to_detection is None else ("Within target" if onset_to_detection <= 168 else "Over target")},
        {"Milestone": "Detection → notification", "Hours": notify_hours,
         "Target": "≤24 h (1 day)", "Status": "Not recorded" if notify_hours is None else ("Within target" if notify_hours <= 24 else "Over target")},
        {"Milestone": "Notification → response start", "Hours": response_hours,
         "Target": "≤168 h (7 days)", "Status": "Not recorded" if response_hours is None else ("Within target" if response_hours <= 168 else "Over target")},
    ]


def _transition(event, new_status, note=""):
    old = event["status"]
    if new_status not in NEXT.get(old, []):
        return False
    event["status"] = new_status
    stamp = _now()
    if new_status == "verified":
        event["verified_at"] = stamp
        event["notified_at"] = event.get("notified_at") or stamp
    elif new_status == "response_active":
        event["notified_at"] = event.get("notified_at") or stamp
        event["response_started_at"] = stamp
    elif new_status == "closed":
        event["closed_at"] = stamp
    if note:
        event["verification_note"] = note
    _audit(event["event_id"], "STATUS_CHANGE", f"{old} -> {new_status}; {note}")
    return True


def render_event_response_tab(lang="en", region="National Overview"):
    _init_state()
    sw = lang == "sw"
    tr = lambda en, sw_text: sw_text if sw else en
    st.header(tr("Event & Response Management", "Usimamizi wa Matukio na Hatua za Kukabiliana"))
    st.error(tr(SIMULATION_LABEL, "DATA ZA KUIGA — mifano ya kutengenezwa tu; si data hai ya ufuatiliaji wa Wizara ya Afya."))
    st.caption(tr(
        "Use this sandbox to test report intake, human review, verification, response tasks and audit exports. Records live only in this Streamlit session and may disappear when it resets.",
        "Tumia mazingira haya kujaribu kupokea taarifa, ukaguzi wa binadamu, uthibitishaji, kazi za kukabiliana na kupakua kumbukumbu. Rekodi huhifadhiwa kwenye kikao hiki tu na zinaweza kupotea kikao kikianza upya."
    ))
    st.warning(tr(
        "Do not enter patient names, phone numbers, exact household addresses, clinical records or other identifying details. This prototype is not connected to eIDSR, DHIS2, FHIR or an official alert desk.",
        "Usiweke majina ya wagonjwa, namba za simu, anwani kamili za kaya, rekodi za kitabibu au taarifa zinazoweza kumtambua mtu. Mfumo huu haujaunganishwa na eIDSR, DHIS2, FHIR au dawati rasmi la tahadhari."
    ))

    events = st.session_state.event_response_records
    audit = st.session_state.event_response_audit
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(tr("Total events", "Matukio yote"), len(events))
    c2.metric(tr("Awaiting review", "Yanasubiri ukaguzi"), sum(e["status"] in ("reported", "under_review") for e in events))
    c3.metric(tr("Verified / active", "Yaliyothibitishwa / yanaendelea"), sum(e["status"] in ("verified", "response_active") for e in events))
    c4.metric(tr("Open response tasks", "Kazi wazi za kukabiliana"), sum(t["status"] == "Open" for e in events for t in e.get("tasks", [])))

    tab_inbox, tab_report, tab_audit = st.tabs([
        tr("Event inbox", "Orodha ya matukio"),
        tr("Report a signal", "Ripoti ishara"),
        tr("Audit trail", "Kumbukumbu ya ukaguzi"),
    ])

    with tab_inbox:
        st.subheader(tr("Event inbox and workflow", "Orodha ya matukio na mtiririko wa kazi"))
        st.dataframe(_event_frame(events, lang), use_container_width=True, hide_index=True)
        ids = [e["event_id"] for e in events]
        if not ids:
            st.info(tr("No events in this session.", "Hakuna matukio katika kikao hiki."))
        else:
            selected_id = st.selectbox(tr("Select event", "Chagua tukio"), ids, key="erm_selected_event")
            event = next(e for e in events if e["event_id"] == selected_id)
            st.markdown(f"### {event['event_id']} · {event['title']}")
            st.caption(f"{tr('SIMULATION RECORD', 'REKODI YA KUIGA')} · {event['source_type']}")
            st.write(f"**{tr('Description', 'Maelezo')}:** {event['description']}")
            st.write(f"**{tr('Location', 'Eneo')}:** {event['region']} · {event['district']} · {event['location_detail']}")
            st.write(f"**{tr('Status', 'Hali')}:** {STATUS[event['status']][lang]}")
            st.write(f"**{tr('Assigned reviewer', 'Mkaguzi aliyepangiwa')}:** {event.get('assigned_to') or tr('Unassigned', 'Hajapangiwa')}")
            with st.form(f"erm_update_{selected_id}"):
                owner = st.text_input(tr("Assigned role / reviewer label (no personal details)", "Jukumu / lebo ya mkaguzi (usiweke taarifa binafsi)"), value=event.get("assigned_to", ""))
                priority = st.selectbox(tr("Priority", "Kipaumbele"), PRIORITIES, index=PRIORITIES.index(event["priority"]))
                note = st.text_area(tr("Review / verification note (non-identifying)", "Dokezo la ukaguzi / uthibitishaji (bila taarifa za kumtambua mtu)"), value=event.get("verification_note", ""))
                save = st.form_submit_button(tr("Save review details", "Hifadhi maelezo ya ukaguzi"))
            if save:
                before = {"assigned_to": event.get("assigned_to"), "priority": event["priority"], "verification_note": event.get("verification_note", "")}
                event["assigned_to"], event["priority"], event["verification_note"] = owner.strip(), priority, note.strip()
                _audit(selected_id, "REVIEW_DETAILS_UPDATED", f"before={before}; after={{'assigned_to': {owner.strip()!r}, 'priority': {priority!r}, 'verification_note': {note.strip()!r}}}")
                st.success(tr("Review details saved and audited.", "Maelezo yamehifadhiwa na kurekodiwa kwenye kumbukumbu."))
                st.rerun()

            st.markdown("#### " + tr("Workflow action", "Hatua ya mtiririko wa kazi"))
            possible = NEXT.get(event["status"], [])
            if possible:
                action_cols = st.columns(min(3, len(possible)))
                for i, next_status in enumerate(possible):
                    label = STATUS[next_status][lang]
                    if action_cols[i].button(label, key=f"erm_transition_{selected_id}_{next_status}", use_container_width=True):
                        if _transition(event, next_status, event.get("verification_note", "")):
                            st.success(tr("Status transition saved to audit trail.", "Mabadiliko ya hali yamehifadhiwa kwenye kumbukumbu."))
                            st.rerun()
            else:
                st.info(tr("This event is closed. No further workflow transitions are available.", "Tukio limefungwa. Hakuna hatua nyingine za mtiririko zinazopatikana."))

            st.markdown("#### " + tr("7-1-7 monitoring (prototype)", "Ufuatiliaji wa 7-1-7 (mfano)"))
            st.caption(tr("These are monitoring targets, not an automatic declaration or replacement for national disease-specific guidance. Missing timestamps are shown as not recorded.", "Haya ni malengo ya ufuatiliaji, si tamko la moja kwa moja wala mbadala wa mwongozo wa kitaifa wa ugonjwa husika. Tarehe zisizopo huonyeshwa kama hazijarekodiwa."))
            st.dataframe(pd.DataFrame(_seven_one_seven(event)), use_container_width=True, hide_index=True)

            st.markdown("#### " + tr("Response tasks", "Kazi za kukabiliana"))
            tasks = event.setdefault("tasks", [])
            if tasks:
                task_rows = [{k: t.get(k) for k in ("task_id", "task", "owner", "due_at", "status", "created_at", "completed_at")} for t in tasks]
                st.dataframe(pd.DataFrame(task_rows), use_container_width=True, hide_index=True)
                open_tasks = [t for t in tasks if t["status"] == "Open"]
                if open_tasks:
                    task_id = st.selectbox(tr("Mark task complete", "Weka kazi kuwa imekamilika"), [t["task_id"] for t in open_tasks], key=f"erm_task_pick_{selected_id}")
                    if st.button(tr("Mark complete", "Weka kuwa imekamilika"), key=f"erm_task_done_{selected_id}"):
                        task = next(t for t in tasks if t["task_id"] == task_id)
                        task["status"], task["completed_at"] = "Complete", _now()
                        _audit(selected_id, "TASK_COMPLETED", f"{task_id}: {task['task']}")
                        st.rerun()
            else:
                st.caption(tr("No tasks yet.", "Bado hakuna kazi."))
            with st.form(f"erm_task_add_{selected_id}"):
                task_text = st.text_input(tr("New action / task", "Hatua / kazi mpya"))
                task_owner = st.text_input(tr("Responsible role", "Jukumu linalowajibika"), value="District response team (simulation)")
                task_due = st.date_input(tr("Due date", "Tarehe ya mwisho"), value=dt.date.today() + dt.timedelta(days=1))
                add_task = st.form_submit_button(tr("Add response task", "Ongeza kazi ya kukabiliana"))
            if add_task:
                if not task_text.strip():
                    st.error(tr("Enter a task description.", "Weka maelezo ya kazi."))
                else:
                    task_id = f"{selected_id}-T{len(tasks)+1}"
                    task = {"task_id": task_id, "task": task_text.strip(), "owner": task_owner.strip(),
                            "due_at": task_due.isoformat(), "status": "Open", "created_at": _now(), "completed_at": None}
                    tasks.append(task)
                    _audit(selected_id, "TASK_CREATED", f"{task_id}: {task['task']}; owner={task['owner']}; due={task['due_at']}")
                    st.rerun()

    with tab_report:
        st.subheader(tr("Register a synthetic test signal", "Sajili ishara ya majaribio"))
        st.caption(tr("Use fictional examples only. Do not submit real alerts through this demo.", "Tumia mifano ya kubuni pekee. Usitume tahadhari halisi kupitia mfumo huu wa majaribio."))
        with st.form("erm_new_event_form", clear_on_submit=True):
            title = st.text_input(tr("Short event title", "Kichwa kifupi cha tukio"))
            signal_type = st.selectbox(tr("Signal type", "Aina ya ishara"), SIGNAL_TYPES)
            event_region = st.text_input(tr("Region", "Mkoa"), value=region if region and region != "National Overview" else "")
            district = st.text_input(tr("District / council (fictional or non-identifying)", "Wilaya / halmashauri (ya kubuni au isiyotambulisha mtu)"))
            location_detail = st.text_input(tr("General location only; no household address", "Eneo la jumla tu; usiweke anwani ya kaya"))
            source_type = st.selectbox(tr("Source category", "Aina ya chanzo"), ["Community report (simulated)", "Health facility report (simulated)", "Laboratory signal (simulated)", "Media / hotline (simulated)", "Environmental / animal signal (simulated)", "Other (simulated)"])
            description = st.text_area(tr("What was observed? Do not include personal data.", "Nini kilichoonekana? Usiweke taarifa binafsi."))
            priority = st.selectbox(tr("Initial priority (human review required)", "Kipaumbele cha awali (ukaguzi wa binadamu unahitajika)"), PRIORITIES, index=1)
            assigned_to = st.text_input(tr("Assigned role / reviewer label", "Jukumu / lebo ya mkaguzi"), value="Unassigned")
            onset_known = st.checkbox(tr("Approximate onset date known", "Tarehe ya kuanza inajulikana"), value=False)
            onset_date = st.date_input(tr("Approximate onset date", "Tarehe ya takriban kuanza"), value=dt.date.today(), disabled=not onset_known)
            detected_date = st.date_input(tr("Detection date", "Tarehe ya kugundua"), value=dt.date.today())
            detected_time = st.time_input(tr("Detection time", "Muda wa kugundua"), value=dt.datetime.now().replace(second=0, microsecond=0).time())
            submitted = st.form_submit_button(tr("Register simulated event", "Sajili tukio la majaribio"))
        if submitted:
            if not title.strip() or not event_region.strip() or not description.strip():
                st.error(tr("Title, region and description are required.", "Kichwa, mkoa na maelezo vinahitajika."))
            else:
                stamp = dt.datetime.combine(detected_date, detected_time).astimezone().replace(microsecond=0).isoformat()
                serial = len(events) + 1
                event_id = f"SIM-{dt.datetime.now().strftime('%Y%m%d')}-{serial:03d}"
                event = {
                    "event_id": event_id, "title": title.strip(), "signal_type": signal_type,
                    "region": event_region.strip(), "district": district.strip() or "Not recorded",
                    "location_detail": location_detail.strip() or "Not recorded",
                    "description": description.strip(), "source_type": source_type, "priority": priority,
                    "status": "reported", "reported_at": _now(),
                    "onset_at": dt.datetime.combine(onset_date, dt.time(12, 0)).astimezone().replace(microsecond=0).isoformat() if onset_known else None,
                    "detected_at": stamp,
                    "notified_at": None, "response_started_at": None, "verified_at": None,
                    "closed_at": None, "assigned_to": assigned_to.strip(), "verification_note": "",
                    "simulation": True, "tasks": [],
                }
                events.append(event)
                _audit(event_id, "EVENT_CREATED", f"Synthetic event registered; type={signal_type}; source={source_type}; priority={priority}")
                st.success(tr(f"Simulation event {event_id} registered.", f"Tukio la majaribio {event_id} limesajiliwa."))
                st.rerun()

    with tab_audit:
        st.subheader(tr("Append-only audit log for this session", "Kumbukumbu ya ukaguzi inayoongezwa tu katika kikao hiki"))
        st.caption(tr("Logs record who/what action, event ID, timestamp and a short change description. This is not tamper-proof or durable storage.", "Kumbukumbu huhifadhi mhusika/hatua, namba ya tukio, muda na maelezo mafupi ya mabadiliko. Hii si hifadhi isiyoweza kubadilishwa wala ya kudumu."))
        audit_df = pd.DataFrame(audit)
        if not audit_df.empty:
            st.dataframe(audit_df.iloc[::-1], use_container_width=True, hide_index=True)
            st.download_button(tr("Download audit log CSV", "Pakua kumbukumbu ya ukaguzi CSV"),
                               audit_df.to_csv(index=False).encode("utf-8"), file_name="ecohealth_simulation_audit.csv",
                               mime="text/csv", key="erm_audit_download")
        event_df = pd.DataFrame([{**e, "tasks": str(e.get("tasks", []))} for e in events])
        if not event_df.empty:
            st.download_button(tr("Download event register CSV", "Pakua orodha ya matukio CSV"),
                               event_df.to_csv(index=False).encode("utf-8"), file_name="ecohealth_simulation_events.csv",
                               mime="text/csv", key="erm_events_download")
