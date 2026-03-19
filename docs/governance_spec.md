# Governance Function Specification

## Purpose

This document freezes the governance-layer responsibilities and function-level intent for MacroVeritas at the current MVP boundary.

- It defines the documented role of the A-header, the six departments, and the distinct prosecution lane.
- It names the planned office structure and the intended descriptor interfaces that later rounds may build on.
- It does not imply implemented orchestration, enforcement, persistence, registry mutation, scientific execution, evidence grading, or CellVoyager integration.

This document is the function-level source of truth for the current governance freeze. It should be read together with [`docs/architecture.md`](architecture.md), [`docs/module_map.md`](module_map.md), and [`docs/api_specs.md`](api_specs.md).

## A-header

### Core Role

核心决策层 / A-header is the documented coordination layer for non-trivial modules, scripts, and future CLI families.

Its role is conservative:

- freeze why a unit of work exists
- freeze the intended input and output boundary
- freeze who owns review and escalation coverage

It is not a runtime controller, workflow engine, or policy executor.

### Functional Lanes

#### 定旨线 / Mandate Lane

- Purpose: freeze the work mandate, scope boundary, and explicit non-goals for a documented module, command family, or work packet.
- Planned core functions:
  - `define_work_mandate`
  - `declare_non_goals`
- Intended inputs: a proposed work unit name, linked governance references, and a concise scope statement.
- Intended outputs: a mandate header and an explicit non-goal statement.
- Deferred items: automatic header generation, orchestration hooks, policy enforcement.

#### 定约线 / Contract Lane

- Purpose: freeze declared inputs, outputs, and governed artifact references before runtime logic exists.
- Planned core functions:
  - `declare_input_contract`
  - `declare_output_contract`
  - `link_governed_artifacts`
- Intended inputs: documented input categories, output categories, object-family references, and future CLI-family references where relevant.
- Intended outputs: an interface-boundary descriptor and a documented artifact reference list.
- Deferred items: schema validation, runtime contract checking, dispatch wiring.

#### 定责线 / Oversight Lane

- Purpose: freeze ownership, review coverage, and escalation routing at the documentation level.
- Planned core functions:
  - `assign_governance_roles`
  - `declare_review_route`
- Intended inputs: role labels, review-lane requirements, escalation triggers, and linked department references.
- Intended outputs: a governance-coverage header and a declared review route.
- Deferred items: permissions, assignment automation, workflow routing.

## Six Departments

### 吏部 / Personnel Department

Role in the system: freeze human-role vocabulary and responsibility coverage headers for governed work. This department defines how ownership is described, not how people are authenticated or managed.

#### 角色簿司 / Role Catalog Office

- Purpose: keep a small stable vocabulary for project roles such as lead, curator, analyst, reviewer, and auditor.
- Planned core functions:
  - `define_role_profile`
  - `map_role_responsibilities`
- Intended inputs: a role label, a documentation context, and a concise responsibility note.
- Intended outputs: a role-profile descriptor and a role-to-responsibility map.
- Deferred items: directory services, staffing records, permissions.

#### 署任司 / Assignment Header Office

- Purpose: describe who is the working owner and who is the routine reviewer for a governed object or work packet.
- Planned core functions:
  - `assign_working_owner`
  - `assign_review_owner`
- Intended inputs: an artifact or task reference, role-profile references, and a stage or readiness note.
- Intended outputs: an ownership header and a review-coverage header.
- Deferred items: identity lookup, workload balancing, task routing.

#### 升核司 / Escalation Coverage Office

- Purpose: document who sponsors escalation and how uncovered ownership gaps are recorded.
- Planned core functions:
  - `declare_escalation_sponsor`
  - `record_coverage_gap`
- Intended inputs: an escalation context, current owner labels, and a gap note when coverage is incomplete.
- Intended outputs: an escalation-sponsor descriptor and a coverage-gap note.
- Deferred items: staffing workflow, notifications, organizational policy enforcement.

### 户部 / Registry Department

Role in the system: freeze the intake, binding, and extraction-planning interfaces for registry-facing objects. This department may later own registry IO, but no such behavior is implemented now.

#### 登籍司 / Intake Office

- Purpose: define how primary registry objects enter documented project scope.
- Planned core functions:
  - `register_study_intake`
  - `register_dataset_intake`
  - `register_claim_intake`
- Intended inputs: source references, provisional identifiers, provenance notes, and basic scope statements.
- Intended outputs: intake descriptors for `StudyCard`, `DatasetCard`, or `ClaimCard`.
- Deferred items: persistent identifiers, file writes, schema validation, object creation.

#### 定位司 / Locator Binding Office

- Purpose: define how registry objects will later be associated with concrete filesystem locations and artifact bundles.
- Planned core functions:
  - `bind_dataset_locator`
  - `bind_artifact_locator`
- Intended inputs: object identity, locator or path references, and binding provenance.
- Intended outputs: locator-binding descriptors that document the intended attachment.
- Deferred items: existence checks, path mutation, storage backends, registry updates.

#### 摘录司 / Extraction Planning Office

- Purpose: frame planned extraction and metadata-capture tasks without executing them.
- Planned core functions:
  - `propose_claim_extraction_task`
  - `propose_metadata_capture_task`
- Intended inputs: curated source references, target object-family labels, and extraction intent.
- Intended outputs: extraction-task descriptors and capture-scope notes.
- Deferred items: extraction logic, NLP, automated parsing, field-level schemas.

### 礼部 / Standards Department

Role in the system: freeze naming, boundary, and documentation-discipline standards so later code layers have a stable contract language.

#### 名制司 / Naming Office

- Purpose: keep object-family names, CLI-family names, and descriptor labels consistent across docs and code.
- Planned core functions:
  - `validate_object_naming`
  - `validate_cli_family_name`
- Intended inputs: candidate labels, naming context, and the relevant documentation reference.
- Intended outputs: a naming finding and, when valid, a normalized label note.
- Deferred items: automatic linting, code rewrites, mass rename tooling.

#### 界约司 / Contract Boundary Office

- Purpose: check that declared inputs, outputs, references, and non-goals are explicit enough for later implementation work.
- Planned core functions:
  - `validate_contract_boundary`
  - `declare_required_references`
- Intended inputs: a draft header, boundary claims, and linked governance documents.
- Intended outputs: a boundary-validation note and a required-reference note.
- Deferred items: parser-based validation, enforcement, service-level policy.

#### 例外司 / Exception Office

- Purpose: document controlled deviations and deferred rule coverage during the freeze.
- Planned core functions:
  - `record_standard_exception`
  - `summarize_deferred_rule`
- Intended inputs: a deviation statement, rationale, and compensating references.
- Intended outputs: an exception note and a deferred-rule summary.
- Deferred items: approvals workflow, waiver service, automatic exception tracking.

### 兵部 / Operations Department

Role in the system: freeze method and reanalysis-boundary descriptors so later execution layers can be added without changing the governance contract. This department does not execute science in the current milestone.

#### 方法司 / Method Scope Office

- Purpose: define the documented context for a `MethodCard` and its expected inputs.
- Planned core functions:
  - `declare_method_context`
  - `declare_method_inputs`
- Intended inputs: method labels, assumptions, and planned input-family references.
- Intended outputs: a method-context descriptor and an input-contract note.
- Deferred items: algorithm implementation, parameter validation, method execution.

#### 复核司 / Reanalysis Planning Office

- Purpose: frame reanalysis requests and bundle plans without running them.
- Planned core functions:
  - `plan_reanalysis_request`
  - `assemble_bundle_plan`
- Intended inputs: study, dataset, or claim references; method context; and requested deliverables.
- Intended outputs: a reanalysis-request descriptor and a planned `ReanalysisBundle` header.
- Deferred items: orchestration loops, job scheduling, notebook workflows, CellVoyager integration.

#### 清单司 / Artifact Manifest Office

- Purpose: describe expected run artifacts and declared outputs at the contract level.
- Planned core functions:
  - `describe_run_artifacts`
  - `describe_run_outputs`
- Intended inputs: run-stage labels, artifact categories, and output intent.
- Intended outputs: an artifact-manifest descriptor and an output-contract note.
- Deferred items: manifest generation, pipeline writing, runtime storage logic.

### 工部 / Infrastructure Department

Role in the system: freeze filesystem-layout, configuration-boundary, and runtime-surface descriptors that support the CLI-first scaffold.

#### 形制司 / Layout Contract Office

- Purpose: declare how storage areas and artifact-location families are described at the governance level.
- Planned core functions:
  - `declare_layout_contract`
  - `reserve_artifact_location_family`
- Intended inputs: layout segments, object or run context, and storage intent.
- Intended outputs: a layout-contract descriptor and a reserved-location note.
- Deferred items: storage allocation, directory mutation beyond the current scaffold CLI, backend management.

#### 配置司 / Config Boundary Office

- Purpose: distinguish committed config inputs from derived path or runtime values.
- Planned core functions:
  - `validate_config_boundary`
  - `describe_config_inputs`
- Intended inputs: config keys, derived-path references, and boundary questions.
- Intended outputs: a config-boundary note and a config-input descriptor.
- Deferred items: schema migration, environment management, secrets handling.

#### 运行界面司 / Runtime Surface Office

- Purpose: keep the allowed runtime surface conservative and explicit.
- Planned core functions:
  - `declare_runtime_surface`
  - `record_environment_constraint`
- Intended inputs: command-surface labels, environment assumptions, and linked constraint documents.
- Intended outputs: a runtime-surface note and a constraint record.
- Deferred items: deployment automation, service provisioning, orchestration runtime.

### 刑部 / Review Department

Role in the system: freeze the routine review and audit lane used for traceability, linkage, readiness, and escalation decisions. This department is distinct from prosecution and should remain the default lightweight review path.

#### 受核司 / Audit Intake Office

- Purpose: define the scope of a routine audit check at a high-value transition point.
- Planned core functions:
  - `propose_audit_check`
  - `confirm_audit_scope`
- Intended inputs: an object or bundle reference, a stage transition, and traceability concerns.
- Intended outputs: an audit-check descriptor and a scope-confirmation note.
- Deferred items: automatic trigger evaluation, review queue management.

#### 审记司 / Audit Record Office

- Purpose: define the documented pass and return outcomes of routine audit.
- Planned core functions:
  - `record_audit_pass`
  - `record_audit_return`
- Intended inputs: an audit-check descriptor, findings summary, and required follow-up notes.
- Intended outputs: an `AuditRecord` header and, when needed, a return note.
- Deferred items: evidence grading, scoring, adjudication engine.

#### 移送司 / Escalation Gate Office

- Purpose: hand off materially disputed or high-risk cases from routine review to prosecution without merging the two lanes.
- Planned core functions:
  - `escalate_review_case`
  - `assemble_escalation_packet`
- Intended inputs: an audit record reference, escalation rationale, and linked supporting context.
- Intended outputs: an escalation-packet descriptor and a prosecution handoff note.
- Deferred items: automated escalation, sanctions, case tracking.

## 检察院 / Prosecution

### Why It Is Distinct

Prosecution is not a stronger spelling of routine review. It is a separate governance lane for materially disputed, high-risk, or governance-sensitive cases that have already crossed the routine audit boundary.

Routine review asks whether an object or bundle is sufficiently documented for trusted downstream use.

Prosecution asks whether an escalated case needs structured case framing, response handling, and a documented disposition recommendation.

### Functional Lanes

#### 受案司 / Case Intake Lane

- Purpose: accept only escalated cases and screen whether the prosecution lane is warranted.
- Planned core functions:
  - `accept_escalated_case`
  - `screen_material_dispute`
- Intended inputs: an escalation packet, the linked audit record, and a dispute summary.
- Intended outputs: a case-intake header and a screening note.
- Deferred items: automatic screening, queue routing, formal case intake workflow.

#### 案情司 / Case Brief Lane

- Purpose: structure the affected artifacts, disputed points, and open response questions.
- Planned core functions:
  - `assemble_case_brief`
  - `request_case_response`
- Intended inputs: a case-intake header, linked artifacts, and response questions.
- Intended outputs: a case-brief descriptor and a response-request note.
- Deferred items: formal correspondence, evidence grading, external service integration.

#### 处置司 / Disposition Lane

- Purpose: document a recommended resolution path after escalated review.
- Planned core functions:
  - `recommend_case_disposition`
  - `record_case_resolution_header`
- Intended inputs: a case brief, response materials, and decision rationale.
- Intended outputs: a disposition recommendation and a case-resolution header.
- Deferred items: sanctions, appeals, case-management engine, automated enforcement.

### Non-Goals

The current prosecution freeze does not implement:

- routine audit operations
- automated escalation
- evidence grading logic
- sanctions
- formal case management
- orchestration runtime

## Cross-Cutting Rules

- Governance labels such as `核心决策层`, `吏部`, `户部`, `礼部`, `兵部`, `工部`, `刑部`, and `检察院` remain documentation-facing and human-facing labels.
- Python code uses ASCII and English names for packages, modules, offices, and functions.
- No functional office gets its own package tree yet.
- Office and lane functions live as static descriptors and header-contract definitions inside the current department or prosecution modules for now.
- Static descriptors may freeze intended inputs, outputs, non-goals, object-family ownership, and reserved CLI-family alignment.
- Static descriptors do not imply implemented handlers, registry IO, scientific execution, evidence grading, or service orchestration.
