"""International-standard policy brief builder for EcoHealth Sentinel.

The generator structures user-reviewed content; it does not infer policy findings
or turn demonstration values into evidence.
"""
from datetime import date
import html
import streamlit as st


def _section(title, body):
    body = (body or "").strip()
    return f"## {title}\n\n{body if body else '_Not provided. Complete this section before external circulation._'}"


def build_policy_brief(fields):
    title = fields["title"].strip() or "Public health policy brief"
    sections = [
        f"# {title}",
        f"**Geography:** {fields['geography']}  ",
        f"**Intended decision-maker:** {fields['audience']}  ",
        f"**Prepared on:** {date.today().isoformat()}  ",
        f"**Prepared by:** {fields['author'] or 'Not specified'}",
        "> DRAFT FOR REVIEW. This brief requires source verification, technical review and approval before circulation.",
        "## Key messages",
        fields["key_messages"] or "_Not provided._",
        _section("Executive summary", fields["summary"]),
        _section("Policy problem and context", fields["problem"]),
        _section("Evidence and key findings", fields["evidence"]),
        _section("Policy options and trade-offs", fields["options"]),
        _section("Recommended actions", fields["recommendations"]),
        _section("Implementation and accountability", fields["implementation"]),
        _section("Monitoring, evaluation and learning", fields["monitoring"]),
        _section("Equity, rights and safeguards", fields["equity"]),
        _section("Limitations and evidence gaps", fields["limitations"]),
        _section("References and data sources", fields["references"]),
        "## Review and sign-off",
        "- Technical review: Not recorded",
        "- Policy/legal review: Not recorded",
        "- Approval authority: Not recorded",
        "- Version: Draft 1.0",
        "",
        "**Evidence rule:** Do not circulate until every quantitative claim has a traceable source, reference period, geography, unit, method and retrieval date. Label illustrative or synthetic values explicitly.",
    ]
    return "\n\n".join(sections)


def render_policy_brief_tab(lang, region, country, role_label, data=None):
    sw = lang == "sw"
    st.header("Kizalishaji cha Muhtasari wa Sera" if sw else "International-standard Policy Brief Builder")
    st.caption(
        "Muundo wa rasimu; hakiki ushahidi na vyanzo kabla ya kusambaza." if sw else
        "Structured drafting tool for decision-makers. A template does not certify evidence quality or policy approval."
    )
    st.info(
        "Takwimu za dashibodi zinaweza kuwa za mfano. Usizitumie kama ushahidi uliothibitishwa." if sw else
        "Dashboard figures in this prototype may be illustrative. They are not inserted as verified findings. Add only evidence you have checked."
    )
    with st.expander("How to use this brief / Jinsi ya kutumia", expanded=True):
        st.markdown(
            "1. Define one specific policy decision.\n"
            "2. Identify the decision-maker and geographic level.\n"
            "3. Add evidence with source, year, unit and limitations.\n"
            "4. Compare feasible options and explain trade-offs.\n"
            "5. Make actionable recommendations with owners and timelines.\n"
            "6. Review, validate and approve before sharing."
        )
    with st.form("international_policy_brief_form"):
        st.subheader("1. Brief identity")
        brief_title = st.text_input("Title", placeholder="A specific, action-oriented policy title")
        c1, c2 = st.columns(2)
        geography = c1.text_input("Geographic scope", value=f"{region}, {country}")
        audience = c2.text_input("Primary decision-maker / audience", value=role_label)
        author = st.text_input("Authoring team / institution (optional)")
        st.subheader("2. Decision summary")
        key_messages = st.text_area("Key messages (3–5 concise points)", height=110)
        summary = st.text_area("Executive summary: problem, evidence, proposed action and expected public value", height=150)
        st.subheader("3. Policy analysis")
        problem = st.text_area("Policy problem and context: who is affected, scale, urgency and policy gap", height=150)
        evidence = st.text_area("Evidence and key findings: include figures only with source, year, unit and geography", height=180)
        options = st.text_area("Policy options: include status quo, benefits, costs, feasibility, risks and trade-offs", height=150)
        recommendations = st.text_area("Recommended actions: specify what should change, who should act and by when", height=150)
        st.subheader("4. Delivery and accountability")
        implementation = st.text_area("Implementation: responsible institutions, confirmed partners, resources, sequencing and timeline", height=150)
        monitoring = st.text_area("Monitoring and evaluation: indicators, baseline, target, data source, frequency and accountable owner", height=150)
        equity = st.text_area("Equity, gender, disability, human rights, privacy and community safeguards", height=120)
        st.subheader("5. Evidence quality and references")
        limitations = st.text_area("Limitations, uncertainty, missing data and transferability", height=120)
        references = st.text_area("References: organisation/author, title, year, URL/DOI and access date; list each source separately", height=150)
        submitted = st.form_submit_button("Generate policy brief / Tengeneza muhtasari")
    if submitted:
        fields = {
            "title": brief_title, "geography": geography, "audience": audience, "author": author,
            "key_messages": key_messages, "summary": summary, "problem": problem, "evidence": evidence,
            "options": options, "recommendations": recommendations, "implementation": implementation,
            "monitoring": monitoring, "equity": equity, "limitations": limitations, "references": references,
        }
        brief = build_policy_brief(fields)
        st.session_state["eco_policy_brief_markdown"] = brief
        st.session_state["eco_policy_brief_html"] = (
            "<!doctype html><html><head><meta charset='utf-8'><title>Policy brief</title>"
            "<style>body{font-family:Arial,sans-serif;max-width:850px;margin:40px auto;line-height:1.55}"
            "h1,h2{color:#173b4a}blockquote{border-left:4px solid #35a98b;padding:8px 16px;background:#eef6f4}"
            "@media print{body{margin:15mm}}</style></head><body><pre style='white-space:pre-wrap;font:inherit'>"
            + html.escape(brief) + "</pre></body></html>"
        )
    brief = st.session_state.get("eco_policy_brief_markdown")
    if brief:
        st.subheader("Generated draft / Rasimu iliyotengenezwa")
        st.text_area("Preview", brief, height=520, key="eco_policy_brief_preview")
        st.download_button("Download Markdown", brief, file_name="ecohealth_policy_brief.md", mime="text/markdown")
        st.download_button("Download print-ready HTML", st.session_state["eco_policy_brief_html"],
                           file_name="ecohealth_policy_brief.html", mime="text/html")
        st.warning("Before circulation: verify every claim, add complete citations, obtain technical and policy review, and record approval. Missing fields are not evidence.")
