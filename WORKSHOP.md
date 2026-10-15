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

## Lightweight claiming and clock-in

### Current claims

**This table is the clock-in.** It lists only work in progress *right now*, so two sessions never edit the same files by accident. It is not a log.

| Worker / session | Issue | Branch | Files it owns | Claimed (UTC) |
|---|---|---|---|---|
| _none right now_ | | | | |

**Open for claiming:** Story Director M1 (#4) · Narration word-level timing (follow-up to #5) · reviews of PR #7 / PR #8.
Unmerged work to know about: Movie Builder QA on draft PR #7, Narration Studio on PR #8. Neither is on `main` yet.

**Clock in (30 seconds):**
1. Pull `main` and read this table and the latest posts on #2.
2. If your files overlap an existing row, pick other files, coordinate on #2, or do a TAKEOVER (below). Don't share files silently.
3. Add your row and push it straight to `main` with the commit message `claim: <worker> on #<issue>`. Editing this table is the one routine change allowed directly on `main`; touch nothing else in that commit.
4. If the push is rejected because `main` moved, pull again, re-check the table, and retry.

**Clock out:** delete your row (`release: <worker> on #<issue>`) in the same session you finish, and leave the handoff on your issue or PR (template below). If you open a PR or find something another Skill needs, also post one short line on #2.

**Stale claims:** a row older than 12 hours whose branch has no new commits is presumed abandoned. Post a TAKEOVER on its issue saying what you checked, then replace the row. Never delete someone's branch or force-push to it.

### Optional claim comment

The table above is the claim. A **CLOCK IN** comment on the task issue is only worth posting when you need to explain scope to another worker (shared files, a takeover, a plan that changes an interface). It never blocks useful work.

Suggested concise message:

```markdown
### CLOCK IN — [worker/session]
- Working on: #issue, [specific deliverable] on [branch]
- Own files: [paths]
- Verification: [concrete test]
- Coordination needed: [none / question / overlapping PR]
```

A clock-in is a **courtesy claim, not a lock, attendance record, or proof of ongoing work**. If a past claim has no recent evidence of work, examine its PR/commits and coordinate or record a scoped takeover; don't assume an agent remains active. Never overwrite another worker's unmerged branch without explicit consent or a released handoff.

## During implementation

Make the smallest useful and testable change. Work on a dedicated branch and open a PR rather than changing `main` directly, **except for your own row in the Current claims table, or when the user specifically requests a direct documentation/policy edit on main**. Avoid edits outside the task's owner directory. Preserve all user-owned artifacts, licensing requirements and sensitive data rules from AGENTS.md.

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

**Definition of done:** a useful deliverable exists, acceptance checks were executed and reported (or limitations candidly disclosed), reviewable change history is available, and future work is unambiguously handed off. The goal remains good movies and independently useful Skills—not management theater.
