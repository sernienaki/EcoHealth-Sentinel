# Plain-language data understanding and bilingual glossary

## User experience goal
A person should not need training in statistics, SDMX, DCIDs or UN data systems to understand a basic indicator. Technical metadata remains available, but the first explanation uses everyday language.

## Recommended explanation card
1. What is this? Official indicator name.
2. In simple words: one or two short sentences.
3. Example: a small hypothetical example clearly labelled illustrative.
4. Why does it matter? Practical relevance.
5. What does the number not tell us? Limitations, denominator and context.
6. Where and when? Geography and reference period.
7. Who produced it? Publisher, source link and retrieval date.
8. Technical details: definition, unit, method, disaggregation and source identifiers.

## Translation principles
- Use familiar Kiswahili, not literal translations of statistical jargon.
- Keep official indicator names and acronyms available in technical details.
- Explain acronyms at first use.
- Have translations reviewed by a fluent Kiswahili public-health/data reviewer before production use.
- Do not change denominator, population, period or measurement concept during translation.

## Glossary starter content
indicator_glossary.py includes bilingual educational explanations for malaria incidence, maternal mortality ratio, under-five mortality, immunisation coverage, basic drinking-water service, sanitation service level, poverty headcount and health-worker density.

These are generic teaching explanations. They do not claim that a matching indicator or data series exists in connected sources. Source-specific definitions take precedence.

## Plain-language quality checks
A non-specialist reviewer should be able to identify the population counted, numerator, denominator, unit, year/period, geography, publisher and at least one limitation. If metadata do not support an answer, the interface must say so.