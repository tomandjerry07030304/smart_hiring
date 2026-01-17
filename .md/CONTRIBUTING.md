# Contributing to Smart Hiring System

Thank you for considering contributing! 🎉

## Quick Start

1. Fork the repo
2. Create a branch: `git checkout -b feature/your-feature`
3. Make changes
4. Test locally
5. Commit: `git commit -m "Add: your feature"`
6. Push: `git push origin feature/your-feature`
7. Open Pull Request

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/my-project-s1.git

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup MongoDB (local or Atlas)
# Copy .env.example to .env and configure

# Run tests
pytest

# Run locally
python app.py
```

## Code Style

- Follow PEP 8
- Use meaningful variable names
- Add comments for complex logic
- Write docstrings for functions

## Commit Messages

Format: `Type: Description`

Types:
- `Add:` New feature
- `Fix:` Bug fix
- `Update:` Changes to existing feature
- `Remove:` Removed feature
- `Docs:` Documentation only
- `Style:` Formatting, no code change
- `Refactor:` Code restructure
- `Test:` Adding tests
- `Chore:` Maintenance

Examples:
```
Add: AI interviewer integration
Fix: Job posting error for company role
Update: Improved matching algorithm
Docs: API documentation update
```

## Testing

- Write tests for new features
- Ensure existing tests pass
- Test on multiple browsers (if frontend)

## Pull Request Process

1. Update README.md if needed
2. Update CHANGELOG.md
3. Ensure code follows style guide
4. Describe changes in PR description
5. Link related issues

## What We're Looking For

**High Priority:**
- AI Interviewer integration
- Email notifications
- Better error handling
- Mobile responsiveness
- Test coverage

**Medium Priority:**
- UI/UX improvements
- Performance optimization
- Documentation
- Accessibility

**Nice to Have:**
- Dark mode
- Internationalization
- Advanced features

## Questions?

Open an issue or discussion on GitHub!

Thank you for contributing! 🙏
