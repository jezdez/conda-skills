---
name: review-notes
description: Use when turning supplied code-review findings into a concise handoff for the author.
---

# Review notes

Organize the user's review findings so the code author can act on them. This example only summarizes supplied findings; it does not review code or run commands.

For each finding, keep the file and line if provided, the problem, its consequence, and the proposed fix. Preserve any uncertainty. If a location or fix is missing, say so rather than inventing one.

Put findings that could lose data or expose private information first, followed by correctness problems and maintainability suggestions. Preserve the reviewer's severity labels if supplied. Combine duplicate findings only when they describe the same problem at the same location.

End with the checks the reviewer actually ran and any stated testing gaps. Do not describe suggested tests as passed, and do not modify files.
