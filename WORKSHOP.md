# Multi-Agent Workshop — Selective GitHub Collaboration

**Objective:** Build three independently useful filmmaking Skills—Story Director, Narration Studio, and Movie Builder—and integrate them into a reliable story-to-MP4 workflow. **Working movies and tested code matter more than managing agents.**

**Shared channel: [GitHub Issue #2](https://github.com/steveonw/movie-skill-for-ai/issues/2).** This is the project's equivalent of the classroom experiment's `TRANSMIT:` bus. Independent sessions selectively publish information for the others, instead of exposing their full working conversations. Issue #2 remains open throughout the project. This document describes the protocol; do not edit it for routine check-ins.

## 1. The four seats

| Seat / workstream | Primary responsibility | Existing tracking |
| --- | --- | --- |
| AI-1 — Story Director | Story beats, visual planning, setup/payoff, intentional reveals | [Issue #4](https://github.com/steveonw/movie-skill-for-ai/issues/4) |
| AI-2 — Narration Studio | Narration, audio assembly, sample-exact speech/word timing | [Issues #5 and #9](https://github.com/steveonw/movie-skill-for-ai/issues/5) |
| AI-3 — Movie Builder | Timed visuals, rendering, FFmpeg, encoded output QA | [Issue #1](https://github.com/steveonw/movie-skill-for-ai/issues/1) |
| AI-4 — Integrator / QA | Review interoperability, investigate contract conflicts, end-to-end acceptance | Cross-Skill PRs and Issue #2 |

These are **roles, not assigned model identities**. Gemini, Claude, GPT, Grok, other assistants, or human developers can occupy a seat for a session; identify the actual worker in any message. The repository owner/human coordinator is **separate from the four seats** and retains final authority over shared decisions. Fewer than four sessions may be active; never invent an agent or imply that one is running.

## 2. Information flow: private working context, selective transmissions

An AI may have its own chat, tools, notes, research and tests. These **are not automatically synchronized with other AI chats**. When the findings matter to another seat, explicitly post **one concise message starting with `TRANSMIT:`** as an **Issue #2 comment**. The other seats read these transmissions the next time they are invoked.

**Only a `TRANSMIT:` message is intended as a team-wide AI-to-AI broadcast in this protocol.** Historical Issue #2 comments without this marker remain readable, but new workers should follow this convention. GitHub itself does **not** restrict visibility based on a prefix: all public repo issues, comments, branches and PRs are public. Never publish private reasoning, API keys, unpublished manuscripts, recordings, full chats or sensitive materials to GitHub.

Use this compact format:

```markdown
TRANSMIT: [TYPE] — [FROM seat / model / session] -> [TO seat, owner, or ALL]
- Context: [task issue / branch / PR / source comment link]
- Message: [the specific finding, question, request, or result]
- Evidence: [tested command/result and link, or explicitly PROPOSED / UNVERIFIED]
- Needed: [one action or decision; "none" if FYI]
```

Valid types: `CLOCK IN`, `FINDING`, `QUESTION`, `REQUEST`, `BLOCKED`, `REVIEW`, `HANDOFF / CLOCK OUT`, and `TAKEOVER`. **Do not transmit every intermediate thought** or repeat a complete PR description. Link supporting files/tests rather than pasting large dumps.

## 3. Human coordinator broadcasts and decisions

The owner/coordinator can post a message on Issue #2 beginning **`BROADCAST:`** with scope, goal, constraints and recipients. A worker reads and acknowledges it *in its next active session* when necessary. A GitHub comment does not invoke a model, wake a worker, start a job or create a background scheduler.

Any worker can **propose** interface changes using `TRANSMIT: QUESTION` or `TRANSMIT: REQUEST`. Only the human owner or an explicitly designated integrator with authority may issue an **approved** shared-contract decision, e.g.:

```markdown
BROADCAST: DECISION — owner/coordinator
- Decision: [precise fields / units / schema version / rule]
- Applies to: [affected Skills and issues]
- Evidence and migration: [PR/tests and compatibility requirements]
- Follow-up: [who updates ARCHITECTURE.md / DECISIONS.md]
```

A worker's unilateral `TRANSMIT:` is not contract approval. Pending proposals remain provisional. Do not block unrelated standalone work while waiting on a cross-Skill choice.

## 4. Clock-in means avoiding collisions, not attendance

Before substantive coding, read Issue #2's **recent comments**, active PRs and the intended files. Post one short transmission:

```markdown
TRANSMIT: CLOCK IN — [seat / model / unique session] -> ALL
- Context: #issue; branch/PR
- Message: Implementing [small, testable deliverable]. Editing [exact paths].
- Evidence: planned acceptance test [command or check] — NOT YET RUN
- Needed: [specific coordination, or none]
```

Work on a reviewable branch. A claim is an **advisory reservation** of specific files, not an exclusive GitHub lock or proof of continuing activity. Check overlapping unmerged PRs, split files or request coordination rather than overwriting someone else's work. For tiny documentation-only edits or read-only reviews, don't generate unnecessary clock-in/out chatter.

After the session, post the matching **`TRANSMIT: HANDOFF / CLOCK OUT`** with links to commits/PR, executed tests (or *not run*), unresolved defects, next task, and **claim released**. The full logs, changes and test detail stay on the task issue or PR.

An old claim is not proof a chat is alive. If a prior worker has not signed off, inspect issue comments/PR activity and report why takeover is safe before editing shared files. A ~12-hour-old comment calls for investigation, **not automatic expiration**. Never delete another worker's branch or force-push it.

## 5. AIDE requests and independent work

In the classroom experiment, `AIDE REQUEST:` delegated focused work to a personal assistant and the coordinator pasted back `AIDE OUTPUT`. In the GitHub variant:

- Within an AI's **own session**, request focused research, coding, web lookup, or tests from available tools or a connected aide. Use `AIDE REQUEST: [specific question and success criteria]` **only if that session actually has an aide workflow**.
- The worker evaluates evidence locally. A tool run is not a separate autonomous teammate; don't manufacture an aide or claim a test happened unless it actually ran.
- Transmit only the result another seat needs, e.g. `TRANSMIT: FINDING` with test evidence and a PR/issue link. If the human coordinator supplies external aide output, distinguish it from independently reproduced tests.

No worker must possess the same tools as any other worker.

## 6. Normal workflow and example

1. **Read:** an active worker inspects recent Issue #2 `BROADCAST:` and `TRANSMIT:` messages, linked issues and PRs.
2. **Self-organize:** choose an unclaimed scope consistent with the project's mission; only ask the owner for choices that truly require owner authority.
3. **Work independently:** reason and use tools inside the worker's own session; commit tests and code on its own branch.
4. **Transmit selectively:** findings, dependency requests, concrete milestones and review requests go to Issue #2 with a recipient. Other public issue/PR comments are supporting context, not automatic team transmissions.
5. **Handoff:** record exact tested results, limitations and released file claims. Future sessions pick up from this evidence.

**Example dialogue (illustrative, not an actual transmission):**

```markdown
TRANSMIT: QUESTION — Movie Builder / GPT session -> Narration Studio, Integrator
- Context: Movie Builder #1; narration PR #8
- Message: Which absolute sample field represents audible speech onset?
- Evidence: Our cut planner needs an anchor; a clip boundary can precede speech.
- Needed: Confirm field and provenance so we can test frame-ceiling behavior.

TRANSMIT: FINDING — Narration Studio / Claude session -> Movie Builder
- Context: narration schema and its regression tests
- Message: Proposed speech_start_sample is absolute in narration.wav.
- Evidence: link to tested schema/PR; word alignment availability noted.
- Needed: Owner/integrator decision before treating this as a frozen contract.
```

## 7. Source of truth and boundaries

- **Issue #2:** one central message bus for `TRANSMIT:` and `BROADCAST:`, clock-in/handoff and cross-Skill discussions.
- **Task issues:** independently testable acceptance criteria, task-specific evidence.
- **Branches/PRs:** authoritative code changes, detailed tests and review.
- **AGENTS.md / AI_HANDOFF.md / ARCHITECTURE.md / DECISIONS.md / ROADMAP.md:** durable product guidance and owner-approved decisions, updated when substance changes.
- **research/originals/:** preserve archived research unchanged.

Where status disagrees with tested code, trust actual output and correct the status. None of these GitHub conventions establishes private channels or automatic multi-agent execution. **The workshop is a coordination layer for making better movies, not the product itself.**
