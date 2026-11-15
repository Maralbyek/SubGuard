from pathlib import Path


SCHEMA = (Path(__file__).parents[1] / "db" / "schema.sql").read_text(
    encoding="utf-8"
).lower()


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
        "evaluation_run",
    ):
        assert f"create table {table}" in SCHEMA


def test_evaluation_run_has_no_foreign_key():
    evaluation_table = SCHEMA.split("create table evaluation_run", 1)[1]
    evaluation_table = evaluation_table.split("create index", 1)[0]
    assert "references " not in evaluation_table


def test_schema_preserves_order_and_nullable_finding_element():
    assert "unique (flow_id, screen_order)" in SCHEMA
    assert "interface_element_id bigint references interface_element" in SCHEMA
