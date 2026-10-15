# AI Workshop — OPTIONAL Coordination, NOT the Project

**Mission:** Build three separate, cooperative filmmaking Skills: **Story Director**, **Narration Studio**, and **Movie Builder**, producing low-cost, well-timed illustrated narration videos. **Read [README.md](README.md) and [AI_HANDOFF.md](AI_HANDOFF.md) before anything about clocking in.**

This file describes a convenient way to share changes across AI sessions. **Clock-in is a GitHub comment, not attendance tracking, an access-control gate, a job queue or a requirement to perform useful work.** A worker without GitHub comment access should still do the user-requested engineering task and hand off results in ordinary text. Nobody should “piss off” or refuse because a clock field wasn't filled out. No AI runs continuously after a chat finishes.

This repository also has a **lightweight collaboration system for AI-assisted development**. It is not a background-agent scheduler: an assistant only works while actively invoked in a session. GitHub provides the persistent record between sessions.

## Current work board (keep this up to date on `main`)

**Every worker edits this table on `main` when they clock in and when they clock out.** Branches and PRs are invisible to a new session until merged; this table is what the next AI reads first. Editing only this table directly on `main` is allowed; everything else still goes through a branch + PR.

_Last updated: 2026-10-15 03:10 UTC by Claude (narration-studio-m1-claude)_

| Skill / task | Issue | Who (self-reported) | State | Branch / PR | Next step |
|---|---|---|---|---|---|
| Movie Builder: QA + make Skill 3 installable | #1 | GPT-6 · movie-builder-skill3-qa-package | **Active now** (clocked in 03:05 UTC) | `work/movie-builder-m1-qa` · draft PR #7 | Fix the one-frame overshoot bug reported on PR #7; finish QA + packaging |
| Narration Studio M1 | #5 | Claude · narration-studio-m1-claude | **Done, clocked out**; waiting on owner review | `work/narration-studio-m1` · PR #8 | Owner reviews/merges PR #8. Later: word-level timing, aligning an outside MP3 |
| Story Director M1 | #4 | nobody | **Open, unclaimed** | none | Clock in on #4 and claim it here |
| Cross-skill questions | #2 | anyone | Open questions on `narration.json` waiting for Movie Builder / Story Director replies | n/a | Read before changing the shared JSON files |

**What exists on `main` today:** Movie Builder technical prototype (`movie_builder/`). **Not yet on `main`:** Narration Studio (PR #8), Movie Builder QA (PR #7). If you need Narration Studio before PR #8 merges, check out `work/narration-studio-m1`.

**Housekeeping:** `work/narration-studio-m2` is an empty leftover branch (identical to an old `main`); safe for the owner to delete.

### How to update the board
- **Clock in:** add or edit your row (State = Active now, with time), then post the CLOCK IN comment on the issue as below.
- **Clock out:** set State to Done / Partial / Blocked, fill in Next step, update "Last updated", then post CLOCK OUT on the issue.
- Commit message: `board: <who> clock in/out on #<issue>`. Touch only this section in that commit, so it never conflicts with anyone's PR.
- Found a row marked Active for hours with no new commits or comments? Don't delete it; follow TAKEOVER below and note it in the row.

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
