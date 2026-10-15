# AI Workshop — Shared Coordination, Not Agent Attendance

**Mission:** Produce three independently useful, interoperable filmmaking Skills: Story Director, Narration Studio and Movie Builder. The deliverable is working media and verified code, not clock-in reports.

**This GitHub repository is shared project memory between human and AI sessions.** There are no persistent background agents. A session only works when a user explicitly starts it. A worker's issue comment is a handoff to *future people or sessions*, not a message to itself.

## Central communication hub: Issue #2

**Read recent comments on the [shared AI workshop board (#2)](https://github.com/steveonw/movie-skill-for-ai/issues/2) at the beginning of each session.** This is the cross-AI message board, where the master AI and other Skill developers can see what is actually happening. It must not become an attendance log.

When a meaningful milestone/PR occurs, **post one short board comment** containing: which Skill/AI, link to the task issue and PR, tested results versus untested claims, the next step, and any request or warning for other Skills. Keep the detailed test logs and handoff on your task issue/PR. On cross-Skill schema questions, request a master/owner decision on #2 and wait for accepted contract updates before treating the proposal as official. Do not announce an invented agent status as active.

## Communication principle

Use GitHub only when the message would change another worker's decision or help a later session resume accurately. **Avoid ceremonial self-messaging.** No repeating status in multiple issues; no daily attendance, timecards, or check-ins with no code or useful discovery. A worker should spend most of the session coding, testing and reviewing.

Use:
- **Issues:** independently testable work items, dependencies and substantive blockers.
- **Issue comments:** coordination across owners, tested findings, conflicts, and final handoffs.
- **Pull requests:** the authoritative reviewable record of code changes, test results and remaining gaps.
- **AGENTS.md / AI_HANDOFF.md / ROADMAP.md:** shared technical directions and durable current state, updated only for meaningful changes.
- **WORKSHOP.md (this file):** shared working agreement, plus the **Current claims** table below (who is working on what *right now*). Don't keep an agent activity log here: rows are deleted when work ends, history lives in issues and PRs.
- **research/originals/:** immutable source archives.

## Clock in: a shared, live file-ownership table on `main`

### Current claims

**The table below is the clock-in.** Add a row **only when beginning a concrete editing session** and remove it at handoff. The point is to stop agents from editing the same files without knowing about each other, not to track attendance or pretend agents are running in the background.

| Worker / session | Issue and deliverable | Branch / PR | Files being edited | Next action / help needed | Claimed (UTC) |
| --- | --- | --- | --- | --- | --- |
| _none currently claimed_ | | | | | |

**Find work and outstanding requests:** [open issues](https://github.com/steveonw/movie-skill-for-ai/issues?q=is%3Aissue+is%3Aopen) · [open PRs](https://github.com/steveonw/movie-skill-for-ai/pulls?q=is%3Apr+is%3Aopen) · [cross-agent messages (#2)](https://github.com/steveonw/movie-skill-for-ai/issues/2). Do **not** maintain a manually copied list of "available" issues or PR statuses here; that becomes stale.

### Start work (30-second coordination)

1. **Read first:** fetch the current `main` version of this table, recent #2 posts, the task issue, and existing branches/PRs. An earlier agent's claimed branch may have unmerged changes that must be reviewed before continuing.
2. **Choose a small scope:** identify one issue, a concrete deliverable, a unique session label, your working branch, and **specific file paths**. A role like "Movie Builder" alone is too broad to serve as a useful claim.
3. **CLOCK IN:** insert one row in the table on `main`. Example row:
   `| GPT-6 / 2026-10-14-mb-cuts | #1: prove encoded reveal frames | work/movie-builder-cuts / PR TBD | movie_builder/verify_cuts.py, movie_builder/tests/ | Run cut tests; ask Narration about onset anchors | 2026-10-15 03:30 UTC |`
   This is an **example only**, not an active claim. Use the actual current UTC time and actual worker/session label.
4. **Commit only the table edit** to `main` as `claim: <worker/session> #<issue>`. Do not mix code or unrelated documentation with this short claim commit. If a competing edit changed `WORKSHOP.md`, fetch the newest version, re-check for overlapping files, and retry using the latest blob SHA; do not force-push or replace someone else's row.
5. **Code on your own branch**, not on `main`. A claim is a courtesy reservation of a **file-edit scope**, not ownership of an entire Skill or a lock. If any listed file overlaps another claim or unmerged PR, coordinate or narrow your scope **before** editing it.

For user-requested small edits **to this coordination document itself**, do not create a row just to change and remove that row. Make the requested main-branch edit and report the commit.

If GitHub write access is unavailable, don't block the work: leave an issue/PR comment if possible and explicitly state the overlap uncertainty in your handoff.

### Stale claims and collision handling

A clock-in does **not** mean that an agent is still running. GitHub cannot tell whether a chat session remains active. A claim older than ~12 hours **merits inspection**, but is **not automatically abandoned**. Check the last issue/PR comments and branch commits, then either coordinate with the worker or post a brief **TAKEOVER** on the task issue explaining which files and evidence you checked. Never delete the other worker's branch, force-push their work or silently overwrite their claim. Update the table to reflect the new owner only after that review.

If two sessions reach for the same files, one should take a separate test/review task or create a separate branch and PR. **File claims are advisory; branch and PR history are authoritative.**

## How agents actually communicate

**Issue #2 is for messages meant for another worker or the project integrator.** A message is useful only if the recipient can understand the requested decision or action. Routine clock-ins belong **only in the table**; detailed logs belong **only on the task issue/PR**.

When one Skill needs another, post **one** targeted request on #2:

```markdown
### REQUEST / DECISION NEEDED — [source Skill -> destination Skill or owner]
- From: [worker/session, issue, PR]
- To: [Story Director / Narration Studio / Movie Builder / owner or integrator]
- Need: [one concrete answer, review or artifact]
- Why it matters: [downstream test blocked or risk of conflict]
- Proposed default: [specific proposal, explicitly not yet approved]
- Reply location: [issue or PR link]
```

The recipient, **when invoked in a later active session**, should read #2, respond on the linked issue/PR, and leave one short link back on #2 if the answer affects other Skills. A #2 comment **does not start an agent**, deliver a notification, or authorize an interface change by itself. A proposed shared schema becomes authoritative only when the owner/designated integrator approves it and the appropriate contract docs/tests are updated.

Other substantive board messages can start with `FINDING`, `REVIEW REQUEST`, or `BLOCKED`, always with a recipient, a link, and a requested next action. Don't post a second "status" comment merely to repeat your PR description.

## During implementation

Make the smallest useful and testable change. Work on a dedicated branch and open a PR rather than changing `main` directly, **except for updating the Current claims table or user-requested policy/documentation changes on main**. Avoid edits outside the task's owner directory. Preserve all user-owned artifacts, licensing requirements and sensitive data rules from AGENTS.md.

Comment on an issue only for something *another session needs to know*:
- **FINDING:** measured outcome with test evidence or a cross-Skill interface constraint.
- **QUESTION / BLOCKED:** a genuine decision or resource needed from another owner.
- **REVIEW:** a concrete request to inspect a PR or contract decision.
- **TAKEOVER:** why previously claimed files are safe to continue.

Link the relevant issue or PR. **Do not post routine internal thoughts, generic “progress” messages, or duplicate comments in the workshop board.** For cross-Skill changes, report substantive findings/questions on **Issue #2**, with a link to the specific issue/PR. The same technical information should live in detail only once; the board contains concise summaries and cross-links.

## Handoff / clock-out

At the end of a session, leave **one concise, evidence-based handoff** on the relevant issue or PR so the next worker doesn't have to reconstruct the context. Clock-out is encouraged where a claim was made, but it is not more important than the deliverable.

```markdown
### HANDOFF / CLOCK OUT — [worker/session]
- Result: [PR/commit and concrete files]
- Verified: [commands run + observed outputs]; not run: [anything untested]
- Remaining: [precise open issues and next action]
- Coordination: [interface changes / none]
- Claim released: yes
```

Avoid claiming success merely because tests were written: say which tests *actually ran*, where, and with what outputs. Draft PRs remain works in progress. Don't claim work continues after the session.

## Source of truth and priorities

1. Executed tests, real renders and inspected assets.
2. Current code on the linked branch and PR.
3. Issue acceptance criteria and recent factual handoffs.
4. AI_HANDOFF.md / ROADMAP.md as a summarized current snapshot.
5. Earlier planning discussions and historical research.

If documents disagree with tested code, fix the documentation; don't make vague success claims.

**Definition of done:** a useful deliverable exists, acceptance checks were executed and reported (or limitations candidly disclosed), reviewable change history is available, and future work is unambiguously handed off. **CLOCK OUT:** remove your row from the live claims table, then leave one evidence-based handoff on your task issue/PR. If another workstream needs to act, leave one targeted linked notice on #2. The goal remains good movies and independently useful Skills—not management theater.
