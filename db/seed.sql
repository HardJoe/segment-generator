BEGIN;

INSERT INTO nodes (id, name)
VALUES
    (1, '1'),
    (2, '2'),
    (3, '3'),
    (4, '4'),
    (5, '5'),
    (6, '6'),
    (7, '7'),
    (8, '8'),
    (9, '9'),
    (10, '10'),
    (11, '11'),
    (12, '12')
ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name;

INSERT INTO ports (id, node_id, name, value)
VALUES
    (1, 1, '1a', 100),
    (2, 2, '2a', 90),
    (3, 2, '2b', 130),
    (4, 3, '3a', 150),
    (5, 4, '4a', 70),
    (6, 5, '5a', 160),
    (7, 6, '6a', NULL),
    (8, 6, '6b', NULL),
    (9, 6, '6c', NULL),
    (10, 7, '7a', NULL),
    (11, 7, '7b', NULL),
    (12, 7, '7c', NULL),
    (13, 8, '8a', 200),
    (14, 9, '9a', 120),
    (15, 10, '10a', 80),
    (16, 11, '11a', 150),
    (17, 11, '11b', 100),
    (18, 11, '11d', 60),
    (19, 11, '11c', 300),
    (20, 12, '12a', 250),
    (21, 12, '12b', 200),
    (22, 12, '12c', 400)
ON CONFLICT (id) DO UPDATE SET
    node_id = EXCLUDED.node_id,
    name = EXCLUDED.name,
    value = EXCLUDED.value;

INSERT INTO connections (id, source_port_id, target_port_id)
VALUES
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
    (11, 19, 22)
ON CONFLICT (id) DO UPDATE SET
    source_port_id = EXCLUDED.source_port_id,
    target_port_id = EXCLUDED.target_port_id;

SELECT setval(pg_get_serial_sequence('nodes', 'id'), (SELECT MAX(id) FROM nodes));
SELECT setval(pg_get_serial_sequence('ports', 'id'), (SELECT MAX(id) FROM ports));
SELECT setval(
    pg_get_serial_sequence('connections', 'id'),
    (SELECT MAX(id) FROM connections)
);

COMMIT;
