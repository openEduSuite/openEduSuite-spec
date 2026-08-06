<!--
SPDX-FileCopyrightText: 2026 openDesk Edu Contributors
SPDX-License-Identifier: Apache-2.0
-->

# How to Use This OpenSpec Change Proposal

This document explains how to navigate and use the Nix Integration change proposal following the OpenSpec methodology.

---

## OpenSpec Methodology Overview

The OpenSpec methodology (from [Fission AI](https://fission.codes/openspec)) uses three key directories:

```
openspec/
├── specs/          ← Source of truth: behavioral contracts (SHALL/MUST/SHOULD)
├── changes/        ← Active change proposals (delta specs: ADDED/MODIFIED/REMOVED)
└── archive/        ← Completed changes (decision log: why, what, how)
```

**This change proposal lives in `changes/nix-integration-proposal/`**

---

## Document Structure

```
changes/nix-integration-proposal/
├── README.md           # 📌 This file - Quick overview and navigation
├── HOW-TO-USE.md       # 📖 This file - How to use the proposal
├── proposal.md         # 📋 The "why" - Motivation, goals, scope, impact
├── specs.md            # 📜 The "what" - Delta specs (ADDED/MODIFIED/REMOVED)
└── tasks.md            # 🎯 The "how" - Actionable implementation tasks
```

**Plus the full specification:**
```
specs/platform/nix-integration/index.md  # 📚 Complete technical specification
```

---

## When to Use Each Document

### 🎯 You're a **Decision Maker** (Team Lead, Architecture, Security, Ops)

**Start here:**
```
→ Start with: README.md
   
→ For motivation: proposal.md
   - Read: Abstract, Motivation, Goals, Scope
   - Check: Impact Assessment, Risk Assessment
   - Review: Acceptance Criteria
   
→ To approve: proposal.md#approval
   - Add your approval to the table
```

**Time required:** 30-60 minutes

---

### 👨‍💻 You're a **Developer**

**Start here:**
```
→ Start with: README.md
   
→ For understanding: proposal.md
   - Read: Scope, Architecture, Requirements
   
→ For implementation: tasks.md
   - Find tasks assigned to you
   - Check dependencies
   - Update status as you work
   
→ For details: specs.md
   - See what files will be ADDED/MODIFIED/REMOVED
   - Check the validation mapping
   
→ For technical specs: specs/platform/nix-integration/index.md
   - Complete technical details
   - File structure, interfaces, schemas
```

**Time required:** Varies by task

---

### 🔍 You're a **Reviewer**

**Start here:**
```
→ Start with: README.md
   
→ For technical review: proposal.md
   - Focus: Architecture, Requirements, Dependencies
   
→ For delta review: specs.md
   - Check: ADDED/MODIFIED/REMOVED sections
   - Verify: Each change maps to acceptance criteria
   
→ For implementation review: tasks.md
   - Check: Task breakdown is complete
   - Verify: Dependencies are correct
   - Review: Effort estimates are reasonable
```

**Time required:** 60-120 minutes

---

## Reading Order Recommendations

### Quick Overview (5 minutes)

1. **README.md** - Get the big picture
2. **proposal.md** - Read Abstract and Goals
3. **Stop** - You now understand what's being proposed

### Full Review (30-60 minutes)

1. **README.md** - Overview
2. **proposal.md** - Complete proposal
   - Motivation & Problems
   - Goals & Non-Goals
   - Scope
   - Architecture
   - Requirements
   - Migration Phases
   - Risks
3. **specs.md** - What will change
4. **Stop** - You now understand the what and why

### Implementation Planning (60+ minutes)

1. **All of the above**
2. **tasks.md** - How it will be implemented
   - Task organization
   - Dependencies
   - Parallelization
   - Quality gates
3. **specs/platform/nix-integration/index.md** - Technical details
4. **Stop** - You're ready to start implementation

---

## Understanding the Delta Spec (specs.md)

The delta spec uses **ADDED**, **MODIFIED**, and **REMOVED** sections to clearly define what will change:

### ADDED
```markdown
- `opendesk-nix/flake.nix` — Root flake
  - Purpose: Entry point for the Nix build system
  - Spec: [link to technical spec]
```

**Interpretation:** This file will be created. It's the entry point for the build system.

### MODIFIED
```markdown
- `opendesk-edu/nix/lib/k8s.nix` — MOVE to `opendesk-nix/lib/k8s.nix`
  - Reason: Consolidate all Nix code
  - Changes: May be updated to match new requirements
```

**Interpretation:** This existing file will be moved and possibly updated.

### REMOVED
```markdown
- `opendesk-edu/nix/` — DEPRECATE in favor of `opendesk-nix/`
  - Reason: All Nix code moved to opendesk-nix
  - Timeline: After Phase 8
```

**Interpretation:** This directory will eventually be removed.

### Validation Mapping

Each change maps to acceptance criteria:

| Delta Spec | Acceptance Criteria | Spec Section |
|------------|---------------------|--------------|
| Added flake.nix | AC-001, AC-002 | [link] |

**Interpretation:** Adding flake.nix helps satisfy AC-001 and AC-002.

---

## Using the Task List (tasks.md)

### Task Format

```markdown
| Task ID | Task | Priority | Effort | Dependencies | Assignee | Status |
|---------|------|----------|--------|--------------|----------|--------|
| T1.1.01 | Create k8s.nix library | P0 | M | Phase 0 | @developer | ⏳ |
```

### Task ID Format

- `T<phase>.<wave>.<sequence>`
- Example: `T1.1.01` = Phase 1, Wave 1, Task 1
- **Benefit:** Easy to track which phase a task belongs to

### Priority Levels

| Priority | Meaning | Icon |
|----------|---------|------|
| P0 | Critical - Must be done | ⭐⭐⭐ |
| P1 | High - Should be done | ⭐⭐ |
| P2 | Medium - Nice to have | ⭐ |
| P3 | Low - Can be deferred | (none) |

### Effort Estimates

| Effort | Hours | Description |
|--------|-------|-------------|
| S | <4h | Small task |
| M | 4-8h | Medium task |
| L | 8-16h | Large task |
| XL | 16-32h | Extra large task |
| XXL | 32+h | Very large task |

### Status Values

| Status | Meaning | Action |
|--------|---------|--------|
| ⏳ Not Started | Task hasn't begun | Ready to pick up |
| 🔄 In Progress | Task is being worked on | None |
| ✅ Done | Task is complete and verified | None |
| ❌ Blocked | Task cannot proceed | Resolve blockers |
| 🚧 Needs Review | Task needs review | Review and approve |

---

## Implementation Workflow

### 1. Pick a Task

```bash
# Find tasks assigned to you
cd openEduSuite-spec/changes/nix-integration-proposal
grep "YourName" tasks.md

# Or find unassigned P0 tasks
grep "⏳" tasks.md | grep "P0"
```

### 2. Understand the Task

- Read the task description in `tasks.md`
- Check dependencies - are they done?
- If dependencies are not done, pick a different task
- Read related sections in `specs.md` - what files are being changed?
- Read technical details in `specs/platform/nix-integration/index.md`

### 3. Implement the Task

- Follow the task description
- Implement the changes described in `specs.md`
- Follow the technical specifications
- Write tests if applicable
- Update documentation if applicable

### 4. Update Task Status

```markdown
# Change from:
| T1.1.01 | ... | @YourName | ⏳ |

# To:
| T1.1.01 | ... | @YourName | 🚧 |
```

Request a review from a team member.

### 5. Code Review

- Reviewer checks the implementation against:
  - Task description in `tasks.md`
  - Delta specs in `specs.md`
  - Technical specs in `specs/platform/nix-integration/index.md`
  - Acceptance criteria in `proposal.md`

- If approved:
  ```markdown
  | T1.1.01 | ... | @YourName | ✅ |
  ```

- If changes needed:
  ```markdown
  | T1.1.01 | ... | @YourName | 🔄 |
  ```

---

## Quality Gates

Each phase has **quality gates** that must be passed before proceeding:

### Example: Phase 1 Quality Gate

- [ ] All libraries implemented and tested
- [ ] Flake structure working
- [ ] Directory structure in place
- [ ] CI/CD pipelines passing
- [ ] At least 2 services built successfully

**Rule:** Don't start Phase 2 until Phase 1 quality gate passes.

---

## Parallelization Strategy

### Independent Waves

Tasks are organized into **waves** that can be executed in parallel:

```
Phase 1:
├── Wave 1.1: Library Migration
├── Wave 1.2: Security Library ← Can be done in parallel with 1.1
├── Wave 1.3: SBOM Library ← Can be done in parallel with 1.1, 1.2
└── Wave 1.4: Registry Library ← Can be done in parallel with 1.1-1.3
```

### Team Allocation

With **2 developers**:
- Developer A: Works on Wave 1.1
- Developer B: Works on Wave 1.2
- When both finish, move to next waves

With **3 developers**:
- Developer A: Works on Wave 1.1
- Developer B: Works on Wave 1.2
- Developer C: Works on Wave 1.3
- When all finish, move to next waves

---

## Tracking Progress

### Daily Standup

Each developer reports:

1. **What I worked on yesterday**
   - Task ID and description
   - Status changes

2. **What I'm working on today**
   - Task ID and description
   - Expected status change

3. **Blockers**
   - What's preventing progress
   - Who can help resolve

### Weekly Review

1. **Check quality gates** - Have we passed the current phase?
2. **Review progress** - Are we on track for the timeline?
3. **Identify blockers** - What's preventing progress?
4. **Adjust priorities** - Do we need to reprioritize tasks?

---

## Common Patterns

### Working on a New Service

1. **Find the task** in `tasks.md` (e.g., T2.1.01 - Create SOGo 5 image)
2. **Check the spec** in `specs.md` (ADDED section for service image)
3. **Read the technical spec** in `specs/platform/nix-integration/index.md`
4. **Implement** following the patterns:
   - Create `images/<service>/default.nix`
   - Define image configuration
   - Add to `flake.nix`
   - Create tests
   - Update documentation

### Creating a New Library

1. **Find the task** in `tasks.md` (e.g., T1.2.01 - Create security library)
2. **Check the spec** in `specs.md` (ADDED section for library)
3. **Read the technical spec** in `specs/platform/nix-integration/index.md`
4. **Implement** in `lib/<name>.nix`
5. **Add to flake.nix**
6. **Write tests**
7. **Add documentation**

---

## Tips for Success

### 1. Start Small

- Pick a small, well-defined task first
- Get familiar with the codebase and methodology
- Ask questions if anything is unclear

### 2. Follow the Spec

- The technical specification is the source of truth
- If something isn't clear, check the spec first
- If the spec is unclear, ask for clarification

### 3. Update Status Regularly

- Update task status as you work
- This helps the team track progress
- This helps identify blockers early

### 4. Communicate Blockers

- If you're blocked, update the task status to ❌
- Explain what's blocking you
- Tag the person who can help
- Don't stay blocked for more than a day

### 5. Review Others' Work

- Review at least one task per day
- Give constructive feedback
- Help unblock teammates

### 6. Focus on Quality

- Write tests for new functionality
- Update documentation
- Follow the style guide
- Keep commits small and focused

---

## Troubleshooting

### I don't understand what a task is asking for

1. Read the task description carefully
2. Check the linked spec sections
3. Check the technical specification
4. Ask in Matrix: `#opendesk-ce-public:matrix.openedusuite.example.org`
5. Create an issue for clarification

### I'm blocked by a dependency

1. Update the task status to ❌ Blocked
2. Add a comment explaining the blocker
3. Tag the person responsible for the dependency
4. Work on a different task if possible

### The spec is unclear or wrong

1. Create an issue with:
   - Link to the unclear spec
   - Your interpretation
   - What you think it should be
2. Tag the relevant people
3. Wait for clarification before proceeding

### I found a bug in the implementation

1. Check if it's already been reported
2. Create an issue with:
   - Steps to reproduce
   - Expected behavior
   - Actual behavior
   - Screenshots/logs if applicable
3. Tag the assignee of the relevant task

---

## Quick Reference Commands

```bash
# View the change proposal files
cd openEduSuite-spec/changes/nix-integration-proposal
ls -la

# Read the proposal
cat proposal.md | head -100  # First 100 lines

# Find tasks assigned to you
grep "@YourName" tasks.md

# Find unassigned P0 tasks
grep "⏳" tasks.md | grep "P0"

# Find blocked tasks
grep "❌" tasks.md

# Count tasks by status
grep -o "⏳\|🔄\|✅\|❌\|🚧" tasks.md | sort | uniq -c

# Count total tasks
grep "^| T" tasks.md | wc -l

# Read the technical specification
cat ../../specs/platform/nix-integration/index.md | head -200
```

---

## Additional Resources

- [OpenSpec Methodology](../../METHODOLOGY.md) - Official OpenSpec documentation
- [Nix Manual](https://nixos.org/manual/nix/stable/) - Nix documentation
- [Nix Flakes](https://nixos.wiki/wiki/Flakes) - Nix flakes guide
- [Nixpkgs Manual](https://nixos.org/manual/nixpkgs/stable/) - Nixpkgs documentation
- [Kubernetes Documentation](https://kubernetes.io/docs/home/) - Kubernetes docs

---

## Feedback

Have feedback on this guide or the change proposal process?

- Create an issue in the repository
- Suggest improvements in Matrix
- Update this document if you have write access

---

**Last Updated:** 2026-08-28  
**Version:** 1.0
