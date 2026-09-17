from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent


def test_schema_enforces_single_wiring_per_direction() -> None:
    schema = " ".join(
        (PROJECT_ROOT / "db/schema.sql").read_text(encoding="utf-8").split()
    )

    assert "source_port_id BIGINT NOT NULL UNIQUE" in schema
    assert "target_port_id BIGINT NOT NULL UNIQUE" in schema
    assert "CHECK (source_port_id <> target_port_id)" in schema


def test_seed_contains_exact_canvas_size_and_null_ports() -> None:
    seed = (PROJECT_ROOT / "db/seed.sql").read_text(encoding="utf-8")

    assert seed.count("NULL)") == 6
    assert "(12, '12')" in seed
    assert "(22, 12, '12c', 400)" in seed
    assert "(11, 19, 22)" in seed
    assert seed.count("SELECT setval(") == 3
