# StudyCard Ingest Runtime

## Purpose

This document is the source of truth for the first real StudyCard ingest
runtime path in MacroVeritas.

- It defines the narrow implemented runtime path now used by public
  `StudyCard` ingest.
- It fixes the boundary between command-facing input normalization and the
  frozen `StudyCardPayload` gateway contract.
- It fixes the boundary between command execution and the already-frozen
  registry gateway.
- It fixes the narrow command-layer success and failure reporting style for
  this milestone.

## Implemented Now

The following path is now real:

- `macro_veritas.cli` exposes `ingest study` as a thin public CLI adapter.
- The public CLI adapter converts parsed args into a small typed CLI mapping.
- `macro_veritas.commands.ingest.normalize_public_studycard_cli_input(...)`
  converts that typed CLI mapping into normalized StudyCard ingest input.

- `macro_veritas.commands.ingest.normalize_studycard_ingest_input(...)`
  normalizes command-facing StudyCard ingest values into a small internal
  mapping.
- `macro_veritas.commands.ingest.prepare_studycard_ingest_payload(...)`
  converts that normalized input into the frozen `StudyCardPayload`.
- `macro_veritas.commands.ingest.execute_studycard_ingest(...)` calls
  `plan_create_study_card(...)` and then `create_study_card(...)`.
- `macro_veritas.commands.ingest.handle_ingest_command(...)` accepts a
  mapping-based internal input and dispatches only the `StudyCard` runtime
  path.
- The actual write remains owned by `macro_veritas.registry.gateway`.

Public surface in this milestone:

- `python -m macro_veritas ingest study ...` is now public.
- `python -m macro_veritas status`, `show-config`, and `init-layout` remain
  public and unchanged.
- No other `ingest` path is public.

## Still Skeleton-Only

The following remain deferred and non-runtime:

- `DatasetCard` ingest command execution
- `ClaimCard` ingest command execution
- `bind`, `extract`, `audit`, `review`, `run`, and `grade` runtime execution
- `StudyCard` update or patch ingest semantics
- any public `DatasetCard` or `ClaimCard` ingest exposure

## Command-To-Payload Normalization Boundary

The StudyCard ingest bridge currently consumes a small command-facing input
shape:

- required: `study_id`, `citation_handle`, `tumor_type`, `therapy_scope`,
  `relevance_scope`, `screening_decision`, `status`, `created_from`
- optional: `screening_note`, `source_artifact`

Normalization rules:

- `tumor_type`, `therapy_scope`, and `relevance_scope` may be passed as one
  string or a sequence of strings.
- The normalized internal input stores these as plural command-side fields:
  `tumor_types`, `therapy_scopes`, and `relevance_scopes`.
- Payload preparation then maps those values onto the frozen gateway payload
  keys:
  `tumor_scope_tags`, `therapy_scope_tags`, `relevance_scope_tags`,
  `created_from_note`, and `source_artifact_locator`.

No raw `argparse.Namespace` object is part of this boundary.

## Command-To-Gateway Call Boundary

The StudyCard ingest execution order is fixed as:

1. parse explicit CLI flags
2. adapt those flags into a typed StudyCard CLI mapping
3. normalize command-facing StudyCard ingest input
4. prepare one full-card `StudyCardPayload`
5. call `plan_create_study_card(payload)`
6. call `create_study_card(payload)` if planning succeeds

Interpretation rules:

- The public CLI does not pass raw `argparse.Namespace` into command logic.
- The command layer does not write files directly.
- The command layer does not bypass the gateway.
- The command layer does not alter the gateway contract.
- The command layer does not implement DatasetCard or ClaimCard ingest runtime.

## Command Result Rule

The narrow internal command result style for this milestone is:

- success and failure are returned as one `CommandExecutionResult` mapping
- required keys: `ok`, `operation`, `card_family`, `target_id`, `message`
- failure-only key: `error_category`

The current error categories are:

- `duplicate_target`
- `invalid_payload`
- `unsupported_operation`
- `registry_failure`

Translation rule:

- duplicate create failures become `duplicate_target`
- malformed StudyCard data or malformed command input become `invalid_payload`
- unsupported ingest card families and unsafe canonical StudyCard identifiers
  become `unsupported_operation`
- other gateway/domain failures become `registry_failure`

The command layer must not expose raw filesystem exceptions as its intended
contract.

## Non-Goals

This milestone does not add or imply:

- DatasetCard ingest runtime
- ClaimCard ingest runtime
- DatasetCard or ClaimCard public ingest
- StudyCard update or patch ingest
- bind/extract/audit/review/run/grade runtime execution
- scientific logic
- evidence grading
- CellVoyager integration
- FastAPI
- SQL persistence
- notebook workflow
- plugin discovery
- orchestration runtime
