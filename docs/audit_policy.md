# Audit Policy

## Scope

Audit exists in MacroVeritas to keep registry objects and artifact bundles reviewable, traceable, and safe to use for later evidence work. In the MVP documentation stage, audit is a governance policy, not an implemented engine.

- Audit in this phase is human-led and document-driven.
- No automated audit service, scoring engine, or adjudication system is implemented.
- The routine audit and review lane is the lightweight review domain closest to the future `刑部` concept.
- A future escalated review / prosecution lane (`检察院`) is distinct and is not implemented here.

## What Can Be Audited At MVP Level

At MVP level, audit can reasonably assess whether the record is clear enough to trust as project input:

- `StudyCard` identity and source provenance completeness
- `DatasetCard` study linkage and filesystem binding traceability
- `ClaimCard` scope clarity and source linkage
- `MethodCard` declared method context and version labeling
- `ReanalysisBundle` artifact presence, manifest completeness, and input/output traceability
- `EvidenceCard` linkage to claim, dataset, method, and supporting artifacts
- `AuditRecord` completeness as a review record

This is not the same as proving scientific truth.

## Audit Trigger Points

The MVP audit policy should be applied at a small number of high-value transition points:

- when a `StudyCard` is moving from draft to registered
- when a `DatasetCard` is first bound to a usable project location
- when a `ClaimCard` is marked ready for downstream work
- when a `ReanalysisBundle` is assembled for review
- before an `EvidenceCard` is treated as reportable project output

## Outcomes

Audit outcomes are intentionally simple:

- `pass`: the object is sufficiently documented and linked for its current stage
- `return`: the object needs clarification, missing provenance, or corrected linkage before it should continue
- `escalate`: the issue is material enough to require project-lead review or handoff to a stronger future review lane

An audit outcome should not delete artifacts or erase history.

## Routine Review And Escalated Review

MacroVeritas distinguishes two review concepts at the documentation level:

- Routine review / audit lane: the default MVP review path for traceability, provenance, linkage, and stage readiness. This is the concept closest to the future `刑部`-like review domain.
- Escalated review / prosecution lane: a separate future concept for materially disputed, high-risk, or governance-sensitive cases. This is the concept closest to the future `检察院` lane.

For the MVP documentation layer:

- routine review remains the primary and lightweight review policy
- `AuditRecord` remains the planned record of routine review being applied
- escalated review should build on routine audit outputs rather than replace them
- neither lane is implemented as a service, engine, or formal workflow system

## What Audit Failure Does Not Mean

An audit failure does not, by itself, mean:

- the paper is wrong
- the dataset is fraudulent
- the claim is scientifically false
- the analyst acted in bad faith
- the work can never proceed

At MVP level, failure usually means the current record is not yet strong enough for trusted downstream use.

## Relation To Future "检察院" Concept

MacroVeritas may later adopt a stronger, more adversarial review concept sometimes described as a `检察院` lane. That future concept remains distinct from routine audit and is not implemented here.
