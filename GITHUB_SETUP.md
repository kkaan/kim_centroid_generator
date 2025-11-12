# GitHub Repository Setup Guide

This guide walks you through setting up branch protection and other repository settings for the KIM Centroid Generator project.

## Branch Protection Rules

Branch protection ensures code quality by requiring PRs, reviews, and passing tests before merging to `main`.

### Setting Up Main Branch Protection

1. **Go to Repository Settings**
   - Navigate to https://github.com/kkaan/kim_centroid_generator
   - Click **Settings** tab (top right)

2. **Access Branch Protection Rules**
   - In left sidebar, click **Branches** (under "Code and automation")
   - Click **Add branch protection rule** button

3. **Configure Protection Rule**

   **Branch name pattern:**
   ```
   main
   ```

   **Enable these settings:**
   - ✅ **Require a pull request before merging**
     - ✅ Require approvals: **1**
     - ✅ Dismiss stale pull request approvals when new commits are pushed

   - ✅ **Require status checks to pass before merging**
     - ✅ Require branches to be up to date before merging
     - Search for and select: **test** (this is the CI job from tests.yml)

   - ✅ **Do not allow bypassing the above settings**

   - ✅ **Restrict who can push to matching branches**
     - Add: Maintainers only (or specific team members)

4. **Click "Create"** to save the rule

### What This Does

- **No direct commits to main** - All changes must go through a PR
- **One approval required** - At least one team member must review and approve
- **Tests must pass** - GitHub Actions CI must complete successfully
- **Branch must be up to date** - Must merge latest main before PR can be merged

## Repository Settings

### General Settings

1. **Go to Settings > General**

2. **Pull Requests Section:**
   - ✅ Allow squash merging (optional - good for clean history)
   - ✅ Automatically delete head branches (cleans up merged branches)

### Actions Settings

1. **Go to Settings > Actions > General**

2. **Actions permissions:**
   - Select: **Allow all actions and reusable workflows**

3. **Workflow permissions:**
   - Select: **Read and write permissions**
   - ✅ Allow GitHub Actions to create and approve pull requests

This allows the build workflow to create releases.

## Collaborators and Teams

### Adding Team Members

1. **Go to Settings > Collaborators and teams**

2. **Click "Add people"**
   - Enter GitHub username or email
   - Select role:
     - **Write**: Can push to branches, create PRs, approve PRs
     - **Maintain**: Write access + manage settings
     - **Admin**: Full access

3. Team members will receive an email invitation

### Recommended Roles

- **Research scientists**: Write access
- **Lead developer**: Maintain access
- **Project owner**: Admin access

## Repository Visibility

Currently: **Private** (recommended for medical software under development)

To change visibility:
1. Settings > General > Danger Zone
2. Change repository visibility
3. **Note**: Be careful with medical/patient data - keep private unless data is anonymized

## Setting Up GitHub Pages (Optional)

If you want to host documentation:

1. **Go to Settings > Pages**
2. **Source**: Deploy from a branch
3. **Branch**: Select `main` and `/docs` folder
4. **Save**

Documentation will be available at: `https://kkaan.github.io/kim_centroid_generator/`

## Issue Templates (Optional)

To standardize bug reports and feature requests:

1. **Go to Settings > Features**
2. **Issues section**: Click "Set up templates"
3. Add **Bug Report** and **Feature Request** templates
4. Customize templates in `.github/ISSUE_TEMPLATE/`

## Testing Your Setup

### Test Branch Protection

1. Try to push directly to main:
   ```bash
   git checkout main
   # Make a change
   git commit -m "Test direct push"
   git push origin main
   ```
   **Expected**: Push should be rejected

2. Create a PR without tests passing:
   - Create a branch, make a change, create PR
   - If tests fail, merge button should be disabled

3. Create a PR without review:
   - Even with passing tests, merge should require approval

### Test CI/CD

1. **Test CI on PR:**
   - Create a feature branch
   - Push changes
   - Create PR to main
   - Check "Actions" tab to see tests running

2. **Test Release Build:**
   - Create a version tag: `git tag v2025.01.15 -m "Test release"`
   - Push tag: `git push origin v2025.01.15`
   - Check "Actions" tab - build workflow should trigger
   - Check "Releases" - new release should be created with executable

## Troubleshooting

### "Status checks not found"

If you don't see the **test** status check when setting up branch protection:
1. Create a PR first to trigger the workflow
2. After workflow runs once, the status check will appear in the list
3. Then you can require it in branch protection

### "Actions not running"

If GitHub Actions aren't triggering:
1. Check Settings > Actions > General
2. Ensure Actions are enabled
3. Check workflow files are in `.github/workflows/`
4. Check workflow syntax with `yamllint` or GitHub's validator

### "Can't merge PR"

If you can't merge even with approvals and passing tests:
1. Check if branch is up to date with main
2. Ensure all required status checks are passing (green checkmarks)
3. Verify you have merge permissions

## Quick Reference

**Repository URL:** https://github.com/kkaan/kim_centroid_generator

**Main branch protection:**
- Require PR: ✅
- Require 1 approval: ✅
- Require tests passing: ✅
- No direct pushes: ✅

**GitHub Actions:**
- Tests on PR: ✅ (`.github/workflows/tests.yml`)
- Build on tag: ✅ (`.github/workflows/build.yml`)

---

*Complete these steps once, then the team can follow the development workflow in [DEVELOPMENT_WORKFLOW.md](DEVELOPMENT_WORKFLOW.md)*
