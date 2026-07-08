# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

Three core actions a user should be able to perform:

1. **Add a pet** — The user enters basic pet information (name, species, age, and any special needs) so the system knows who it is planning care for.
2. **Add and manage care tasks** — The user creates tasks such as a morning walk, feeding, medication, or grooming, each with a title, estimated duration in minutes, and a priority level (low, medium, or high).
3. **Generate and view today's schedule** — The user triggers the scheduler, which selects and orders tasks based on the owner's available time and task priorities, then displays the resulting daily plan with a plain-language explanation of why each task was included and when it happens.

The four main building blocks are:

- **Owner** — holds the owner's name, how many minutes they have available today, and any personal preferences (e.g., prefers morning tasks). Responsible for setting availability and owning one or more pets.
- **Pet** — holds pet info (name, species, age, special needs) and the list of care tasks associated with that pet.
- **Task** — a dataclass holding a task's title, duration in minutes, priority, and category. Knows whether it is high-priority.
- **Scheduler** — receives an Owner, a Pet, and the task list, then builds an ordered daily plan that fits within the available time. Also generates a human-readable explanation of the plan.

Relationships: an Owner owns one or more Pets; a Pet has zero or more Tasks; the Scheduler uses the Owner and Pet to produce a plan from the Task list.

**b. Design changes**

After reviewing the skeleton, four issues were identified and fixed:

1. **Private-named dataclass fields removed** (`_tasks`, `_pets` → `tasks`, `pets` with `init=False`). In Python dataclasses, a field named `_tasks` still appears as a constructor parameter, forcing callers to write `Pet(_tasks=[...])`. Making them `init=False` hides them from the constructor so `Pet("Mochi", "dog", 3)` works cleanly.

2. **Added `Owner.list_pets()`** — `Owner` could store pets but had no way to retrieve them, breaking the owns-many relationship defined in the UML.

3. **Added `Task.__post_init__` validation** — `priority` was unchecked, so a typo like `"hig"` would silently score as 99 in the scheduler and always be pushed to the end of the plan. Now it raises a clear `ValueError` immediately on construction.

4. **Added `start_hour` to `Scheduler`** — `explain_plan` previously displayed all tasks starting at `00:00` (midnight), which made the output misleading. Adding a `start_hour` parameter (defaulting to 8 AM) produces a realistic time display and makes the scheduler more flexible.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers two constraints: task priority (high / medium / low) and the owner's total available time in minutes. Priority was treated as the primary constraint because a pet's medical or feeding needs should never be skipped in favor of lower-stakes enrichment tasks regardless of duration. Available time is the secondary constraint — once the time budget is exhausted, remaining tasks are dropped. Owner preferences (stored on the `Owner` object) are not yet wired into the scheduling algorithm; they were deprioritized because priority and time alone are sufficient for a daily plan.

**b. Tradeoffs**

The scheduler uses a **greedy first-fit** approach: it sorts all pending tasks by priority and then walks the list, adding each task if it fits in the remaining time. The tradeoff is that a single long high-priority task (e.g. a 60-minute grooming session) can consume most of the time budget and crowd out several shorter medium-priority tasks that together would have been more beneficial. A smarter alternative would be a knapsack-style optimizer that maximizes total value within the time budget, but that adds significant complexity. The greedy approach is reasonable here because pet care tasks are not interchangeable — a high-priority medication task genuinely should not be skipped in favor of filling the schedule with more short tasks. Conflict detection is also limited to tasks with manually assigned `start_time` values; the scheduler itself never produces overlapping windows since it assigns times sequentially.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

The suite has 15 tests covering five areas: task basics (completion status, task counts, and that an invalid priority raises `ValueError`), sorting correctness (`sort_by_time` returns chronological order and puts untimed tasks last; `sort_by_priority` orders high → medium → low), recurrence logic (a completed daily task spawns a copy due tomorrow, weekly recurs in 7 days, "as-needed" does not recur), conflict detection (overlapping windows are flagged, non-overlapping ones are not), and scheduler edge cases (completed tasks excluded, time budget never exceeded, empty pets/owners don't crash). These matter because they pin down the behaviors the app's daily plan depends on — if sorting or the time budget silently broke, the schedule would still render but would be wrong, which is worse than an error.

**b. Confidence**

Confidence is about 4 out of 5. Every core behavior has at least one passing test, including the empty-input edge cases. With more time, the next tests would be: overlapping tasks for *different* pets at the same time, many same-priority tasks competing for a too-small time budget (to verify which ones win is deterministic), recurring tasks completed multiple days in a row (to check copies don't multiply incorrectly), and start times that cross midnight.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
