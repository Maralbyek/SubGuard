from pathlib import Path


SCHEMA = (Path(__file__).parents[1] / "db" / "schema.sql").read_text(
    encoding="utf-8"
).lower()


def table_definition(name):
    table = SCHEMA.split(f"create table {name} (", 1)[1]
    return table.split(");", 1)[0]


def test_schema_contains_all_erd_tables():
    for table in (
        "business",
        "flow",
        "screen",
        "interface_element",
        "requirement",
        "clause",
        "finding",
        "annotation",
        "annotator",
        "pipeline_run",
        "evaluation_run",
    ):
        assert f"create table {table}" in SCHEMA


def test_evaluation_run_has_no_foreign_key():
    evaluation_table = table_definition("evaluation_run")
    assert "references " not in evaluation_table


def test_schema_preserves_order_and_nullable_finding_element():
    assert "unique (flow_id, screen_order)" in SCHEMA
    assert "interface_element_id bigint references interface_element" in SCHEMA


def test_annotation_labels_include_not_applicable_and_not_captured():
    annotation = table_definition("annotation")
    assert (
        "label text not null check "
        "(label in ('met', 'not_met', 'partial', 'n/a', 'nc'))"
    ) in annotation


def test_judge_verdict_excludes_annotation_only_labels():
    finding = table_definition("finding")
    assert "verdict text not null check (verdict in ('met', 'not_met', 'partial'))" in finding


def test_annotation_is_unique_per_flow_requirement_and_annotator():
    annotation = table_definition("annotation")
    assert "flow_id bigint not null references flow (flow_id)" in annotation
    assert (
        "req_id bigint not null references requirement (requirement_id)"
        in annotation
    )
    assert "finding_id" not in annotation
    assert "unique (flow_id, req_id, annotator_id)" in annotation


def test_findings_require_a_pipeline_run_and_are_unique_per_run():
    finding = table_definition("finding")
    assert "run_id uuid not null references pipeline_run (run_id)" in finding
    assert "unique (run_id, flow_id, requirement_id)" in finding


def test_pipeline_run_records_model_and_screenshot_setting():
    pipeline_run = table_definition("pipeline_run")
    assert "run_id uuid primary key" in pipeline_run
    assert "model varchar not null" in pipeline_run
    assert "screenshots_on boolean not null" in pipeline_run
    assert "created_at timestamp not null" in pipeline_run
