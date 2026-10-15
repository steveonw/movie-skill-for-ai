# AI Workshop — Issue #2 Is the Main Communication Hub

**Project mission:** Build three standalone, interoperable filmmaking Skills: Story Director, Narration Studio and Movie Builder. Useful movies, working code and tested outputs take priority over project-management rituals.

**Single coordination location:** [GitHub Issue #2 — AI Workshop Message Board](https://github.com/steveonw/movie-skill-for-ai/issues/2). **All agents use Issue #2 for clock-ins, clock-outs, work claims, cross-Skill messages, review requests and decisions.** Do not use a live table in this Markdown file or commit to `main` for routine attendance/claim updates. This document holds stable rules only; Issue #2 holds the conversation and its history.

There are **no continuously running background agents**. Comments are messages for future sessions and people. A posted `CLOCK IN` is not evidence an AI remains online, and Issue #2 comments do not automatically trigger other agents.

## Starting a coding session — read, claim, then work

1. **Check Issue #2 first:** read recent comments, identify open questions and locate the latest `CLOCK IN`, `CLOCK OUT`, or `TAKEOVER` for your intended files. Follow links to the current task issue, branches and pull requests; inspect current repository state rather than trusting a stale status comment.
2. **Pick a narrow deliverable:** identify the task issue, specific files, working branch/PR and repeatable acceptance test. Separate ownership of Story Director, Narration Studio and Movie Builder where possible.
3. **CLOCK IN on Issue #2:** when you begin substantial code editing, post **one brief comment** like this:

```markdown
### CLOCK IN — [worker / session identifier]
- Task: #[issue] — [specific deliverable]
- Branch/PR: [link or planned name]
- Editing: [exact paths or narrow directory]
- Check: [test or observable deliverable]
- Need from others: [none / named question]
```

4. **Avoid collisions:** another worker's claimed files or unmerged PR require review and coordination before edits. Reply on Issue #2 with a conflict question or choose separate files. Use your own branch; do not force-push someone else's work.
5. **Work on the deliverable.** A clock-in is not a permission gate. If GitHub comments are unavailable, continue useful work, note the coordination limitation and provide a clear handoff.

A brief question, read-only review, or owner-requested tweak to this coordination protocol does **not** need ceremonial clock-in and clock-out posts.

## Issue #2 is the conversation, not just a noticeboard

Post actionable messages **in Issue #2**, including:
- `CLOCK IN`: who is doing what, branch, and file scope.
- `QUESTION / REQUEST — [source -> recipient]`: one decision or artifact needed from another Skill or the owner/master AI. State why, link the issue/PR, and say who should answer.
- `FINDING / BLOCKED / REVIEW REQUEST`: measured facts or obstacles others need to act on, with direct links to evidence.
- `DECISION — [owner / designated integrator]`: accepted cross-Skill contract choice, affected fields/versions and follow-up documentation/tests. A proposal is **not** an approved contract.
- `CLOCK OUT / HANDOFF`: links to the completed or draft deliverable, what actually ran, what remains and an explicit claim release.

**Replies belong primarily on Issue #2 when coordinating across agents.** Keep long stack traces, detailed tests, code discussion and changed-file reviews in the specific task issue or PR, then link them from a short Issue #2 comment. Do not duplicate the same technical report in multiple places. One useful update is better than many trivial status messages.

Cross-Skill request example:

```markdown
### QUESTION — Movie Builder -> Narration Studio / owner
- Related: #1, PR #7, PR #8
- Need: accepted field and sample units for audible speech start
- Why: movie cuts should not reveal a punchline before its spoken anchor
- Proposal (unapproved): ceil measured start samples to the next video frame
- Reply: here on Issue #2; link schema approval when decided
```

## Finish and hand off on Issue #2

When a session with a `CLOCK IN` ends, **post one `CLOCK OUT / HANDOFF` on Issue #2**. This is how other agents know a file claim was released; no row on `main` needs changing.

```markdown
### CLOCK OUT / HANDOFF — [worker / same session identifier]
- Task/PR: #[issue] / [branch or PR link]
- Done: [concrete artifact or changed files]
- Verified: [command + observed result, or "not run"]
- Still needed: [one clear next step or blocker]
- Impact on other Skills: [none / specific request]
- File claim released: Yes
```

If the worker also needs a detailed task-specific handoff, put the full evidence on the task issue or PR and link it. Keep the Issue #2 comment short.

## Stale claims and takeovers

A clock-in is an advisory claim, **not a lock**. Do not assume that a worker is active merely because it did not clock out. For an apparently abandoned claim, inspect Issue #2's latest comments, the task issue, branch and PR activity. A claim older than 12 hours is a reason to inspect, **not an automatic expiry**. If there is no conflicting active work, post `TAKEOVER` on Issue #2 with the prior claim link, evidence checked, new scope and branch. Do not delete branches or overwrite unmerged work.

## Ownership and source of truth

- **Issue #2:** single home for coordination, current session claims, questions, decisions and handoffs. Keep it open throughout development unless the repository owner retires it.
- **Task issues (#1 Movie Builder, #4 Story Director, #5 Narration Studio, etc.):** acceptance criteria and detailed task-specific evidence.
- **PRs/branches:** code and reviews; use them instead of changing `main` directly for implementation.
- **AGENTS.md / AI_HANDOFF.md / ROADMAP.md / ARCHITECTURE.md / DECISIONS.md:** durable project instructions and accepted designs. Update only when substance changes, not for each clock-in.
- **research/originals/:** preserve immutable historical research.

Tests and current code outrank prose status claims. Never label a synthetic-audio proof as a finished narrated movie, invent tests or promise background execution. **The purpose of the workshop is to let separate sessions coordinate effectively while they build a working filmmaking toolkit.**
