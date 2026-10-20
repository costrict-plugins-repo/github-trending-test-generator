#!/usr/bin/env python3
"""
Test Reminder Hook for Claude Code
After writing/editing source files, checks if a corresponding test file exists
and reminds to generate tests if not.
"""

import json
import os
import sys

# Patterns that indicate a file IS a test file (skip these)
TEST_FILE_PATTERNS = [
    lambda p: "_spec.rb" in p,
    lambda p: "_test.rb" in p,
    lambda p: "_test.go" in p,
    lambda p: "_test.exs" in p,
    lambda p: p.endswith(".test.js") or p.endswith(".test.ts") or p.endswith(".test.tsx") or p.endswith(".test.jsx"),
    lambda p: p.endswith(".spec.js") or p.endswith(".spec.ts") or p.endswith(".spec.tsx") or p.endswith(".spec.jsx"),
    lambda p: "test_" in os.path.basename(p) and p.endswith(".py"),
    lambda p: p.endswith("Test.php"),
    lambda p: "__tests__/" in p,
    lambda p: "/spec/" in p,
    lambda p: "/test/" in p and not "/test_" in p,
    lambda p: "/tests/" in p,
]

# Patterns that indicate a file is a SOURCE file worth testing
SOURCE_FILE_PATTERNS = [
    # Ruby/Rails
    {
        "check": lambda p: p.endswith(".rb") and any(d in p for d in [
            "app/models/", "app/controllers/", "app/services/",
            "app/jobs/", "app/mailers/", "app/helpers/",
            "lib/",
        ]),
        "test_paths": lambda p: [
            p.replace("app/", "spec/").replace(".rb", "_spec.rb"),
            p.replace("app/", "test/").replace(".rb", "_test.rb"),
            p.replace("lib/", "spec/lib/").replace(".rb", "_spec.rb"),
        ],
    },
    # Python
    {
        "check": lambda p: p.endswith(".py") and not p.endswith("__init__.py") and any(d in p for d in [
            "src/", "app/", "lib/",
        ]),
        "test_paths": lambda p: [
            "tests/test_" + os.path.basename(p),
            "tests/" + os.path.dirname(p).split("/")[-1] + "/test_" + os.path.basename(p),
        ],
    },
    # JavaScript/TypeScript
    {
        "check": lambda p: any(p.endswith(ext) for ext in [".js", ".ts", ".tsx", ".jsx"]) and "src/" in p,
        "test_paths": lambda p: [
            p.replace("/src/", "/src/__tests__/").rsplit(".", 1)[0] + ".test." + p.rsplit(".", 1)[1],
            p.rsplit(".", 1)[0] + ".test." + p.rsplit(".", 1)[1],
            p.rsplit(".", 1)[0] + ".spec." + p.rsplit(".", 1)[1],
        ],
    },
    # Go
    {
        "check": lambda p: p.endswith(".go") and not p.endswith("_test.go"),
        "test_paths": lambda p: [
            p.replace(".go", "_test.go"),
        ],
    },
    # PHP
    {
        "check": lambda p: p.endswith(".php") and "app/" in p,
        "test_paths": lambda p: [
            "tests/Unit/" + os.path.basename(p).replace(".php", "Test.php"),
            "tests/Feature/" + os.path.basename(p).replace(".php", "Test.php"),
        ],
    },
    # Elixir
    {
        "check": lambda p: p.endswith(".ex") and "lib/" in p,
        "test_paths": lambda p: [
            p.replace("lib/", "test/").replace(".ex", "_test.exs"),
        ],
    },
]

# Files to never suggest tests for
SKIP_PATTERNS = [
    lambda p: "migration" in p.lower(),
    lambda p: "config/" in p,
    lambda p: "db/" in p and "migrate" in p,
    lambda p: p.endswith(".md"),
    lambda p: p.endswith(".json"),
    lambda p: p.endswith(".yml") or p.endswith(".yaml"),
    lambda p: p.endswith(".toml"),
    lambda p: p.endswith(".lock"),
    lambda p: p.endswith(".env"),
    lambda p: "vendor/" in p,
    lambda p: "node_modules/" in p,
]


def is_test_file(file_path):
    """Check if this file is itself a test file."""
    normalized = file_path.lstrip("/")
    return any(check(normalized) for check in TEST_FILE_PATTERNS)


def should_skip(file_path):
    """Check if this file should be skipped entirely."""
    normalized = file_path.lstrip("/")
    return any(check(normalized) for check in SKIP_PATTERNS)


def find_test_path(file_path):
    """Find where the test file should be for this source file."""
    normalized = file_path.lstrip("/")
    for pattern in SOURCE_FILE_PATTERNS:
        if pattern["check"](normalized):
            return pattern["test_paths"](normalized)
    return []


def get_state_file(session_id):
    """Session-scoped state to avoid repeat reminders."""
    return os.path.expanduser(
        f"~/.claude/test_reminder_state_{session_id}.json"
    )


def load_reminded(session_id):
    """Load set of files already reminded about."""
    path = get_state_file(session_id)
    if os.path.exists(path):
        try:
            with open(path, "r") as f:
                return set(json.load(f))
        except (json.JSONDecodeError, IOError):
            return set()
    return set()


def save_reminded(session_id, reminded):
    """Save reminded files set."""
    path = get_state_file(session_id)
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            json.dump(list(reminded), f)
    except IOError:
        pass


def main():
    if os.environ.get("DISABLE_TEST_REMINDER", "0") == "1":
        sys.exit(0)

    try:
        input_data = json.loads(sys.stdin.read())
    except json.JSONDecodeError:
        sys.exit(0)

    session_id = input_data.get("session_id", "default")
    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input", {})

    if tool_name not in ("Edit", "Write", "MultiEdit"):
        sys.exit(0)

    file_path = tool_input.get("file_path", "")
    if not file_path:
        sys.exit(0)

    # Skip test files, config, migrations, etc.
    if is_test_file(file_path) or should_skip(file_path):
        sys.exit(0)

    # Check if this is a testable source file
    test_paths = find_test_path(file_path)
    if not test_paths:
        sys.exit(0)

    # Check if any test file already exists
    for tp in test_paths:
        # Try absolute path and relative to common project roots
        if os.path.exists(tp) or os.path.exists("/" + tp):
            sys.exit(0)  # Test file exists, no reminder needed

    # Dedup: only remind once per session per file
    reminded = load_reminded(session_id)
    if file_path in reminded:
        sys.exit(0)

    reminded.add(file_path)
    save_reminded(session_id, reminded)

    # Output reminder
    expected = test_paths[0] if test_paths else "unknown"
    print(
        f"No test file found for {os.path.basename(file_path)}.\n"
        f"Expected test at: {expected}\n"
        f"Run /generate-tests {file_path} to create one.",
        file=sys.stderr,
    )
    sys.exit(0)  # Exit 0 for PostToolUse - don't block, just inform


if __name__ == "__main__":
    main()
