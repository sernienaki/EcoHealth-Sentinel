# UN data source registry and connector architecture

## Purpose
The registry is a discovery and governance layer. Documenting a portal does not mean an API connector exists.

## Connector contract
- Use independent modules and official HTTPS base URLs.
- Use bounded timeouts, explicit error types and read-only access unless separately approved.
- Validate identifiers before constructing request paths.
- Preserve publisher identifiers, geography, time, dimensions, unit, source, footnotes and provenance.
- Handle unavailable services, empty results and schema changes.
- Never silently harmonise or aggregate records.
- Include mocked tests and separate live verification.
- Expose source terms, retrieval date and metadata to users.

## Current state
| Source | State | Notes |
|---|---|---|
| UN System Data Commons | Existing | Custom REST V2 integration; facets retained |
| UNSD SDG API | Implemented in PR #24 | Read-only GET connector; M49 geography |
| WHO GHO | Discovery only | Verify API contract and terms |
| UNICEF Data | Discovery only | Verify official access route and metadata |
| WHO/UNICEF JMP | Discovery only | Verify download/API format and service-ladder definitions |
| UN WPP | Discovery only | Verify token and versioned API contract |
| UNdata | Discovery only | Separate SDMX interface |

Official SDG API docs: https://unstats.un.org/sdgapi/swagger/
Tanzania M49 code: 834.

## Status vocabulary
- implemented_existing: connector present before this PR.
- implemented_pr24: connector added in this PR.
- discovery_only: official portal documented, but no app connector.

Do not change a source to implemented until code, tests, metadata mapping and error handling are present.