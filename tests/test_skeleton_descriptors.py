from __future__ import annotations

from importlib import import_module

from macro_veritas.audit.specs import list_audit_outcomes
from macro_veritas.governance.a_header import (
    describe_a_header_function,
    describe_a_header_lane,
    list_a_header_core_functions,
    list_a_header_lanes,
    list_governance_domains,
    list_governed_departments,
)
from macro_veritas.governance.departments import (
    infrastructure,
    operations,
    personnel,
    registry,
    review,
    standards,
)
from macro_veritas.prosecution.specs import (
    describe_core_function as describe_prosecution_function,
    describe_functional_office as describe_prosecution_lane,
    describe_relation_to_audit,
    list_core_functions as list_prosecution_functions,
    list_functional_offices as list_prosecution_lanes,
)
from macro_veritas.registry.claim import list_lifecycle_states as claim_states
from macro_veritas.registry.dataset import list_lifecycle_states as dataset_states
from macro_veritas.registry.specs import list_registry_object_families
from macro_veritas.registry.study import list_lifecycle_states as study_states
from macro_veritas.shared.naming import list_reserved_cli_families, normalize_object_family_name


def _assert_descriptor_shape(descriptor: dict[str, object], required_keys: tuple[str, ...]) -> None:
    for key in required_keys:
        assert key in descriptor


def test_new_skeleton_modules_import() -> None:
    module_names = [
        "macro_veritas.governance",
        "macro_veritas.governance.a_header",
        "macro_veritas.governance.departments.personnel",
        "macro_veritas.governance.departments.registry",
        "macro_veritas.governance.departments.standards",
        "macro_veritas.governance.departments.operations",
        "macro_veritas.governance.departments.infrastructure",
        "macro_veritas.governance.departments.review",
        "macro_veritas.registry",
        "macro_veritas.registry.specs",
        "macro_veritas.registry.study",
        "macro_veritas.registry.dataset",
        "macro_veritas.registry.claim",
        "macro_veritas.runs.specs",
        "macro_veritas.audit.specs",
        "macro_veritas.prosecution.specs",
        "macro_veritas.shared.naming",
        "macro_veritas.shared.types",
    ]

    for module_name in module_names:
        assert import_module(module_name) is not None


def test_governance_descriptor_functions_return_expected_shapes() -> None:
    assert list_a_header_lanes() == ("mandate", "contracts", "oversight")
    assert "declare_review_route" in list_a_header_core_functions()
    assert list_governed_departments() == (
        "personnel",
        "registry",
        "standards",
        "operations",
        "infrastructure",
        "review",
    )
    assert "macro_veritas.prosecution" in list_governance_domains()

    mandate_lane = describe_a_header_lane("mandate")
    assert mandate_lane is not None
    _assert_descriptor_shape(
        mandate_lane,
        ("name", "governance_label", "purpose", "inputs", "outputs", "core_functions", "deferred_items"),
    )

    review_route = describe_a_header_function("declare_review_route")
    assert review_route is not None
    _assert_descriptor_shape(
        review_route,
        ("name", "purpose", "inputs", "outputs", "non_goals"),
    )


def test_department_descriptor_functions_return_expected_shapes() -> None:
    department_modules = [
        personnel,
        registry,
        standards,
        operations,
        infrastructure,
        review,
    ]

    for module in department_modules:
        assert module.department_name()
        assert module.describe_department_scope()
        assert module.list_functional_offices()
        assert module.list_core_functions()
        assert isinstance(module.list_deferred_capabilities(), tuple)

        office = module.describe_functional_office(module.list_functional_offices()[0])
        assert office is not None
        _assert_descriptor_shape(
            office,
            ("name", "governance_label", "purpose", "inputs", "outputs", "core_functions", "deferred_items"),
        )

        function_name = module.list_core_functions()[0]
        function_descriptor = module.describe_core_function(function_name)
        assert function_descriptor is not None
        _assert_descriptor_shape(
            function_descriptor,
            ("name", "purpose", "inputs", "outputs", "non_goals"),
        )


def test_descriptor_functions_return_doc_aligned_metadata() -> None:
    assert "StudyCard" in list_registry_object_families()
    assert study_states() == ("draft", "registered", "closed")
    assert dataset_states() == ("identified", "registered", "bound", "retired")
    assert claim_states() == ("captured", "scoped", "ready", "closed")
    assert list_audit_outcomes() == ("pass", "return", "escalate")
    assert "ingest" in list_reserved_cli_families()
    assert "show" in list_reserved_cli_families()
    assert "list" in list_reserved_cli_families()
    assert "delete" in list_reserved_cli_families()
    assert "bind_dataset_locator" in registry.list_core_functions()
    assert "show" in registry.list_expected_cli_families()
    assert "list" in registry.list_expected_cli_families()
    assert "delete" in registry.list_expected_cli_families()
    assert "escalate_review_case" in review.list_core_functions()
    assert "review" not in review.list_expected_cli_families()
    assert "case_intake_lane" in list_prosecution_lanes()
    assert "accept_escalated_case" in list_prosecution_functions()
    assert "routine audit" in describe_relation_to_audit()
    assert normalize_object_family_name("studycard") == "StudyCard"

    prosecution_lane = describe_prosecution_lane("case_intake_lane")
    assert prosecution_lane is not None
    _assert_descriptor_shape(
        prosecution_lane,
        ("name", "governance_label", "purpose", "inputs", "outputs", "core_functions", "deferred_items"),
    )

    prosecution_function = describe_prosecution_function("recommend_case_disposition")
    assert prosecution_function is not None
    _assert_descriptor_shape(
        prosecution_function,
        ("name", "purpose", "inputs", "outputs", "non_goals"),
    )
