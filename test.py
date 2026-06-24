"""Test runner for Fly-in simulation maps."""

import subprocess
import sys
import time
from dataclasses import dataclass


@dataclass
class TestCase:
    """Represents a single map test case.

    Attributes:
        name: Human-readable test name.
        filepath: Path to the map file.
        max_turns: Maximum acceptable turn count.
        category: Difficulty category.
    """

    name: str
    filepath: str
    max_turns: int
    category: str


TESTS: list[TestCase] = [
    TestCase("Linear path",         "easy_1_linear.txt",          6,  "EASY"),
    TestCase("Simple fork",         "easy_2_fork.txt",            6,  "EASY"),
    TestCase("Basic capacity",      "easy_3_capacity.txt",        8,  "EASY"),
    TestCase("Dead end trap",       "medium_1_deadend.txt",       15, "MEDIUM"),
    TestCase("Circular loop",       "medium_2_loop.txt",          20, "MEDIUM"),
    TestCase("Priority puzzle",     "medium_3_priority.txt",      12, "MEDIUM"),
    TestCase("Maze nightmare",      "hard_1_maze.txt",            45, "HARD"),
    TestCase("Capacity hell",       "hard_2_capacity.txt",        60, "HARD"),
    TestCase("Ultimate challenge",  "hard_3_ultimate.txt",        35, "HARD"),
    TestCase("Impossible Dream",    "challenger_impossible_dream.txt", 45, "CHALLENGER"),
]

COLORS = {
    "green":  "\033[92m",
    "red":    "\033[91m",
    "yellow": "\033[93m",
    "cyan":   "\033[96m",
    "white":  "\033[97m",
    "gray":   "\033[90m",
    "reset":  "\033[0m",
}

CATEGORY_COLORS = {
    "EASY":       COLORS["green"],
    "MEDIUM":     COLORS["yellow"],
    "HARD":       COLORS["red"],
    "CHALLENGER": COLORS["cyan"],
}


def colorize(text: str, color: str) -> str:
    """Wrap text in an ANSI color code.

    Args:
        text: Text to colorize.
        color: Key from COLORS dict.

    Returns:
        Colorized string.
    """
    return f"{COLORS.get(color, '')}{text}{COLORS['reset']}"


def run_test(test: TestCase, main_script: str) -> tuple[bool, int, str, float]:
    """Run a single test case and return results.

    Args:
        test: The test case to run.
        main_script: Path to the main fly-in script.

    Returns:
        Tuple of (passed, turn_count, error_message, elapsed_seconds).
    """
    start_time = time.time()
    try:
        result = subprocess.run(
            [sys.executable, main_script, test.filepath],
            capture_output=True,
            text=True,
            timeout=30,
        )
        elapsed = time.time() - start_time
        print(result.stdout)
        if result.returncode != 0:
            return False, 0, result.stderr.strip() or result.stdout.strip(), elapsed

        lines = [
            line for line in result.stdout.strip().split("\n")
            if line.strip() and not line.startswith("\033")
        ]

        turn_count = len(lines)
        passed = turn_count <= test.max_turns
        return passed, turn_count, "", elapsed

    except subprocess.TimeoutExpired:
        elapsed = time.time() - start_time
        return False, 0, "TIMEOUT after 30 seconds", elapsed
    except Exception as e:
        elapsed = time.time() - start_time
        return False, 0, str(e), elapsed


def print_header() -> None:
    """Print the test runner header."""
    print(colorize("=" * 65, "cyan"))
    print(colorize("  FLY-IN TEST RUNNER", "cyan"))
    print(colorize("=" * 65, "cyan"))
    print()


def print_category_header(category: str) -> None:
    """Print a category section header.

    Args:
        category: The difficulty category name.
    """
    color = CATEGORY_COLORS.get(category, "white")
    print(f"\n{color}── {category} {'─' * (55 - len(category))}{COLORS['reset']}")


def print_result(test: TestCase, passed: bool, turns: int, error: str, elapsed: float) -> None:
    """Print a single test result line.

    Args:
        test: The test case.
        passed: Whether the test passed.
        turns: Number of turns taken.
        error: Error message if failed.
        elapsed: Time taken in seconds.
    """
    status = colorize("PASS", "green") if passed else colorize("FAIL", "red")
    name_padded = test.name.ljust(22)

    if error:
        print(f"  [{status}] {name_padded} ERROR: {colorize(error, 'gray')}")
    else:
        turns_str = f"{turns} turns"
        target_str = f"(target ≤ {test.max_turns})"
        time_str = colorize(f"{elapsed:.2f}s", "gray")

        if passed:
            turns_colored = colorize(turns_str, "green")
        else:
            turns_colored = colorize(turns_str, "red")

        print(f"  [{status}] {name_padded} {turns_colored} {target_str} {time_str}")


def print_summary(
    results: list[tuple[TestCase, bool, int, str, float]]
) -> None:
    """Print the final summary of all test results.

    Args:
        results: List of (test, passed, turns, error, elapsed) tuples.
    """
    total = len(results)
    passed = sum(1 for _, p, _, _, _ in results if p)
    failed = total - passed
    total_time = sum(e for _, _, _, _, e in results)

    print()
    print(colorize("=" * 65, "cyan"))
    print(colorize("  SUMMARY", "cyan"))
    print(colorize("=" * 65, "cyan"))

    pass_str = colorize(f"{passed} passed", "green")
    fail_str = colorize(f"{failed} failed", "red") if failed else colorize("0 failed", "gray")
    print(f"  {pass_str}  {fail_str}  {colorize(f'{total_time:.2f}s total', 'gray')}")

    if failed > 0:
        print()
        print(colorize("  Failed tests:", "red"))
        for test, p, turns, error, _ in results:
            if not p:
                if error:
                    print(f"    • {test.name}: {error}")
                else:
                    print(
                        f"    • {test.name}: {turns} turns "
                        f"(exceeded target of {test.max_turns})"
                    )

    print(colorize("=" * 65, "cyan"))
    print()


def main() -> None:
    """Entry point for the test runner."""
    if len(sys.argv) < 2:
        print(f"Usage: python {sys.argv[0]} <path_to_main_script>")
        print(f"Example: python {sys.argv[0]} ../fly-in.py")
        sys.exit(1)

    main_script = sys.argv[1]
    results: list[tuple[TestCase, bool, int, str, float]] = []
    current_category = ""

    print_header()

    for test in TESTS:
        if test.category != current_category:
            current_category = test.category
            print_category_header(current_category)

        passed, turns, error, elapsed = run_test(test, main_script)
        results.append((test, passed, turns, error, elapsed))
        print_result(test, passed, turns, error, elapsed)

    print_summary(results)


    all_passed = all(p for _, p, _, _, _ in results)
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
