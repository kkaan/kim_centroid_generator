# Changelog

All notable changes to KIM Centroid Generator will be documented here.

Version format: `vYYYY.MM.DD` (date-based)

## [Unreleased]

### Added
- Development workflow documentation (DEVELOPMENT_WORKFLOW.md)
- Contributing guidelines (CONTRIBUTING.md)
- Automated CI/CD with GitHub Actions
- Basic smoke tests for core functionality
- Branch protection requirements (PR + 1 reviewer + CI passing)

### Testing
- Workflow infrastructure validation

---

## [v2025.01.12] - 2025-01-12

### Added
- Interactive mode for custom structure selection when default structures not found
- User can select specific structures by number, "all", or "skip"
- Actual DICOM structure names preserved in output (properly formatted)
- Command-line `--interactive` flag to enable/disable interactive mode
- Startup prompt to configure interactive mode
- Comprehensive test plan documentation (TEST_PLAN.md)
- Detailed user guide with screenshots (docs/USER_GUIDE.md)
- Project documentation for AI assistants (CLAUDE.md)
- File readiness checking with timeout to handle files being copied

### Changed
- Output format now uses actual structure names instead of generic labels
- Enhanced error handling for DICOM file access
- Updated PyInstaller spec for better executable builds

### Validated
- Baseline vs interactive mode outputs produce identical centroid calculations
- KIM system compatibility confirmed (reads output files without errors)
- Backward compatibility maintained (non-interactive mode unchanged)

---

## How to Update This File

When making changes:

1. **Add to "Unreleased" section** - Document your changes under the appropriate category:
   - **Added**: New features
   - **Changed**: Changes to existing functionality
   - **Deprecated**: Soon-to-be removed features
   - **Removed**: Removed features
   - **Fixed**: Bug fixes
   - **Security**: Security fixes

2. **On release** - Move "Unreleased" items to a new version section:
   ```markdown
   ## [vYYYY.MM.DD] - YYYY-MM-DD

   (move unreleased items here)
   ```

3. **Keep it concise** - Users scan this quickly. Be clear but brief.

---

## Template for New Release

```markdown
## [vYYYY.MM.DD] - YYYY-MM-DD

### Added
- New feature 1
- New feature 2

### Changed
- Updated behavior of X

### Fixed
- Fixed bug in Y
```
