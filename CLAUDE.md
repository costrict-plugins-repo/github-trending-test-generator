# Test Generator

You have the test-generator plugin active. Follow these rules whenever the user writes new code, asks for tests, or works on files that lack test coverage.

## Framework Detection

Detect the test framework from the project structure:

### Ruby / Rails
- **RSpec**: `spec/` directory, `Gemfile` contains `rspec`
- **Minitest**: `test/` directory, `Gemfile` contains `minitest`
- Test path: `spec/{type}/{name}_spec.rb` or `test/{type}/{name}_test.rb`

### Python
- **pytest**: `conftest.py` exists, `requirements.txt` or `pyproject.toml` contains `pytest`
- **unittest**: `test_*.py` files with `import unittest`
- Test path: `tests/test_{name}.py` or `test_{name}.py`

### JavaScript / TypeScript
- **Jest**: `jest.config.*` exists, `package.json` contains `jest`
- **Vitest**: `vitest.config.*` exists, `package.json` contains `vitest`
- **Mocha**: `.mocharc.*` exists, `package.json` contains `mocha`
- Test path: `__tests__/{name}.test.{js,ts}` or `{name}.test.{js,ts}` or `{name}.spec.{js,ts}`

### PHP
- **PHPUnit**: `phpunit.xml` exists, `composer.json` contains `phpunit`
- Test path: `tests/{Type}/{Name}Test.php`

### Go
- **testing**: Built-in, no config needed
- Test path: `{name}_test.go` (same directory)

### Elixir
- **ExUnit**: `test/` directory, `mix.exs` present
- Test path: `test/{name}_test.exs`

### Rust
- **cargo test**: Built-in, inline `#[cfg(test)]` modules or `tests/` directory
- Test path: inline `mod tests` block or `tests/{name}.rs`

## Test Generation Rules

### What to test

For each public function/method/class, generate tests covering:

1. **Happy path** - Normal expected inputs and outputs
2. **Edge cases** - Empty inputs, nil/null, zero, empty strings, boundary values
3. **Error cases** - Invalid inputs, exceptions, error responses
4. **Return values** - Verify correct types and values

### What NOT to test

- Private methods (test them through public interfaces)
- Framework internals (don't test Rails' `has_many` works)
- Trivial getters/setters with no logic
- Third-party library behavior

### Test quality rules

- Each test should test ONE behavior
- Test names should describe the behavior, not the method: `it "returns nil when user not found"` not `it "tests find_user"`
- Use descriptive context blocks: `describe "#find" do; context "when user exists" do`
- Prefer real objects over mocks when possible
- Mock external services (APIs, email, file system)
- Use factories/fixtures for test data, not raw creation
- Tests must be independent - no shared mutable state
- Keep setup minimal - only create what the test needs

### Framework-specific patterns

**RSpec (Ruby)**:
- Use `let` for lazy-loaded test data
- Use `described_class` instead of hardcoding class names
- Use `before` blocks sparingly
- Use `shared_examples` for common behavior
- Use `have_attributes` matcher for object comparison
- Rails: use `FactoryBot` if present, `fixtures` otherwise

**pytest (Python)**:
- Use `@pytest.fixture` for test data
- Use `parametrize` for testing multiple inputs
- Use `pytest.raises` for exception testing
- Use `monkeypatch` or `unittest.mock.patch` for mocking
- Use `conftest.py` for shared fixtures

**Jest / Vitest (JS/TS)**:
- Use `describe` / `it` blocks
- Use `beforeEach` for per-test setup
- Use `jest.mock()` / `vi.mock()` for module mocking
- Use `toEqual` for deep comparison, `toBe` for primitives
- Test async code with `async/await`

**PHPUnit (PHP)**:
- Use `setUp()` for test initialization
- Use `@dataProvider` for parameterized tests
- Use `$this->expectException()` for error testing
- Use `createMock()` for mocking

**Go testing**:
- Use table-driven tests with `[]struct` slices
- Use `t.Run()` for subtests
- Use `t.Helper()` in test helpers
- Use `testify` if present, otherwise standard `testing`

## File mapping

When generating tests, map source files to test files:

| Source | Test File |
|---|---|
| `app/models/user.rb` | `spec/models/user_spec.rb` |
| `app/services/payment_service.rb` | `spec/services/payment_service_spec.rb` |
| `src/utils/format.ts` | `src/utils/__tests__/format.test.ts` or `src/utils/format.test.ts` |
| `app/Http/Controllers/UserController.php` | `tests/Feature/UserControllerTest.php` |
| `internal/auth/token.go` | `internal/auth/token_test.go` |
| `lib/my_app/accounts.ex` | `test/my_app/accounts_test.exs` |
| `src/services/auth.py` | `tests/test_auth.py` |

## Behavior

When the user writes or modifies a source file:
1. Check if a corresponding test file exists
2. If no test file exists, offer to generate one
3. If a test file exists but doesn't cover the new/changed code, suggest additions
4. Always show the generated tests before writing them
