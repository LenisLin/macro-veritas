# CLI Command Contracts

## Purpose

This document freezes the first internal command-family contracts for
MacroVeritas.

- It defines the reserved internal command families for the next phase.
- It defines the expected owner, purpose, inputs, outputs, and dependency
  boundary of each family.
- It defines the shared internal command style used by the skeleton modules in
  `macro_veritas.commands`.
- Concrete gateway-facing payload families are frozen separately in
  [`docs/payload_contracts.md`](payload_contracts.md).

This document now describes a mixed internal implementation state.

- It does not mean these commands are public yet.
- It does not imply broad file IO, serializer behavior, or public CLI
  execution.
- It does not imply implemented flags, options, or handler logic.
- One narrow exception now exists: internal `StudyCard` ingest execution is
  implemented behind the reserved `ingest` family.

## Command Families

### `ingest`

- Owning module: `macro_veritas.commands.ingest`
- Owning domain: Registry Department / 户部, intake boundary
- Purpose: execute the first internal `StudyCard` ingest bridge while keeping
  `DatasetCard` and `ClaimCard` ingest non-runtime
- Payload contract source: [`docs/payload_contracts.md`](payload_contracts.md)
- MVP payload families touched: `StudyCardPayload`, `DatasetCardPayload`,
  `ClaimCardPayload`
- Expected primary inputs: internal StudyCard ingest input, target card-family
  label, full-card StudyCard payload prepared from normalized intake input, and
  provenance note
- Expected primary outputs: StudyCard gateway create-plan request, StudyCard
  gateway create execution, and an internal command result mapping
- Expected dependency boundary: registry governance intake descriptors,
  card-contract docs, payload-contract docs, the StudyCard ingest bridge doc,
  and registry gateway create-planning/create contracts
- Runtime status now: internal `StudyCard` path is implemented through
  `plan_create_study_card(...)` followed by `create_study_card(...)`
- Still deferred inside `ingest`: public CLI exposure, DatasetCard ingest
  runtime, ClaimCard ingest runtime, and public flag design
- Non-goals in this milestone: no public CLI registration, no DatasetCard or
  ClaimCard ingest execution, no scientific logic, no evidence grading

### `bind`

- Owning module: `macro_veritas.commands.bind`
- Owning domain: Registry Department / 户部, locator-binding boundary
- Purpose: stage the association of governed objects with raw, processed, or
  artifact-facing locators
- Payload contract source: [`docs/payload_contracts.md`](payload_contracts.md)
- MVP payload families touched: `StudyCardPayload`, `DatasetCardPayload`,
  `ClaimCardPayload`
- Expected primary inputs: target object identity, locator reference, binding
  provenance note, full replacement payload when an update plan is needed
- Expected primary outputs: future gateway read/update-plan request and a
  binding summary
- Expected dependency boundary: registry governance binding descriptors,
  registry layout naming conventions, payload-contract docs, registry gateway
  read and update-planning contracts
- Non-goals in this milestone: no filesystem checks, no path mutation, no
  gateway execution, no storage probing

### `extract`

- Owning module: `macro_veritas.commands.extract`
- Owning domain: Registry Department / 户部, extraction-planning boundary
- Purpose: stage claim or metadata capture tasks against curated sources
- Payload contract source: [`docs/payload_contracts.md`](payload_contracts.md)
- MVP payload families touched: `ClaimCardPayload` for create/update and
  `StudyCardPayload` / `DatasetCardPayload` for update follow-up
- Expected primary inputs: curated source reference, extraction scope note,
  linked study or dataset context, full-card payload for a future create/update
  plan
- Expected primary outputs: future gateway read/create/update-plan request and
  an extraction-task summary
- Expected dependency boundary: registry governance extraction-planning
  descriptors, card contracts, payload-contract docs, registry gateway read and
  mutation-plan
  contracts
- Non-goals in this milestone: no text parsing, no metadata extraction engine,
  no gateway execution, no scientific interpretation

### `audit`

- Owning module: `macro_veritas.commands.audit`
- Owning domain: Review Department / 刑部, routine audit lane
- Purpose: stage routine audit checks and routine audit outcome recording around
  reviewable objects
- Payload contract source: [`docs/payload_contracts.md`](payload_contracts.md)
- MVP payload families touched: consume `StudyCard` / `DatasetCard` /
  `ClaimCard` read and list DTOs; no first-slice mutation payload preparation
- Expected primary inputs: object or bundle reference, audit scope note,
  findings summary, intended audit outcome label
- Expected primary outputs: audit action summary and future audit-record-facing
  planning request
- Expected dependency boundary: audit policy, review-governance descriptors, and
  payload-contract docs plus registry gateway read contracts for audited cards
- Non-goals in this milestone: no audit engine, no adjudication runtime, no
  evidence grading, no public CLI exposure

### `review`

- Owning module: `macro_veritas.commands.review`
- Owning domain: Prosecution / 检察院, escalated review lane
- Purpose: stage escalated review / prosecution intake after routine audit
  escalation
- Payload contract source: [`docs/payload_contracts.md`](payload_contracts.md)
- MVP payload families touched: consume `StudyCard` / `DatasetCard` /
  `ClaimCard` read DTOs; no first-slice mutation payload preparation
- Expected primary inputs: escalation packet, linked audit reference, dispute
  summary, response-context note
- Expected primary outputs: case-intake summary and prosecution handoff note
- Expected dependency boundary: prosecution lane descriptors, audit escalation
  policy, payload-contract docs, and registry gateway read contracts for linked
  cards
- Non-goals in this milestone: no case management, no sanctions, no workflow
  engine, no public CLI exposure

### `run`

- Owning module: `macro_veritas.commands.run`
- Owning domain: Operations Department / 兵部, run/bundle boundary
- Purpose: stage future run or bundle commands around declared inputs, methods,
  and outputs
- Payload contract source: [`docs/payload_contracts.md`](payload_contracts.md)
- MVP payload families touched: consume `StudyCard` / `DatasetCard` /
  `ClaimCard` read DTOs; no first-slice mutation payload preparation
- Expected primary inputs: method or bundle reference, linked input object
  references, run intent note
- Expected primary outputs: run-scope summary and future bundle-planning request
- Expected dependency boundary: operations governance descriptors, run-domain
  docs, payload-contract docs, and registry gateway read contracts for linked
  input cards
- Non-goals in this milestone: no scientific execution, no bundle generation,
  no orchestration runtime, no CellVoyager integration

### `grade`

- Owning module: `macro_veritas.commands.grade`
- Owning domain: Review-adjacent grading boundary, provisionally aligned with
  Review Department / 刑部
- Purpose: stage a future evidence-judgment or claim-grading command family
  without locking grading runtime behavior
- Payload contract source: [`docs/payload_contracts.md`](payload_contracts.md)
- MVP payload families touched: consume `ClaimCard` plus linked
  `DatasetCard` / `StudyCard` read DTOs; no first-slice mutation payload
  preparation
- Expected primary inputs: claim reference, linked dataset or bundle context,
  judgment intent note
- Expected primary outputs: grading summary and future evidence-judgment request
- Expected dependency boundary: review governance, gateway read contracts for
  linked cards, payload-contract docs, and later evidence-layer contracts that
  remain deferred
- Non-goals in this milestone: no evidence grading logic, no scoring engine, no
  report assembly runtime, no public CLI exposure

## Command Style

The frozen internal command style is conservative:

- one module per reserved command family under `macro_veritas.commands`
- one `build_parser(subparsers_or_parser: object) -> None` hook per family
- one `handle_<family>_command(args: object) -> object` hook per family
- static descriptor helpers for family metadata and dependency declarations
- static payload-touchpoint descriptors that point to
  [`docs/payload_contracts.md`](payload_contracts.md)
- runtime execution exists only for the internal StudyCard ingest bridge;
  other command families remain descriptor/skeleton-only
- file IO is allowed only through the registry gateway for explicitly
  documented internal runtime paths
- no silent side effects

Interpretation:

- `build_parser(...)` is an internal skeleton hook only.
- `handle_ingest_command(...)` now has a narrow internal StudyCard runtime path.
- Other `handle_<family>_command(...)` functions remain internal placeholders.
- Raw `argparse` objects remain outside the gateway contract and must be
  normalized before payload preparation.
- Option and flag design remains deferred.
- No family gets a deep subpackage tree in this milestone.

## Public Exposure Rule

These command families are reserved and skeletonized, but they are not yet part
of the stable public CLI surface.

- `python -m macro_veritas status` remains public.
- `python -m macro_veritas show-config` remains public.
- `python -m macro_veritas init-layout` remains public.
- The reserved internal command families must not change current help text or
  public CLI behavior in this milestone.
