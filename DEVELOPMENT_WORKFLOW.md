# Development Workflow Guide

A practical guide for working on KIM Centroid Generator. Keep it simple, stay organized.

## Branch Strategy

### Branch Naming

Use descriptive, lowercase names with hyphens:

```
feature/interactive-structure-selection
fix/dicom-permission-error
docs/update-user-guide
test/add-centroid-validation
```

**Format:** `type/short-description`

**Types:**
- `feature/` - New functionality
- `fix/` - Bug fixes
- `docs/` - Documentation only
- `test/` - Adding or updating tests
- `refactor/` - Code cleanup (no behavior change)

### Working with Branches

```bash
# Create a new branch from main
git checkout main
git pull origin main
git checkout -b feature/your-feature-name

# Make changes, commit, push
git add .
git commit -m "Add your feature"
git push -u origin feature/your-feature-name
```

## Commit Messages

Keep them simple and descriptive:

**Good:**
- `Add interactive mode for custom structure selection`
- `Fix permission error when reading DICOM files`
- `Update user guide with installation steps`

**Not so good:**
- `fix` (too vague)
- `asdfasdf` (not descriptive)
- `Updated files and stuff` (unclear)

### Format

```
Short summary (50 chars or less)

Optional longer explanation if needed:
- What changed
- Why it changed
- Any important details
```

## Pull Request Process

### 1. Create the PR

```bash
# Via GitHub CLI
gh pr create --base main --title "Your PR title"

# Or via GitHub web interface
# Go to your branch and click "Compare & pull request"
```

### 2. PR Requirements

Before your PR can be merged:
- ✅ All tests must pass (automated CI check)
- ✅ One team member must approve
- ✅ CHANGELOG.md must be updated (see below)
- ✅ No merge conflicts with main

### 3. Review Process

1. **Request a reviewer** - Tag someone familiar with the code
2. **Address feedback** - Make requested changes in new commits
3. **Update if needed** - Respond to review comments
4. **Merge** - Reviewer or you can merge after approval

### 4. After Merge

```bash
# Clean up your local branches
git checkout main
git pull origin main
git branch -d feature/your-old-branch
```

## Version Tagging

We use **date-based versioning**: `vYYYY.MM.DD`

### Creating a Release

1. **Update CHANGELOG.md** - Move "Unreleased" items to new version section
2. **Create and push tag:**

```bash
# Create tag with today's date
git tag v2025.01.15 -m "Release January 15, 2025"
git push origin v2025.01.15
```

3. **Automated build** - GitHub Actions will automatically build and attach the Windows executable

### Version Examples

- `v2025.01.15` - Release on January 15, 2025
- `v2025.02.28` - Release on February 28, 2025
- `v2025.12.01` - Release on December 1, 2025

**Note:** If multiple releases on the same day, append `.1`, `.2`, etc: `v2025.01.15.1`

## Code Review Guidelines

### For Authors

- Keep PRs small and focused (one feature/fix)
- Test your code before requesting review
- Provide context in the PR description
- Be responsive to feedback

### For Reviewers

- Review promptly (within 1-2 days)
- Be constructive and specific
- Ask questions if unclear
- Approve when satisfied

## Common Workflows

### Adding a New Feature

```bash
# 1. Create feature branch
git checkout -b feature/my-feature

# 2. Make changes and test
# ... code changes ...
pytest tests/

# 3. Commit
git add .
git commit -m "Add my feature"

# 4. Push and create PR
git push -u origin feature/my-feature
gh pr create --base main
```

### Fixing a Bug

```bash
# 1. Create fix branch
git checkout -b fix/bug-description

# 2. Fix and test
# ... fix the bug ...
pytest tests/

# 3. Commit with clear message
git commit -m "Fix DICOM file permission error

Added retry logic with timeout to handle files still being written"

# 4. Create PR
git push -u origin fix/bug-description
gh pr create --base main
```

### Updating Documentation

```bash
# Documentation changes follow same process
git checkout -b docs/update-readme
# ... make changes ...
git commit -m "Update README with new installation instructions"
git push -u origin docs/update-readme
gh pr create --base main
```

## Tips for Success

1. **Pull often** - Keep your branch up to date with main
2. **Commit often** - Small commits are easier to review
3. **Test locally** - Don't rely only on CI
4. **Ask questions** - Better to ask than guess
5. **Keep it simple** - Don't over-engineer

## Getting Help

- Check [CONTRIBUTING.md](CONTRIBUTING.md) for setup and basics
- Check [TEST_PLAN.md](TEST_PLAN.md) for testing guidance
- Ask in PR comments or team chat

---

*These are guidelines, not strict rules. Adapt as needed, but be consistent.*
