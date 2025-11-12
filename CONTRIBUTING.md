# Contributing to KIM Centroid Generator

Thank you for contributing! This guide will get you started quickly.

## Quick Start

1. **Clone** the repository
2. **Create a branch** for your changes (see [workflow guide](DEVELOPMENT_WORKFLOW.md))
3. **Make your changes** following existing code style
4. **Test your changes** (see Testing section below)
5. **Submit a pull request** to the `main` branch

## Development Setup

```bash
# Clone the repository
git clone https://github.com/kkaan/kim_centroid_generator.git
cd kim_centroid_generator

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # For testing
```

## Testing

Run tests before submitting a PR:

```bash
pytest tests/
```

Your code should:
- Pass all existing tests
- Include new tests for new features
- Not break existing functionality

## Code Style

- Follow the existing code patterns in the project
- Use clear, descriptive variable names
- Add comments for complex logic
- Keep functions focused and reasonably sized

## Pull Request Process

1. **Ensure tests pass** - CI must be green
2. **Request one reviewer** - Tag a team member
3. **Address feedback** - Make requested changes
4. **Keep it focused** - One feature/fix per PR
5. **Update CHANGELOG.md** - Add entry under "Unreleased"

### PR Checklist

- [ ] Tests pass locally (`pytest tests/`)
- [ ] Code follows existing style
- [ ] CHANGELOG.md updated
- [ ] Commit messages are clear
- [ ] One approval received

## External Contributors

If you're **not** part of the team (no write access to the repository):

1. **Fork** the repository to your GitHub account
2. **Clone your fork** instead of the main repository
3. Follow the same workflow as above
4. When creating PR, it will be from your fork to the main repository

## Reporting Issues

When reporting bugs, include:
- Python version and OS
- Steps to reproduce
- Expected vs actual behavior
- Sample DICOM files (if applicable and safe to share)

## Questions?

Check the [Development Workflow Guide](DEVELOPMENT_WORKFLOW.md) or ask in the PR discussion.

---

*Keep it simple. We're all learning together.*
