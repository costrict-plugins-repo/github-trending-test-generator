---
name: auto-test
description: This skill should be used when the user writes new code, creates a new file, adds a new function or method, asks about testing, mentions "test", "spec", "coverage", or "TDD", or when source files are created/edited that don't have corresponding test files.
version: 1.0.0
---

# Auto Test Skill

This skill automatically suggests test generation when new code is written or modified.

## When This Skill Applies

Activate when:
- The user creates a new source file (not a test file)
- The user adds a new public function or method to an existing file
- The user asks "how should I test this?" or similar
- The user mentions TDD, test coverage, or testing strategy
- A source file is modified that has no corresponding test file

Do NOT activate when:
- The user is editing a test file
- The user is writing configuration, documentation, or migrations
- The user explicitly says they don't want tests

## Behavior

### After new code is written

1. **Check for existing tests** - Look for a corresponding test file
2. **If no test file exists**, suggest:
   ```
   This file doesn't have tests yet. Want me to generate them?
   Detected framework: <framework>
   Test file would be: <path>
   Public methods to cover: <list>
   ```
3. **If test file exists but doesn't cover new code**, suggest:
   ```
   The existing test file at <path> doesn't cover these new methods:
   - <method_name>
   Want me to add tests for them?
   ```

### Test generation approach

When generating tests:

1. **Read the source file** to understand the code
2. **Read existing tests** in the project to match style and conventions
3. **Detect the framework** from project config files
4. **Generate tests** covering:
   - Happy path for each public method
   - Edge cases (nil, empty, boundary values)
   - Error cases (invalid input, exceptions)
5. **Show the tests** before writing, let the user approve

### Framework detection priority

1. Check project root for config files (Gemfile, package.json, pyproject.toml, etc.)
2. Check existing test directories (spec/, test/, __tests__/, tests/)
3. Look at existing test file imports to confirm the framework
4. Default to the most common framework for the language if ambiguous

### Response format

When suggesting tests:

```
**Test suggestion for <source_file>**
Framework: <detected>
Test file: <target_path>
Coverage: <N> methods, <M> tests

Want me to generate the full test file?
```

When writing tests:

```
**Generated tests for <source_file>**
Framework: <detected>
Tests: <count>
Covers: <method list>

<test code>
```
