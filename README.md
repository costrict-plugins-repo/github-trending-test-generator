# test-generator

A Claude Code plugin that auto-generates test files when you write new code. Detects your test framework, scaffolds tests with edge cases, and reminds you when source files lack coverage.

## What It Does

- Detects your test framework (RSpec, pytest, Jest, Vitest, PHPUnit, Go testing, ExUnit, Rust)
- Maps source files to the correct test file paths
- Generates tests covering happy path, edge cases, and error cases
- PostToolUse hook reminds you when edited files don't have tests
- Matches your project's existing test style and conventions

## Installation

```
claude plugin install test-generator
```

## Usage

### Slash Command

```
/generate-tests                          # Scan entire project
/generate-tests app/models/user.rb       # Generate tests for one file
/generate-tests src/utils/               # Generate tests for a directory
```

### Automatic Reminders (Hook)

After you edit a source file without a corresponding test file, the plugin prints:

```
No test file found for user.rb.
Expected test at: spec/models/user_spec.rb
Run /generate-tests app/models/user.rb to create one.
```

Disable with:
```
DISABLE_TEST_REMINDER=1
```

### Skill (Auto-Activated)

The `auto-test` skill activates when you:
- Create a new source file
- Add new public methods
- Ask about testing or mention TDD/coverage

### Agent

The `test-writer` agent does deep analysis - reads existing tests for style, understands dependencies, mocks external services, and generates comprehensive test suites.

## Supported Frameworks

| Language | Frameworks | Test Path Convention |
|---|---|---|
| Ruby | RSpec, Minitest | `spec/**/*_spec.rb`, `test/**/*_test.rb` |
| Python | pytest, unittest | `tests/test_*.py` |
| JS/TS | Jest, Vitest, Mocha | `__tests__/*.test.ts`, `*.spec.ts` |
| PHP | PHPUnit | `tests/Unit/*Test.php`, `tests/Feature/*Test.php` |
| Go | testing, testify | `*_test.go` (same directory) |
| Elixir | ExUnit | `test/*_test.exs` |
| Rust | cargo test | `#[cfg(test)]` inline or `tests/*.rs` |

## Test Quality

Generated tests follow these principles:
- One behavior per test
- Descriptive names: `it "returns nil when user not found"`
- Arrange-Act-Assert pattern
- Minimal setup, no shared mutable state
- Real objects over mocks when possible
- Mocks for external services (APIs, email, file system)
- Uses factories/fixtures matching your project conventions

## Examples

### Ruby/RSpec - Model test

Source: `app/models/user.rb`
```ruby
class User < ApplicationRecord
  def full_name
    "#{first_name} #{last_name}"
  end

  def active?
    !deactivated_at
  end
end
```

Generated: `spec/models/user_spec.rb`
```ruby
require "rails_helper"

RSpec.describe User do
  describe "#full_name" do
    it "combines first and last name" do
      user = build(:user, first_name: "Jane", last_name: "Doe")
      expect(user.full_name).to eq("Jane Doe")
    end

    it "handles nil first name" do
      user = build(:user, first_name: nil, last_name: "Doe")
      expect(user.full_name).to eq(" Doe")
    end
  end

  describe "#active?" do
    it "returns true when not deactivated" do
      user = build(:user, deactivated_at: nil)
      expect(user).to be_active
    end

    it "returns false when deactivated" do
      user = build(:user, deactivated_at: Time.current)
      expect(user).not_to be_active
    end
  end
end
```

### Python/pytest - Service test

Source: `src/services/auth.py`
```python
def authenticate(email, password):
    user = User.find_by_email(email)
    if not user:
        raise UserNotFoundError(email)
    if not user.verify_password(password):
        raise InvalidPasswordError()
    return create_token(user)
```

Generated: `tests/test_auth.py`
```python
import pytest
from unittest.mock import patch, MagicMock
from src.services.auth import authenticate, UserNotFoundError, InvalidPasswordError

class TestAuthenticate:
    def test_returns_token_for_valid_credentials(self):
        user = MagicMock()
        user.verify_password.return_value = True
        with patch("src.services.auth.User") as MockUser:
            MockUser.find_by_email.return_value = user
            token = authenticate("a@b.com", "pass123")
            assert token is not None

    def test_raises_when_user_not_found(self):
        with patch("src.services.auth.User") as MockUser:
            MockUser.find_by_email.return_value = None
            with pytest.raises(UserNotFoundError):
                authenticate("missing@b.com", "pass")

    def test_raises_when_password_invalid(self):
        user = MagicMock()
        user.verify_password.return_value = False
        with patch("src.services.auth.User") as MockUser:
            MockUser.find_by_email.return_value = user
            with pytest.raises(InvalidPasswordError):
                authenticate("a@b.com", "wrong")
```

## License

MIT
