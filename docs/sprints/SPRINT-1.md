# Sprint 1 — Discovery and project baseline

## Sprint goal

Understand the inherited state of Arkane Zone and produce a reliable functional, technical and architectural baseline before starting substantial implementation work.

- **Sprint start:** 2 November 2026
- **Sprint end:** 16 November 2026
- **First progress review:** Tuesday, 3 November 2026
- **Repository:** https://github.com/Cristianco9/arcakane-zone

## Working agreement

This sprint prioritizes discovery, controlled execution, documentation and backlog refinement. Avoid large feature development until the team understands the existing behavior and has documented the current state.

Every finding must be classified as one of:
- **Verified:** supported by code, configuration, tests or a reproducible execution.
- **Hypothesis:** suspected behavior that still needs reproduction or confirmation.
- **Proposal:** a suggested future change, not a description of the current system.

Do not expose credentials or production data in commits, screenshots or documentation.

## Team responsibilities

| Team member | Primary responsibility |
|---|---|
| Cristian Camilo (@Cristianco9) | Technical audit, architecture, environment/deployment review and sprint coordination |
| Luisa María (@luisanorena25) | Functional inventory, user journeys, use cases and acceptance criteria |
| Katherine Arboleda (@kathe005) | Domain model, entity relationships and UML diagrams |
| Whole team | Review findings, validate assumptions, reproduce defects and refine the next backlog |

Responsibilities are starting ownership, not a restriction on collaboration.

## Sprint backlog

### AZ-S1-01 — Business context, actors and scope
**Owner:** Cristian Camilo  
**Priority:** P0

Activities:
- Describe the problem the store solves and its value proposition.
- Identify actors and roles evidenced by the implementation.
- Define the current functional scope and non-goals.
- Extract business rules from models, forms, views and services.
- Record questions for the original author / professor.

Deliverables:
- Business context and system objective.
- Actor descriptions and responsibilities.
- Initial scope, assumptions and glossary.

Acceptance criteria:
- Every current-state statement is traceable to source code or explicitly marked as an assumption.
- Current functionality is separated from future proposals.
- Open questions are recorded.

### AZ-S1-02 — Functional inventory and user journeys
**Owner:** Luisa María  
**Priority:** P0

Activities:
- Review the Django apps: accounts, catalog, orders, payments, reports and support.
- Map routes, views and templates to observable behavior.
- Describe registration/login, catalog search/filtering, cart, checkout, order history/cancellation and support flows.
- Classify features as implemented, partially implemented, unverified or missing.
- Draft use cases / user stories and preliminary acceptance criteria.

Deliverables:
- Module-to-functionality matrix with code references.
- User journey or use-case diagram.
- Initial user stories and open questions.

Acceptance criteria:
- The inventory is based on implementation, not only labels or help-page claims.
- Unverified behavior is clearly marked.
- Gaps between templates, views and business services are recorded.

### AZ-S1-03 — Domain analysis and UML
**Owner:** Katherine Arboleda  
**Priority:** P0

Activities:
- Inspect Django models and migrations for accounts, catalog, orders, payments and support.
- Identify entities, attributes, relationships, cardinalities and integrity constraints.
- Compare models with forms, views and services.
- Produce an initial ER diagram and UML class diagram.
- Record model inconsistencies and design decisions requiring validation.

Deliverables:
- Entity and relationship inventory.
- ER diagram.
- UML class diagram.
- Questions and risks about the current data model.

Acceptance criteria:
- Diagrams describe the existing schema, not an idealized replacement.
- Relationships and cardinalities are supported by model definitions / migrations.
- Proposed changes are visually or textually distinguished from current state.

### AZ-S1-04 — Architecture, configuration and deployment audit
**Owner:** Cristian Camilo  
**Priority:** P0

Activities:
- Review the project layout, installed apps, dependencies and responsibility boundaries.
- Inspect Django settings, environment variables, PostgreSQL configuration, static/media storage and authentication configuration.
- Review `build.sh` and `render.yaml`.
- Attempt a local setup, database migration and seed execution in a controlled environment.
- Record blockers and reproducible steps.
- Check for Docker configuration, GitHub Actions and code-quality automation.

Deliverables:
- Current architecture / component diagram.
- Verified local setup notes.
- Dependency and environment-variable inventory (no secrets).
- Technical risk register.

Acceptance criteria:
- Declared configuration is distinguished from configuration actually tested.
- Failed steps include error messages and evidence.
- No infrastructure changes are made without team review.

### AZ-S1-05 — Test baseline and defect discovery
**Owners:** Luisa María and Katherine Arboleda  
**Priority:** P1

Activities:
- Inventory existing automated tests and test dependencies.
- Run the test suite if environment setup permits.
- Map tested and untested user journeys.
- Review authorization, cart, order, inventory and payment rules.
- Reproduce or disprove the payment retry concern: the help page says a rejected payment can be retried, but `Pago.pedido` is a OneToOne relation and the service creates a new payment on every attempt.
- Record reproduction steps, expected/actual result, severity and evidence.

Deliverables:
- Test execution report and setup blockers.
- Coverage-by-flow matrix.
- Reproducible defect / risk register.
- Recommended additional test cases.

Acceptance criteria:
- Suspected defects are reproduced or explicitly left as hypotheses.
- This task does not include feature fixes.
- Empty/placeholder tests and missing test dependencies are identified.

### AZ-S1-06 — Documentation and next-sprint backlog
**Owners:** Whole team  
**Priority:** P0

Activities:
- Consolidate business context, scope, functional inventory, diagrams and architecture.
- Separate existing capabilities, defects, technical debt and new feature proposals.
- Prioritize next actions by value, risk and dependency.
- Draft the next sprint's epics/stories and acceptance criteria.
- Prepare a short progress presentation for the professor.

Deliverables:
- Initial documentation set.
- Updated README with verified setup steps.
- Prioritized next-sprint backlog.
- Progress summary for the 3 November review.

Acceptance criteria:
- Documentation is consistent and links the diagrams / inventories.
- Current state and proposed future state are clearly separated.
- Every high-priority backlog item has a rationale and acceptance criteria.

## Tuesday review — 3 November 2026

The team should be able to show:
1. A concise explanation of what Arkane Zone is and who uses it.
2. A module/functionality inventory with evidence from the repository.
3. An initial ER/UML draft.
4. The current technology stack and deployment approach.
5. At least the first confirmed defects, risks or verification blockers.
6. The agreed two-week sprint objective, responsibilities and next steps.

The Tuesday review is an early checkpoint, not the sprint completion review.

## Definition of Done for Sprint 1

- Findings have been peer-reviewed by at least one other team member.
- Diagrams and matrices reflect the current implementation.
- Issues are reproducible or marked as hypotheses.
- Documentation is committed to the repository.
- The next sprint backlog is prioritized and ready for planning.
