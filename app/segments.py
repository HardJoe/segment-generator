from collections import defaultdict

from app.domain import Canvas, Port, Segment


class InvalidGraphError(ValueError):
    """Raised when a segment cannot be resolved to valued source ports."""


class SegmentGenerator:
    """Derive segments from a canvas without database or HTTP dependencies."""

    def __init__(self, canvas: Canvas) -> None:
        self._ports = {port.id: port for port in canvas.ports}
        self._ports_by_node: dict[int, list[Port]] = defaultdict(list)
        for port in canvas.ports:
            self._ports_by_node[port.node_id].append(port)

        self._incoming_source: dict[int, int] = {}
        self._outgoing_ports: set[int] = set()
        for connection in canvas.connections:
            if connection.source_port_id not in self._ports:
                raise InvalidGraphError(
                    f"Unknown source port {connection.source_port_id}"
                )
            if connection.target_port_id not in self._ports:
                raise InvalidGraphError(
                    f"Unknown target port {connection.target_port_id}"
                )
            if connection.target_port_id in self._incoming_source:
                raise InvalidGraphError(
                    f"Port {connection.target_port_id} has multiple incoming connections"
                )
            if connection.source_port_id in self._outgoing_ports:
                raise InvalidGraphError(
                    f"Port {connection.source_port_id} has multiple outgoing connections"
                )
            self._incoming_source[connection.target_port_id] = (
                connection.source_port_id
            )
            self._outgoing_ports.add(connection.source_port_id)

    def generate(self) -> list[Segment]:
        segments: list[Segment] = []
        for target in sorted(self._ports.values(), key=lambda port: port.id):
            predecessors = self._predecessors(target)
            if target.value is None or not predecessors:
                continue

            sources: list[Port] = []
            for predecessor in predecessors:
                sources.extend(self._nearest_valued_ports(predecessor, frozenset()))
            sources.sort(key=lambda port: port.id)
            segments.append(Segment(target=target, sources=tuple(sources)))
        return segments

    def _predecessors(self, port: Port) -> list[Port]:
        source_id = self._incoming_source.get(port.id)
        if source_id is not None:
            return [self._ports[source_id]]

        if port.id not in self._outgoing_ports:
            return []

        return [
            candidate
            for candidate in self._ports_by_node[port.node_id]
            if candidate.id != port.id
        ]

    def _nearest_valued_ports(
        self, port: Port, active_path: frozenset[int]
    ) -> list[Port]:
        if port.value is not None:
            return [port]
        if port.id in active_path:
            raise InvalidGraphError(f"Cycle detected while tracing port {port.name}")

        predecessors = self._predecessors(port)
        if not predecessors:
            raise InvalidGraphError(
                f"Port {port.name} has no value and no path to a valued source"
            )

        sources: list[Port] = []
        next_path = active_path | {port.id}
        for predecessor in predecessors:
            sources.extend(self._nearest_valued_ports(predecessor, next_path))
        return sources
