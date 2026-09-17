from app.domain import Canvas, Connection, Node, Port


def supplied_canvas() -> Canvas:
    nodes = tuple(Node(id=node_id, name=str(node_id)) for node_id in range(1, 13))
    port_data = (
        (1, 1, "1a", 100),
        (2, 2, "2a", 90),
        (3, 2, "2b", 130),
        (4, 3, "3a", 150),
        (5, 4, "4a", 70),
        (6, 5, "5a", 160),
        (7, 6, "6a", None),
        (8, 6, "6b", None),
        (9, 6, "6c", None),
        (10, 7, "7a", None),
        (11, 7, "7b", None),
        (12, 7, "7c", None),
        (13, 8, "8a", 200),
        (14, 9, "9a", 120),
        (15, 10, "10a", 80),
        (16, 11, "11a", 150),
        (17, 11, "11b", 100),
        (18, 11, "11d", 60),
        (19, 11, "11c", 300),
        (20, 12, "12a", 250),
        (21, 12, "12b", 200),
        (22, 12, "12c", 400),
    )
    connection_data = (
        (1, 1, 2),
        (2, 3, 8),
        (3, 4, 7),
        (4, 9, 20),
        (5, 5, 10),
        (6, 6, 11),
        (7, 12, 21),
        (8, 13, 16),
        (9, 14, 17),
        (10, 15, 18),
        (11, 19, 22),
    )
    return Canvas(
        nodes=nodes,
        ports=tuple(Port(*data) for data in port_data),
        connections=tuple(Connection(*data) for data in connection_data),
    )
