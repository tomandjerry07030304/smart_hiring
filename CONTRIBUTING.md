# Contributing to Smart Hiring System

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to the Smart Hiring System.

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Commit Messages](#commit-messages)
- [Pull Request Process](#pull-request-process)
- [Testing](#testing)
- [Reporting Issues](#reporting-issues)

---

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment. Be kind, constructive, and professional in all interactions.

---

## Getting Started

1. **Fork** the repository on GitHub
2. **Clone** your fork locally:
   ```bash
   git clone https://github.com/your-username/smart-hiring.git
   cd smart-hiring
   ```
3. **Set up** the development environment (see [README.md](README.md#getting-started))
4. **Create a branch** for your work:
   ```bash
   git checkout -b feature/your-feature-name
   ```

---

## Development Workflow

1. Keep your fork up to date with the upstream `main` branch
2. Work in a feature branch — never commit directly to `main`
3. Make small, focused commits with clear messages
4. Test your changes before submitting a pull request
5. Ensure all existing tests still pass

### Branch Naming

| Type | Pattern | Example |
|------|---------|---------|
| Feature | `feature/description` | `feature/linkedin-oauth` |
| Bug fix | `fix/description` | `fix/resume-parsing-error` |
| Hotfix | `hotfix/description` | `hotfix/jwt-token-expiry` |
| Documentation | `docs/description` | `docs/api-reference-update` |
| Refactor | `refactor/description` | `refactor/scoring-engine` |

---

## Coding Standards

### Python (Backend)

- Follow **PEP 8** style guide
- Use **type hints** for function signatures
- Write **docstrings** for all public functions and classes
- Keep functions focused — single responsibility principle
- Use meaningful variable and function names
- Maximum line length: **120 characters**

```python
def calculate_match_score(candidate: dict, job: dict) -> float:
    """
    Calculate the match score between a candidate and a job posting.

    Args:
        candidate: Candidate profile dictionary with skills and experience.
        job: Job posting dictionary with requirements.

    Returns:
        Match score between 0.0 and 1.0.
    """
    ...
```

### JavaScript (Frontend)

- Use **ES6+** syntax (const/let, arrow functions, template literals)
- Follow consistent naming: `camelCase` for variables/functions, `PascalCase` for classes
- Add JSDoc comments for public functions
- Handle errors gracefully — always catch fetch/API errors

### HTML/CSS

- Use semantic HTML elements
- Follow BEM naming convention for CSS classes where applicable
- Ensure accessibility (ARIA attributes, keyboard navigation, color contrast)

---

## Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) format:

```
<type>(<scope>): <short description>

[optional body]

[optional footer]
```

### Types

| Type | Usage |
|------|-------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation changes |
| `style` | Code formatting (no logic change) |
| `refactor` | Code restructuring (no feature/fix) |
| `test` | Adding or updating tests |
| `chore` | Build scripts, CI, dependency updates |
| `perf` | Performance improvement |
| `security` | Security fix or improvement |

### Examples

```
feat(auth): add LinkedIn OAuth integration
fix(resume): handle malformed PDF uploads gracefully
docs(api): update candidate endpoint documentation
test(fairness): add demographic parity threshold tests
```

---

## Pull Request Process

1. **Update your branch** with the latest `main`:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Run all tests** and ensure they pass:
   ```bash
   pytest
   ```

3. **Push** your branch and open a Pull Request on GitHub

4. **In the PR description**, include:
   - What the change does and why
   - Any breaking changes
   - Screenshots (if UI changes)
   - Related issue numbers

5. **Wait for review** — at least one approval is required before merging

6. **Address feedback** promptly and push updates to the same branch

### PR Checklist

- [ ] Code follows the project's coding standards
- [ ] All tests pass locally
- [ ] New features include appropriate tests
- [ ] Documentation is updated if needed
- [ ] No sensitive data (API keys, credentials) in the code
- [ ] Changes are backward-compatible (or breaking changes are documented)

---

## Testing

### Running Tests

```bash
# All tests
pytest

# Specific test file
pytest tests/test_api.py

# With coverage report
pytest --cov=backend --cov-report=html

# Backend unit tests only
pytest backend/tests/
```

### Writing Tests

- Place test files in `tests/` (integration) or `backend/tests/` (unit)
- Name test files `test_*.py`
- Name test functions `test_<description>()`
- Use fixtures for common setup/teardown
- Test both happy paths and error cases

---

## Reporting Issues

### Bug Reports

When filing a bug report, include:

1. **Summary** — Brief description of the issue
2. **Steps to Reproduce** — Exact steps to trigger the bug
3. **Expected Behavior** — What should happen
4. **Actual Behavior** — What actually happens
5. **Environment** — OS, Python version, browser (if frontend)
6. **Logs/Screenshots** — Any relevant output or error messages

### Feature Requests

When suggesting a feature:

1. **Problem** — What problem does this solve?
2. **Proposed Solution** — How should it work?
3. **Alternatives** — Other approaches you've considered
4. **Impact** — Who benefits from this feature?

---

## Security Vulnerabilities

**Do NOT open a public issue for security vulnerabilities.**

Please refer to [docs/SECURITY.md](docs/SECURITY.md) for responsible disclosure instructions.

---

## Questions?

If you have questions about contributing, open a [GitHub Discussion](https://github.com/your-org/smart-hiring/discussions) or contact the maintainers.

Thank you for helping make Smart Hiring better!
