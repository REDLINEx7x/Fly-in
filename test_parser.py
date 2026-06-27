"""Comprehensive test suite for map parser with all edge cases."""

import tempfile
import os
from map_parser import Parser


def test_case(name: str, content: str, should_pass: bool) -> None:
    """Test a single parser case."""
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
        f.write(content)
        temp_path = f.name

    try:
        parser = Parser(temp_path)
        parser.read_file()
        if should_pass:
            print(f"✅ PASS: {name}")
        else:
            print(f"❌ FAIL: {name} (should have raised error)")
    except ValueError as e:
        if not should_pass:
            print(f"✅ PASS: {name} - Error: {str(e)[:60]}")
        else:
            print(f"❌ FAIL: {name} - {str(e)[:60]}")
    except Exception as e:
        print(f"❌ FAIL: {name} - Unexpected: {type(e).__name__}: {str(e)[:60]}")
    finally:
        os.unlink(temp_path)


# ===== VALID CASES =====
print("\n=== VALID CASES ===")

# Minimal valid map
test_case(
    "Minimal valid map",
    """nb_drones: 1
start_hub: origin 0 0
hub: mid 1 1
end_hub: dest 2 2
connection: origin-mid
connection: mid-dest""",
    True,
)

# Multiple drones
test_case(
    "Multiple drones (10)",
    """nb_drones: 10
start_hub: a 0 0
hub: b 1 1
end_hub: c 2 2
connection: a-b
connection: b-c""",
    True,
)

# Negative coordinates
test_case(
    "Negative coordinates",
    """nb_drones: 1
start_hub: origin -100 -200
hub: mid 0 0
end_hub: dest 100 200
connection: origin-mid
connection: mid-dest""",
    True,
)

# Mixed positive/negative coordinates
test_case(
    "Mixed positive/negative coordinates",
    """nb_drones: 1
start_hub: a -5 10
hub: b 0 -3
hub: c 7 0
end_hub: d -1 1
connection: a-b
connection: b-c
connection: c-d""",
    True,
)

# Large coordinate values
test_case(
    "Large coordinate values",
    """nb_drones: 1
start_hub: a 999999 -999999
hub: b 0 0
end_hub: c 1000000 1000000
connection: a-b
connection: b-c""",
    True,
)

# Comments and empty lines
test_case(
    "Comments and empty lines",
    """# This is a comment
nb_drones: 2

# Another comment
start_hub: origin 0 0

hub: checkpoint 1 1

end_hub: goal 2 2
# More comments
connection: origin-checkpoint
connection: checkpoint-goal""",
    True,
)

# All zone types
test_case(
    "All zone types",
    """nb_drones: 1
start_hub: origin 0 0 [zone=normal]
hub: priority_zone 1 1 [zone=priority]
hub: restricted_zone 2 2 [zone=restricted]
hub: bypass 3 3 [color=cyan]
end_hub: dest 4 4 [zone=normal max_drones=5]
connection: origin-priority_zone
connection: priority_zone-restricted_zone
connection: restricted_zone-bypass
connection: bypass-dest
connection: origin-bypass""",
    True,
)

# Max drones metadata
test_case(
    "Max drones capacity",
    """nb_drones: 1
start_hub: a 0 0 [max_drones=10]
hub: b 1 1 [max_drones=1]
end_hub: c 2 2 [max_drones=100]
connection: a-b [max_link_capacity=5]
connection: b-c [max_link_capacity=1]""",
    True,
)

# Zone colors
test_case(
    "Zone colors",
    """nb_drones: 1
start_hub: a 0 0 [color=green]
hub: b 1 1 [color=red]
hub: c 2 2 [color=blue]
end_hub: d 3 3 [color=orange]
connection: a-b
connection: b-c
connection: c-d""",
    True,
)

# Bidirectional connections (same pair, different order)
test_case(
    "Complex network (5 zones)",
    """nb_drones: 3
start_hub: origin 0 0
hub: hub1 1 1
hub: hub2 2 2
hub: hub3 3 3
end_hub: dest 4 4
connection: origin-hub1
connection: origin-hub2
connection: hub1-hub3
connection: hub2-hub3
connection: hub3-dest""",
    True,
)

# Alphanumeric zone names
test_case(
    "Alphanumeric zone names",
    """nb_drones: 1
start_hub: zone1a 0 0
hub: zone2b 1 1
hub: zone3c 2 2
end_hub: zone4d 3 3
connection: zone1a-zone2b
connection: zone2b-zone3c
connection: zone3c-zone4d""",
    True,
)

# Multiple metadata fields
test_case(
    "Multiple metadata fields on zone",
    """nb_drones: 1
start_hub: a 0 0 [color=green max_drones=5 zone=normal]
hub: b 1 1 [zone=priority color=blue max_drones=3]
end_hub: c 2 2 [max_drones=10 color=red zone=normal]
connection: a-b
connection: b-c""",
    True,
)

# ===== INVALID CASES =====
print("\n=== INVALID CASES ===")

# Missing nb_drones
test_case(
    "Missing nb_drones line",
    """start_hub: a 0 0
hub: b 1 1
end_hub: c 2 2
connection: a-b
connection: b-c""",
    False,
)

# nb_drones not first
test_case(
    "nb_drones not first line",
    """# Comment first
start_hub: a 0 0
nb_drones: 1
hub: b 1 1
end_hub: c 2 2
connection: a-b
connection: b-c""",
    False,
)

# Invalid drone count (zero)
test_case(
    "Invalid drone count (zero)",
    """nb_drones: 0
start_hub: a 0 0
hub: b 1 1
end_hub: c 2 2
connection: a-b
connection: b-c""",
    False,
)

# Invalid drone count (negative)
test_case(
    "Invalid drone count (negative)",
    """nb_drones: -5
start_hub: a 0 0
hub: b 1 1
end_hub: c 2 2
connection: a-b
connection: b-c""",
    False,
)

# Invalid drone count (non-integer)
test_case(
    "Invalid drone count (non-integer)",
    """nb_drones: 3.5
start_hub: a 0 0
hub: b 1 1
end_hub: c 2 2
connection: a-b
connection: b-c""",
    False,
)

# Missing start_hub
test_case(
    "Missing start_hub",
    """nb_drones: 1
hub: b 1 1
end_hub: c 2 2
connection: b-c""",
    False,
)

# Missing end_hub
test_case(
    "Missing end_hub",
    """nb_drones: 1
start_hub: a 0 0
hub: b 1 1
connection: a-b""",
    False,
)

# Multiple start_hubs
test_case(
    "Multiple start_hubs",
    """nb_drones: 1
start_hub: a 0 0
start_hub: a2 1 1
hub: b 2 2
end_hub: c 3 3
connection: a-b
connection: a2-b
connection: b-c""",
    False,
)

# Multiple end_hubs
test_case(
    "Multiple end_hubs",
    """nb_drones: 1
start_hub: a 0 0
hub: b 1 1
end_hub: c 2 2
end_hub: c2 3 3
connection: a-b
connection: b-c
connection: b-c2""",
    False,
)

# Duplicate zone name
test_case(
    "Duplicate zone name",
    """nb_drones: 1
start_hub: a 0 0
hub: b 1 1
hub: b 2 2
end_hub: c 3 3
connection: a-b
connection: b-c""",
    False,
)

# Zone name with space
test_case(
    "Zone name with space",
    """nb_drones: 1
start_hub: "zone a" 0 0
hub: b 1 1
end_hub: c 2 2
connection: zone a-b
connection: b-c""",
    False,
)

# Zone name with dash
test_case(
    "Zone name with dash",
    """nb_drones: 1
start_hub: zone-a 0 0
hub: b 1 1
end_hub: c 2 2
connection: zone-a-b
connection: b-c""",
    False,
)

# Invalid coordinate (non-integer)
test_case(
    "Invalid coordinate (non-integer)",
    """nb_drones: 1
start_hub: a 0.5 1
hub: b 1 1
end_hub: c 2 2
connection: a-b
connection: b-c""",
    False,
)

# Self-connection
test_case(
    "Self-connection",
    """nb_drones: 1
start_hub: a 0 0
hub: b 1 1
end_hub: c 2 2
connection: a-b
connection: b-b
connection: b-c""",
    False,
)

# Duplicate connection
test_case(
    "Duplicate connection (same order)",
    """nb_drones: 1
start_hub: a 0 0
hub: b 1 1
end_hub: c 2 2
connection: a-b
connection: a-b
connection: b-c""",
    False,
)

# Duplicate connection (reverse order)
test_case(
    "Duplicate connection (reverse order)",
    """nb_drones: 1
start_hub: a 0 0
hub: b 1 1
end_hub: c 2 2
connection: a-b
connection: b-a
connection: b-c""",
    False,
)

# Connection to non-existent zone
test_case(
    "Connection to non-existent zone",
    """nb_drones: 1
start_hub: a 0 0
hub: b 1 1
end_hub: c 2 2
connection: a-b
connection: b-nonexistent
connection: b-c""",
    False,
)

# Invalid connection format (no dash)
test_case(
    "Invalid connection format (no dash)",
    """nb_drones: 1
start_hub: a 0 0
hub: b 1 1
end_hub: c 2 2
connection: a b
connection: b-c""",
    False,
)

# Invalid connection format (multiple dashes)
test_case(
    "Invalid connection format (multiple dashes)",
    """nb_drones: 1
start_hub: a 0 0
hub: b 1 1
end_hub: c 2 2
connection: a-b-c
connection: b-c""",
    False,
)

# Invalid metadata format (no equals)
test_case(
    "Invalid metadata format (no equals)",
    """nb_drones: 1
start_hub: a 0 0 [color green]
hub: b 1 1
end_hub: c 2 2
connection: a-b
connection: b-c""",
    False,
)

# Invalid max_drones (zero)
test_case(
    "Invalid max_drones (zero)",
    """nb_drones: 1
start_hub: a 0 0 [max_drones=0]
hub: b 1 1
end_hub: c 2 2
connection: a-b
connection: b-c""",
    False,
)

# Invalid max_drones (negative)
test_case(
    "Invalid max_drones (negative)",
    """nb_drones: 1
start_hub: a 0 0 [max_drones=-1]
hub: b 1 1
end_hub: c 2 2
connection: a-b
connection: b-c""",
    False,
)

# Invalid max_link_capacity (zero)
test_case(
    "Invalid max_link_capacity (zero)",
    """nb_drones: 1
start_hub: a 0 0
hub: b 1 1
end_hub: c 2 2
connection: a-b [max_link_capacity=0]
connection: b-c""",
    False,
)

# Invalid zone type
test_case(
    "Invalid zone type",
    """nb_drones: 1
start_hub: a 0 0 [zone=invalid]
hub: b 1 1
end_hub: c 2 2
connection: a-b
connection: b-c""",
    False,
)

# Blocked zone (should be allowed in parsing, but path should be blocked)
test_case(
    "Blocked zone in map",
    """nb_drones: 1
start_hub: a 0 0
hub: b 1 1 [zone=blocked]
hub: c 2 2
end_hub: d 3 3
connection: a-b
connection: b-c
connection: c-d""",
    True,
)

# Missing connection (disconnected graph)
test_case(
    "Disconnected graph (should parse but path finding will fail)",
    """nb_drones: 1
start_hub: a 0 0
hub: b 1 1
hub: c 2 2
end_hub: d 3 3
connection: a-b
connection: c-d""",
    True,
)

# Empty zones and connections
test_case(
    "Only hubs (minimal)",
    """nb_drones: 1
start_hub: a 0 0
end_hub: b 1 1
connection: a-b""",
    True,
)

# Very long zone names (alphanumeric)
test_case(
    "Long alphanumeric zone names",
    """nb_drones: 1
start_hub: longzonename1234567890abcdefg 0 0
hub: anotherlongzone_label_123 1 1
end_hub: finalzonewithreallylongname999 2 2
connection: longzonename1234567890abcdefg-anotherlongzone_label_123
connection: anotherlongzone_label_123-finalzonewithreallylongname999""",
    True,
)

print("\n=== TEST SUITE COMPLETE ===")
