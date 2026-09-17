import pytest

from app.domain import Canvas, Connection, Node, Port
from app.segments import InvalidGraphError, SegmentGenerator
from tests.canvas_data import supplied_canvas


def test_supplied_canvas_segments() -> None:
    segments = SegmentGenerator(supplied_canvas()).generate()

    assert [segment.formula for segment in segments] == [
        "2a - 1a",
        "2b - 2a",
        "11a - 8a",
        "11b - 9a",
        "11d - 10a",
        "11c - (11a + 11b + 11d)",
        "12a - (2b + 3a)",
        "12b - (4a + 5a)",
        "12c - 11c",
    ]
    assert [segment.result for segment in segments] == [
        -10,
        40,
        -50,
        -20,
        -20,
        -10,
        -30,
        -30,
        100,
    ]


def test_trace_stops_at_first_valued_port() -> None:
    segments = SegmentGenerator(supplied_canvas()).generate()
    segment_12c = next(segment for segment in segments if segment.target.name == "12c")

    assert [source.name for source in segment_12c.sources] == ["11c"]


def test_unresolved_null_source_is_rejected() -> None:
    canvas = Canvas(
        nodes=(Node(1, "1"), Node(2, "2")),
        ports=(Port(1, 1, "1a", None), Port(2, 2, "2a", 10)),
        connections=(Connection(1, 1, 2),),
    )

    with pytest.raises(InvalidGraphError, match="no value and no path"):
        SegmentGenerator(canvas).generate()


def test_multiple_connections_in_one_direction_are_rejected() -> None:
    canvas = Canvas(
        nodes=(Node(1, "1"), Node(2, "2"), Node(3, "3")),
        ports=(
            Port(1, 1, "1a", 1),
            Port(2, 2, "2a", 2),
            Port(3, 3, "3a", 3),
        ),
        connections=(Connection(1, 1, 2), Connection(2, 1, 3)),
    )

    with pytest.raises(InvalidGraphError, match="multiple outgoing"):
        SegmentGenerator(canvas)


def test_cycle_through_null_ports_is_rejected() -> None:
    canvas = Canvas(
        nodes=(Node(1, "1"), Node(2, "2"), Node(3, "3")),
        ports=(
            Port(1, 1, "1a", None),
            Port(2, 1, "1b", 10),
            Port(3, 2, "2a", None),
            Port(4, 3, "3a", 20),
        ),
        connections=(
            Connection(1, 1, 3),
            Connection(2, 3, 1),
            Connection(3, 2, 4),
        ),
    )

    with pytest.raises(InvalidGraphError, match="Cycle detected"):
        SegmentGenerator(canvas).generate()
