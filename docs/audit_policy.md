# Audit Policy

## Scope

Audit exists in MacroVeritas to keep registry objects and artifact bundles reviewable, traceable, and safe to use for later evidence work. In the MVP documentation stage, audit is a governance policy, not an implemented engine.

- Audit in this phase is human-led and document-driven.
- No automated audit service, scoring engine, or adjudication system is implemented.

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
- `escalate`: the issue is material enough to require project-lead review or a stronger future review lane

An audit outcome should not delete artifacts or erase history.

## What Audit Failure Does Not Mean

An audit failure does not, by itself, mean:

- the paper is wrong
- the dataset is fraudulent
- the claim is scientifically false
- the analyst acted in bad faith
- the work can never proceed

At MVP level, failure usually means the current record is not yet strong enough for trusted downstream use.

## Relation To Future "检察院" Concept

MacroVeritas may later adopt a stronger, more adversarial review concept sometimes described as a "检察院" lane. That future concept is not implemented here.

For the MVP documentation layer:

- audit is the lightweight review and traceability policy
- `AuditRecord` is the planned record of that policy being applied
- future "检察院" work, if added, should build on these audit records rather than replace the need for basic object traceability
