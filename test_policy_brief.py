from policy_brief import build_policy_brief


def _fields(**overrides):
    values = {
        "title": "Improving immunisation coverage",
        "geography": "Moshi, Tanzania",
        "audience": "District health management team",
        "author": "Research team",
        "key_messages": "1. Coverage gap requires review.",
        "summary": "A concise summary.",
        "problem": "Problem statement.",
        "evidence": "Source: verified report, 2025; unit: percent.",
        "options": "Status quo; outreach; integrated outreach.",
        "recommendations": "District team to review microplans within 90 days.",
        "implementation": "Named district unit; phased delivery.",
        "monitoring": "Indicator, baseline, target, source, monthly frequency.",
        "equity": "Include remote communities and persons with disabilities.",
        "limitations": "Subnational data are incomplete.",
        "references": "Publisher. Report title. 2025. https://example.org",
    }
    values.update(overrides)
    return values


def test_policy_brief_contains_core_decision_sections():
    brief = build_policy_brief(_fields())
    for heading in (
        "# Improving immunisation coverage",
        "## Key messages",
        "## Executive summary",
        "## Policy problem and context",
        "## Evidence and key findings",
        "## Policy options and trade-offs",
        "## Recommended actions",
        "## Implementation and accountability",
        "## Monitoring, evaluation and learning",
        "## Equity, rights and safeguards",
        "## Limitations and evidence gaps",
        "## References and data sources",
        "## Review and sign-off",
    ):
        assert heading in brief


def test_missing_sections_are_not_fabricated():
    brief = build_policy_brief(_fields(evidence="", recommendations=""))
    assert "Not provided. Complete this section" in brief
    assert "_Not provided._" in brief or "_Not provided. Complete this section before external circulation._" in brief


def test_draft_and_evidence_warning_are_present():
    brief = build_policy_brief(_fields())
    assert "DRAFT FOR REVIEW" in brief
    assert "traceable source" in brief
