"""Streamlit interface for policy deliberation."""
import json
import streamlit as st
from policy_deliberation import Scenario, retrieve_evidence, build_deliberation

def render_policy_deliberation(pack, region, data, lang="en"):
    st.header("⚖️ " + ("Majadiliano ya Sera kwa Wakala Wengi" if lang == "sw" else "Multi-Agent Policy Deliberation"))
    st.caption("Mitazamo ya mfano; si mashauriano ya jamii wala maamuzi ya kliniki." if lang == "sw" else
               "Simulated analytical perspectives; not community consultation or clinical decision-making.")
    with st.form("policy_deliberation_form"):
        question = st.text_area("Swali la sera / Policy question",
            value="How should the district prioritise cholera prevention and response?", max_chars=2000)
        geography = st.text_input("Geography / Eneo", value=region)
        horizon = st.text_input("Time horizon / Muda", value="Next 30 days")
        constraints = st.text_area("Constraints / Vikwazo", placeholder="Budget, workforce, connectivity...")
        submitted = st.form_submit_button("Run deliberation / Anzisha uchambuzi", use_container_width=True)
    if not submitted:
        st.info("Enter a policy question and run the deliberation. No data is sent to an external model.")
        return
    if len(question.strip()) < 10:
        st.error("Please provide a more specific policy question.")
        return
    indicators = {k: v for k, v in (data or {}).items() if isinstance(v, (int, float))}
    status = "placeholder" if (pack or {}).get("data_status") == "placeholder" or not pack else "verify_source_status"
    scenario = Scenario(question=question.strip(), geography=geography.strip() or region,
        time_horizon=horizon.strip() or "Not specified",
        constraints=[x.strip() for x in constraints.splitlines() if x.strip()],
        indicators=indicators, data_status=status)
    index = None
    if pack:
        try:
            from rag import get_index
            index = get_index(pack["code"])
        except Exception:
            index = None
    with st.spinner("Retrieving policy evidence and preparing perspectives..."):
        evidence = retrieve_evidence(question, index=index, k=5)
        report = build_deliberation(scenario, evidence)
    st.warning("Prototype output. Verify sources and local data. Human review is mandatory.")
    st.subheader("Scenario")
    st.write(report.scenario.question)
    st.caption(f"{report.scenario.geography} · {report.scenario.time_horizon} · {len(evidence)} retrieved passages")
    st.subheader("Stakeholder perspectives")
    for argument in report.arguments:
        with st.expander(argument.perspective):
            st.write(argument.position)
            st.write(argument.rationale)
            st.markdown("**Objections**")
            for item in argument.objections: st.write("- " + item)
            st.markdown("**Uncertainties and evidence gaps**")
            for item in argument.uncertainties + argument.evidence_gaps: st.write("- " + item)
    st.subheader("Unresolved disagreements")
    for item in report.unresolved_disagreements: st.warning(item)
    st.subheader("Retrieved evidence")
    if evidence:
        for item in evidence:
            with st.expander(f"{item.source} · {item.evidence_id}"):
                st.write(item.excerpt)
                st.caption(f"Page: {item.page or 'not available'} · {item.verification_status}")
    else:
        st.info("No relevant passages retrieved. The report is not evidence-backed.")
    st.subheader("Safeguards and limitations")
    for item in report.safeguards + report.limitations: st.write("- " + item)
    st.download_button("Download deliberation record (JSON)",
        data=json.dumps(report.model_dump(), ensure_ascii=False, indent=2),
        file_name="ecohealth_policy_deliberation.json", mime="application/json", use_container_width=True)
