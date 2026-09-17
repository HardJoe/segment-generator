from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Node:
    id: int
    name: str


@dataclass(frozen=True, slots=True)
class Port:
    id: int
    node_id: int
    name: str
    value: int | None


@dataclass(frozen=True, slots=True)
class Connection:
    id: int
    source_port_id: int
    target_port_id: int


@dataclass(frozen=True, slots=True)
class Canvas:
    nodes: tuple[Node, ...]
    ports: tuple[Port, ...]
    connections: tuple[Connection, ...]


@dataclass(frozen=True, slots=True)
class Segment:
    target: Port
    sources: tuple[Port, ...]

    @property
    def formula(self) -> str:
        source_names = " + ".join(port.name for port in self.sources)
        if len(self.sources) > 1:
            source_names = f"({source_names})"
        return f"{self.target.name} - {source_names}"

    @property
    def result(self) -> int:
        assert self.target.value is not None
        return self.target.value - sum(
            port.value for port in self.sources if port.value is not None
        )
