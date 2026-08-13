#!/usr/bin/env python3
"""Edge case tests for the Fly-in parser."""

import subprocess
import sys
import os
import tempfile

GREEN = '\033[1;32m'
RED = '\033[1;31m'
YELLOW = '\033[1;33m'
BLUE = '\033[1;34m'
NC = '\033[0m'

TESTS = [
    # (name, map_content, should_fail)
(
    "nb_drones_with_extra_colon",
    """\
nb_drones: 10:extra
start_hub: start 0 0
hub: middle 1 0
end_hub: goal 2 0
connection: start-middle
connection: middle-goal
""",
    True,
),

    (
        "no_drones_line",
        """\
start_hub: start 0 0
hub: a 1 0
end_hub: goal 2 0
connection: start-a
connection: a-goal
""",
        True,
    ),
    (
        "nb_drones_zero",
        """\
nb_drones: 0
start_hub: start 0 0
hub: a 1 0
end_hub: goal 2 0
connection: start-a
connection: a-goal
""",
        True,
    ),
    (
        "nb_drones_string",
        """\
nb_drones: abc
start_hub: start 0 0
end_hub: goal 2 0
connection: start-goal
""",
        True,
    ),
    (
        "no_start_hub",
        """\
nb_drones: 2
hub: a 1 0
end_hub: goal 2 0
connection: a-goal
""",
        True,
    ),
    (
        "two_start_hubs",
        """\
nb_drones: 2
start_hub: start1 0 0
start_hub: start2 1 0
end_hub: goal 2 0
connection: start1-goal
connection: start2-goal
""",
        True,
    ),
    (
        "no_end_hub",
        """\
nb_drones: 2
start_hub: start 0 0
hub: a 1 0
connection: start-a
""",
        True,
    ),
    (
        "dash_in_zone_name",
        """\
nb_drones: 2
start_hub: start-zone 0 0
end_hub: goal 2 0
connection: start-zone-goal
""",
        True,
    ),
    (
        "duplicate_zone_name",
        """\
nb_drones: 2
start_hub: start 0 0
hub: middle 1 0
hub: middle 2 0
end_hub: goal 3 0
connection: start-middle
connection: middle-goal
""",
        True,
    ),
    (
        "connection_unknown_zone",
        """\
nb_drones: 2
start_hub: start 0 0
end_hub: goal 2 0
connection: start-unknown
connection: unknown-goal
""",
        True,
    ),
    (
        "duplicate_connection",
        """\
nb_drones: 2
start_hub: start 0 0
hub: middle 1 0
end_hub: goal 2 0
connection: start-middle
connection: middle-start
connection: middle-goal
""",
        True,
    ),
    (
        "self_connection",
        """\
nb_drones: 2
start_hub: start 0 0
hub: middle 1 0
end_hub: goal 2 0
connection: middle-middle
connection: start-middle
connection: middle-goal
""",
        True,
    ),
    (
        "invalid_zone_type",
        """\
nb_drones: 2
start_hub: start 0 0
hub: middle 1 0 [zone=flying]
end_hub: goal 2 0
connection: start-middle
connection: middle-goal
""",
        True,
    ),
    (
        "invalid_max_drones_zero",
        """\
nb_drones: 2
start_hub: start 0 0
hub: middle 1 0 [max_drones=0]
end_hub: goal 2 0
connection: start-middle
connection: middle-goal
""",
        True,
    ),
    (
        "invalid_metadata_no_value",
        """\
nb_drones: 2
start_hub: start 0 0
hub: middle 1 0 [color]
end_hub: goal 2 0
connection: start-middle
connection: middle-goal
""",
        True,
    ),
    (
        "unknown_metadata_key",
        """\
nb_drones: 2
start_hub: start 0 0
hub: middle 1 0 [speed=fast]
end_hub: goal 2 0
connection: start-middle
connection: middle-goal
""",
        True,
    ),
    (
        "unrecognized_line",
        """\
nb_drones: 2
start_hub: start 0 0
end_hub: goal 2 0
zone: middle 1 0
connection: start-goal
""",
        True,
    ),
    (
        "valid_simple_map",
        """\
nb_drones: 2
start_hub: start 0 0 [color=green]
hub: middle 1 0 [color=blue]
end_hub: goal 2 0 [color=red]
connection: start-middle
connection: middle-goal
""",
        False,
    ),
    (
        "valid_with_comments_and_blanks",
        """\
# This is a comment
nb_drones: 2

start_hub: start 0 0
# Another comment
hub: middle 1 0
end_hub: goal 2 0

connection: start-middle
connection: middle-goal
""",
        False,
    ),
    (
        "valid_restricted_zone",
        """\
nb_drones: 2
start_hub: start 0 0
hub: restricted 1 0 [zone=restricted color=red]
end_hub: goal 2 0
connection: start-restricted
connection: restricted-goal
""",
        False,
    ),

    # ─── HIDDEN EDGE CASES ───────────────────────────────────────────

    # nb_drones with spaces around the number
    (
        "nb_drones_with_spaces",
        """\
nb_drones:    5
start_hub: start 0 0
hub: middle 1 0
end_hub: goal 2 0
connection: start-middle
connection: middle-goal
""",
        False,
    ),
    # nb_drones with float
    (
        "nb_drones_float",
        """\
nb_drones: 2.5
start_hub: start 0 0
hub: middle 1 0
end_hub: goal 2 0
connection: start-middle
connection: middle-goal
""",
        True,
    ),
    # nb_drones negative
    (
        "nb_drones_negative",
        """\
nb_drones: -3
start_hub: start 0 0
hub: middle 1 0
end_hub: goal 2 0
connection: start-middle
connection: middle-goal
""",
        True,
    ),
    # connection before zones are defined
    (
        "connection_before_zones",
        """\
nb_drones: 2
connection: start-goal
start_hub: start 0 0
end_hub: goal 2 0
""",
        True,
    ),
    # zone defined after connection that references it
    (
        "zone_defined_after_connection",
        """\
nb_drones: 2
start_hub: start 0 0
connection: start-goal
end_hub: goal 2 0
""",
        True,
    ),
    # duplicate metadata key in same bracket
    (
        "duplicate_metadata_key",
        """\
nb_drones: 2
start_hub: start 0 0
hub: middle 1 0 [color=red color=blue]
end_hub: goal 2 0
connection: start-middle
connection: middle-goal
""",
        True,
    ),
    # multiple = in metadata value
    (
        "multiple_equals_in_metadata",
        """\
nb_drones: 2
start_hub: start 0 0
hub: middle 1 0 [color=red=blue]
end_hub: goal 2 0
connection: start-middle
connection: middle-goal
""",
        True,
    ),
    # max_link_capacity zero
    (
        "max_link_capacity_zero",
        """\
nb_drones: 2
start_hub: start 0 0
hub: middle 1 0
end_hub: goal 2 0
connection: start-middle [max_link_capacity=0]
connection: middle-goal
""",
        True,
    ),
    # max_link_capacity float
    (
        "max_link_capacity_float",
        """\
nb_drones: 2
start_hub: start 0 0
hub: middle 1 0
end_hub: goal 2 0
connection: start-middle [max_link_capacity=1.5]
connection: middle-goal
""",
        True,
    ),
    # max_drones float
    (
        "max_drones_float",
        """\
nb_drones: 2
start_hub: start 0 0
hub: middle 1 0 [max_drones=2.5]
end_hub: goal 2 0
connection: start-middle
connection: middle-goal
""",
        True,
    ),
    # empty metadata brackets
    (
        "empty_metadata_brackets",
        """\
nb_drones: 2
start_hub: start 0 0
hub: middle 1 0 []
end_hub: goal 2 0
connection: start-middle
connection: middle-goal
""",
        False,
    ),
    # zone name that is only numbers
    (
        "numeric_zone_name",
        """\
nb_drones: 2
start_hub: start 0 0
hub: 123 1 0
end_hub: goal 2 0
connection: start-123
connection: 123-goal
""",
        False,
    ),
    # connection with three zones using dashes
    (
        "connection_three_zones",
        """\
nb_drones: 2
start_hub: start 0 0
hub: middle 1 0
end_hub: goal 2 0
connection: start-middle-goal
connection: start-middle
connection: middle-goal
""",
        True,
    ),
    # only comments and blanks after nb_drones
    (
        "only_comments_no_zones",
        """\
nb_drones: 2
# just comments
# nothing else
""",
        True,
    ),
    # start hub is also end hub (same name)
    (
        "start_and_end_same_name",
        """\
nb_drones: 2
start_hub: start 0 0
end_hub: start 0 0
connection: start-start
""",
        True,
    ),
    # nb_drones appears twice
    (
        "nb_drones_twice",
        """\
nb_drones: 2
nb_drones: 3
start_hub: start 0 0
end_hub: goal 2 0
connection: start-goal
""",
        True,
    ),
    # valid map with negative coordinates
    (
        "valid_negative_coordinates",
        """\
nb_drones: 2
start_hub: start -5 -3
hub: middle -2 0
end_hub: goal 0 3
connection: start-middle
connection: middle-goal
""",
        False,
    ),
    # valid map metadata in any order
    (
        "valid_metadata_any_order",
        """\
nb_drones: 2
start_hub: start 0 0 [max_drones=3 color=green zone=priority]
hub: middle 1 0 [zone=restricted color=orange]
end_hub: goal 2 0 [color=red max_drones=5]
connection: start-middle [max_link_capacity=2]
connection: middle-goal
""",
        False,
    ),
    # space in zone name
    (
        "space_in_zone_name",
        """\
nb_drones: 2
start_hub: start zone 0 0
end_hub: goal 2 0
connection: start-goal
""",
        True,
    ),
    # connection with no zones
    (
        "connection_no_dash",
        """\
nb_drones: 2
start_hub: start 0 0
end_hub: goal 2 0
connection: startgoal
""",
        True,
    ),
    # zone with missing coordinate
    (
        "zone_missing_coordinate",
        """\
nb_drones: 2
start_hub: start 0
end_hub: goal 2 0
connection: start-goal
""",
        True,
    ),
    # zone with float coordinate
    (
        "zone_float_coordinate",
        """\
nb_drones: 2
start_hub: start 0.5 0
end_hub: goal 2 0
connection: start-goal
""",
        True,
    ),
]


def run_test(name: str, content: str, should_fail: bool) -> bool:
    with tempfile.NamedTemporaryFile(
        mode='w', suffix='.txt', delete=False
    ) as f:
        f.write(content)
        tmp_path = f.name

    try:
        result = subprocess.run(
            [sys.executable, 'fly-in.py', tmp_path],
            capture_output=True,
            text=True,
            timeout=10,
        )
        crashed = result.returncode != 0

        if should_fail and crashed:
            print(f"  [{GREEN}PASS{NC}] {name} → correctly rejected")
            return True
        elif not should_fail and not crashed:
            print(f"  [{GREEN}PASS{NC}] {name} → correctly accepted")
            return True
        elif should_fail and not crashed:
            print(f"  [{RED}FAIL{NC}] {name} → should have been rejected")
            print(f"         stdout: {result.stdout.strip()[:100]}")
            return False
        else:
            print(f"  [{RED}FAIL{NC}] {name} → should have been accepted")
            print(f"         stderr: {result.stderr.strip()[:100]}")
            return False
    except subprocess.TimeoutExpired:
        print(f"  [{RED}TIMEOUT{NC}] {name}")
        return False
    finally:
        os.unlink(tmp_path)


def main() -> None:
    print(f"{BLUE}=========================================={NC}")
    print(f"{BLUE}     🔍 FLY-IN PARSER EDGE CASE TESTS    {NC}")
    print(f"{BLUE}=========================================={NC}\n")

    passed = 0
    failed = 0

    categories = {
        "nb_drones": [
            "no_drones_line",
            "nb_drones_zero",
            "nb_drones_string",
            "nb_drones_float",
            "nb_drones_negative",
            "nb_drones_with_spaces",
            "nb_drones_twice",
        ],
        "start/end hub": [
            "no_start_hub",
            "two_start_hubs",
            "no_end_hub",
            "start_and_end_same_name",
        ],
        "zone names": [
            "dash_in_zone_name",
            "duplicate_zone_name",
            "space_in_zone_name",
            "numeric_zone_name",
        ],
        "connections": [
            "connection_unknown_zone",
            "duplicate_connection",
            "self_connection",
            "connection_before_zones",
            "zone_defined_after_connection",
            "connection_three_zones",
            "connection_no_dash",
        ],
        "metadata": [
            "invalid_zone_type",
            "invalid_max_drones_zero",
            "invalid_metadata_no_value",
            "unknown_metadata_key",
            "duplicate_metadata_key",
            "multiple_equals_in_metadata",
            "max_link_capacity_zero",
            "max_link_capacity_float",
            "max_drones_float",
            "empty_metadata_brackets",
            "valid_metadata_any_order",
        ],
        "coordinates": [
            "zone_missing_coordinate",
            "zone_float_coordinate",
            "valid_negative_coordinates",
        ],
        "misc": [
            "unrecognized_line",
            "only_comments_no_zones",
        ],
        "valid maps": [
            "valid_simple_map",
            "valid_with_comments_and_blanks",
            "valid_restricted_zone",
        ],
    }

    test_map = {t[0]: t for t in TESTS}

    for category, names in categories.items():
        print(f"{YELLOW}▶ {category.upper()}{NC}")
        for name in names:
            if name in test_map:
                _, content, should_fail = test_map[name]
                if run_test(name, content, should_fail):
                    passed += 1
                else:
                    failed += 1
        print()

    print(f"{BLUE}=========================================={NC}")
    print(f"  {GREEN}PASS: {passed}{NC} | {RED}FAIL: {failed}{NC}")
    print(f"{BLUE}=========================================={NC}")


if __name__ == '__main__':
    main()
