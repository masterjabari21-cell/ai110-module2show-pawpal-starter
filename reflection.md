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

AI was used at every phase, but with different jobs: brainstorming the class design and three core user actions in Phase 1, generating the dataclass skeleton from the UML, fleshing out the scheduling algorithms (sorting with a lambda key, `timedelta`-based recurrence, interval-overlap conflict detection), drafting the pytest suite, and wiring `st.session_state` into the Streamlit UI. The most effective feature was agent-mode editing across multiple files at once — for example, adding recurrence required coordinated changes to `Task` (new `due_date` field), `Scheduler` (`reschedule_recurring`), `main.py` (demo), and the tests in one pass. The most helpful prompts were specific and attached real files: "Based on my skeletons in pawpal_system.py, how should the Scheduler retrieve all tasks from the Owner's pets?" got a concrete answer; vague prompts like "make it better" would not have. Keeping separate chat sessions per phase (design, algorithms, testing) kept each conversation focused and prevented earlier decisions from being accidentally re-litigated.

**b. Judgment and verification**

When asked to review the skeleton, the AI initially generated dataclass fields named `_tasks` and `_pets` to signal privacy. That suggestion was not kept as-is: in Python dataclasses, underscore-prefixed fields still show up as constructor parameters, forcing awkward calls like `Pet(_tasks=[...])`. The fix — verified by actually constructing objects in the terminal — was plain names with `init=False`. Similarly, when a knapsack-style optimizer was floated as a "smarter" alternative to the greedy scheduler, it was rejected deliberately: pet care tasks aren't interchangeable point values, and the added complexity wasn't justified. Verification throughout was empirical — every AI-generated method was exercised through `main.py` demo output and pytest before being trusted.

---

## 4. Testing and Verification

**a. What you tested**

The suite has 15 tests covering five areas: task basics (completion status, task counts, and that an invalid priority raises `ValueError`), sorting correctness (`sort_by_time` returns chronological order and puts untimed tasks last; `sort_by_priority` orders high → medium → low), recurrence logic (a completed daily task spawns a copy due tomorrow, weekly recurs in 7 days, "as-needed" does not recur), conflict detection (overlapping windows are flagged, non-overlapping ones are not), and scheduler edge cases (completed tasks excluded, time budget never exceeded, empty pets/owners don't crash). These matter because they pin down the behaviors the app's daily plan depends on — if sorting or the time budget silently broke, the schedule would still render but would be wrong, which is worse than an error.

**b. Confidence**

Confidence is about 4 out of 5. Every core behavior has at least one passing test, including the empty-input edge cases. With more time, the next tests would be: overlapping tasks for *different* pets at the same time, many same-priority tasks competing for a too-small time budget (to verify which ones win is deterministic), recurring tasks completed multiple days in a row (to check copies don't multiply incorrectly), and start times that cross midnight.

---

## 5. Reflection

**a. What went well**

The cleanest part of the project is the separation between the logic layer and the UI. Because `pawpal_system.py` has no Streamlit imports, the exact same `Scheduler` powers the terminal demo (`main.py`), the 15 pytest tests, and the web app — and the design survived from UML draft to final code with only additive changes. The conflict detection and recurrence features also landed working on the first test run, which suggests the earlier investment in a clear class design paid off.

**b. What you would improve**

Three things for the next iteration: (1) wire `Owner.preferences` into the scheduler so "prefers morning tasks" actually influences ordering — the field exists but is decorative; (2) add data persistence (save/load to JSON) so pets and tasks survive an app restart, not just a page re-run; (3) upgrade conflict detection to also consider the scheduler's own computed time slots, not just manually entered start times.

**c. Key takeaway**

The biggest lesson is that the human's job in AI-assisted development is to be the architect, not the typist. The AI was excellent at producing code fast, but every design decision that mattered — greedy vs. knapsack scheduling, which constraints to prioritize, when a "more Pythonic" suggestion actually hurt readability — required human judgment about the *domain*, not the syntax. Being specific in prompts, attaching real files, and verifying every suggestion by running it (rather than trusting that it looked right) is what turned AI output into a system that actually works.
