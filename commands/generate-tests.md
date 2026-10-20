---
description: Generate test files for source files that lack test coverage
argument-hint: [file-or-directory-path]
allowed-tools: [Read, Glob, Grep, Write, Bash]
---

# Generate Tests

Generate test files for source code that lacks test coverage.

## Arguments

The user invoked this command with: $ARGUMENTS

## Instructions

### Step 1: Determine scope

- If the user provided a **file path**, generate tests for that specific file
- If the user provided a **directory path**, scan for source files missing tests
- If **no argument**, scan the entire project for untested source files

### Step 2: Detect the test framework

Check for these in order:
1. `Gemfile` / `Gemfile.lock` - look for `rspec` or `minitest`
2. `package.json` - look for `jest`, `vitest`, or `mocha`
3. `pyproject.toml` / `requirements.txt` / `setup.py` - look for `pytest`
4. `phpunit.xml` / `composer.json` - look for `phpunit`
5. `go.mod` - Go project, uses built-in `testing`
6. `mix.exs` - Elixir project, uses `ExUnit`
7. `Cargo.toml` - Rust project, uses built-in `#[test]`

### Step 3: Find untested files

For each source file, check if a corresponding test file exists:

**Ruby/Rails:**
- `app/models/user.rb` -> check `spec/models/user_spec.rb` or `test/models/user_test.rb`
- `app/controllers/users_controller.rb` -> check `spec/controllers/` or `spec/requests/`
- `app/services/*.rb` -> check `spec/services/*_spec.rb`

**Python:**
- `src/module.py` -> check `tests/test_module.py`
- `app/services/auth.py` -> check `tests/services/test_auth.py` or `tests/test_auth.py`

**JavaScript/TypeScript:**
- `src/utils/format.ts` -> check `src/utils/__tests__/format.test.ts`, `src/utils/format.test.ts`, or `src/utils/format.spec.ts`
- `src/components/Button.tsx` -> check `src/components/__tests__/Button.test.tsx`

**PHP:**
- `app/Http/Controllers/UserController.php` -> check `tests/Feature/UserControllerTest.php`
- `app/Services/PaymentService.php` -> check `tests/Unit/PaymentServiceTest.php`

**Go:**
- `internal/auth/token.go` -> check `internal/auth/token_test.go`

### Step 4: Read each untested source file

For each file missing tests:
1. Read the source file
2. Identify all public functions, methods, and classes
3. Understand the dependencies and imports

### Step 5: Generate tests

For each public function/method, generate:
- **Happy path test** - expected inputs produce expected outputs
- **Edge case tests** - nil/null, empty, zero, boundary values
- **Error case tests** - invalid inputs, expected exceptions
- Use the project's existing test patterns (check existing test files for style)

### Step 6: Output

For each file, show:

```
## Test Coverage Report

### Files missing tests: N
### Files with partial coverage: N
### Fully tested files: N (skipped)

---

### Generated: <test_file_path>
**Source**: <source_file_path>
**Functions tested**: <list>

<generated test code>

---
```

Write each test file after showing it. Ask the user before writing if there are more than 5 files.

## Example Usage

```
/generate-tests
/generate-tests app/models/user.rb
/generate-tests src/utils/
/generate-tests internal/auth/token.go
```
