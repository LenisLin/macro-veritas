# Internal StudyCard Ingest Runtime

## Purpose

This document is the source of truth for the first internal command execution
bridge in MacroVeritas.

- It defines the narrow internal-only runtime path now implemented for
  `StudyCard` ingest.
- It fixes the boundary between command-facing input normalization and the
  frozen `StudyCardPayload` gateway contract.
- It fixes the boundary between command execution and the already-frozen
  registry gateway.
- It fixes the narrow command-layer success and failure reporting style for
  this milestone.

## Implemented Now

The following path is now real and internal:

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

This implementation is internal only.

- No new public CLI command is registered.
- `python -m macro_veritas --help` remains unchanged.
- `python -m macro_veritas status` and `python -m macro_veritas show-config`
  remain the public CLI surface relevant to this milestone.

## Still Skeleton-Only

The following remain deferred and non-runtime:

- `DatasetCard` ingest command execution
- `ClaimCard` ingest command execution
- `bind`, `extract`, `audit`, `review`, `run`, and `grade` runtime execution
- any public `ingest` CLI exposure

## Command-To-Payload Normalization Boundary

The internal StudyCard ingest bridge currently consumes a small command-facing
input shape:

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

The internal StudyCard ingest execution order is fixed as:

1. normalize command-facing StudyCard ingest input
2. prepare one full-card `StudyCardPayload`
3. call `plan_create_study_card(payload)`
4. call `create_study_card(payload)` if planning succeeds

Interpretation rules:

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

- public `ingest` CLI registration
- DatasetCard ingest runtime
- ClaimCard ingest runtime
- bind/extract/audit/review/run/grade runtime execution
- scientific logic
- evidence grading
- CellVoyager integration
- FastAPI
- SQL persistence
- notebook workflow
- plugin discovery
- orchestration runtime
