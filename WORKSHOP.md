# AI Workshop Protocol

This repository has a **lightweight collaboration system for AI-assisted development**. It is not a background-agent scheduler: an assistant only works while actively invoked in a session. GitHub provides the persistent record between sessions.

## Where everything goes

- **GitHub Issues:** the task board and discussion threads. One issue per independently testable task.
- **Issue comments:** clock-in, short progress notes when meaningful, blocker messages, clock-out/handoff.
- **Branches and Pull Requests:** changes needing review, experimental work, or code that may conflict with another worker. Do not casually overwrite another worker's branch.
- **AGENTS.md:** shared instructions for anyone touching the repo.
- **AI_HANDOFF.md and ROADMAP.md:** cross-session project memory, not a replacement for task-specific issue histories.
- **research/originals/:** archive—do not alter.

## Clock in (one issue per active worker)

Before coding:
1. Read AGENTS.md, AI_HANDOFF.md, relevant issue and recent comments, related branches/PRs.
2. Check for a recent claim; avoid duplicate modifications to the same files.
3. Post a **CLOCK IN** comment using the template below, including AI/model *as self-reported*, a unique session label, exact intended task/files, proposed branch, and planned verification.
4. If another active claim conflicts, choose a separate task, review their changes, or coordinate in the same thread. A claimed task is a **courtesy reservation**, not a GitHub lock and not proof of active background execution.
5. Prefer one small task that can be completed and evidenced in the current session.

### Clock-in template

```markdown
### CLOCK IN
- Worker: GPT / Claude / Gemini / Grok / other (self-reported)
- Session: YYYY-MM-DD / short unique descriptor
- Task: #issue — short goal
- Intended files: [paths]
- Branch/PR: [link or planned branch]
- Starting from: [commit SHA if known]
- Plan: [2–4 sentences]
- Acceptance test: [specific command/output]
- Dependencies or collisions: [none, or issue/worker]
- Status: Working in this active session only; no background work implied
```

## During work

- Keep changes focused on the issue.
- Add **BLOCKED** comment when input/permissions/runtime prevents further work; say precisely what is missing.
- Add **FINDING** comment for an insight affecting other Skills or the shared file contract. Label facts as tested, inferred, or unverified.
- Link commits, test outputs, and PRs instead of claiming success generically.
- If planning a breaking change, propose it in the issue first and describe migrations.
- Prefer separate files/branches for independent work. Review commits made by others before modifying overlapping files.

## Clock out (required even for incomplete work when possible)

```markdown
### CLOCK OUT / HANDOFF
- Worker/session: [same identity as clock in]
- Issue: #number
- Status: Completed / Partial / Blocked / Not started
- Changed files and commits/PRs: [links]
- What works: [observable test evidence]
- Tests executed: [commands and results, or explicitly 'not run']
- Open problems: [precise failures, missing dependencies, uncertainty]
- Next action: [one concrete small next step]
- Compatibility/architecture impacts: [none or describe]
- Docs updated: [which handoff/roadmap/decision files]
- Claim released: Yes
```

If a session ends unexpectedly without clocking out, the next worker should inspect last activity, branches and commits, then post **TAKEOVER** with the reason and new scope. Never infer someone is still running just from an old CLOCK IN.

### Takeover template

```markdown
### TAKEOVER
- Prior claim: [worker/session and link]
- Evidence checked: [comments, branch head, PR, issue status]
- Why takeover is safe: [no recent conflicting activity / task split / agreed handoff]
- New scope and files: [...]
- Tests to run: [...]
```

There is **no automatic timeout** in v1 because GitHub issue comments are not a reliable heartbeat. Use recent evidence and avoid simultaneous writes. When uncertain, prefer a different scope.

## Definition of done

The issue is only finished when:
- the intended deliverable exists in GitHub;
- the acceptance test was actually run and reported, or the issue honestly states what couldn't be tested;
- output limitations and missing assets are disclosed;
- a worker clocked out, linked work, and updated project handoff documentation when decisions/features changed.

A draft PR or a comment saying “done” without proof is not a passing test.

## Message board

Use **the relevant issue's comments**, not a second, disconnected chat board. If an idea is cross-cutting and not yet a task, create a GitHub Issue titled `[IDEA] ...` linking affected issues. Before creating, search existing issues to avoid duplicates.

Message prefixes: `CLOCK IN`, `PROGRESS`, `FINDING`, `QUESTION`, `BLOCKED`, `REVIEW`, `CLOCK OUT / HANDOFF`, `TAKEOVER`.

## Division of responsibility

- A worker may **propose** priorities or contract changes. Large cross-Skill design changes get an issue/PR for review.
- Test outputs and file contents are stronger evidence than a model's confident summary.
- Preserve user work and original research. Keep secrets and private materials out of this public repository.
- Collaboration records represent **activities actually performed**, not imagined agents, monitoring, or autonomous recurring tasks.

## First use

[Issue #1](https://github.com/steveonw/movie-skill-for-ai/issues/1): Build a minimal standalone Movie Builder renderer. A worker should clock in there **when implementation starts**, not earlier.
