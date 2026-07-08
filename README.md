# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Run `python main.py` to generate a daily schedule from the demo data:

```
=== Today's Schedule for Jordan ===
Available time: 90 min  |  Starting at 08:00

  [    ] 08:00  Morning walk -- Mochi  (30 min, high priority)
              Leash walk around the block
  [    ] 08:30  Feeding -- Mochi  (10 min, high priority)
              1 cup dry kibble + fresh water
  [    ] 08:40  Medication -- Luna  (5 min, high priority)
              Daily allergy pill hidden in a treat
  [    ] 08:45  Training session -- Mochi  (20 min, medium priority)
              Sit, stay, and new trick practice
  [    ] 09:05  Brush coat -- Luna  (15 min, medium priority)
              Prevents matting and reduces hairballs
  [    ] 09:20  Puzzle feeder -- Luna  (10 min, low priority)
              Fill kibble puzzle to keep Luna stimulated

Total scheduled: 90 min
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
python -m pytest

# Verbose mode (shows each test name):
python -m pytest -v
```

**What the tests cover** (15 tests in `tests/test_pawpal.py`):

- **Task basics** — completion status flips correctly, adding tasks grows a pet's task list, and invalid priority values raise a `ValueError` instead of silently mis-sorting.
- **Sorting correctness** — `sort_by_time()` returns tasks in chronological `HH:MM` order and pushes untimed tasks to the end; `sort_by_priority()` orders high → medium → low.
- **Recurrence logic** — completing a daily task creates a fresh copy due tomorrow, a weekly task recurs in 7 days, and "as-needed" tasks do not recur.
- **Conflict detection** — overlapping time windows are flagged with a warning naming both tasks; non-overlapping tasks produce no warnings.
- **Scheduler edge cases** — completed tasks are excluded from plans, the time budget is never exceeded, and a pet with no tasks (or an owner with no pets) yields an empty plan without crashing.

Sample test output:

```
============================= test session starts =============================
platform win32 -- Python 3.13.1, pytest-9.1.1, pluggy-1.6.0
collected 15 items

tests/test_pawpal.py::test_mark_complete_changes_status PASSED           [  6%]
tests/test_pawpal.py::test_add_task_increases_pet_task_count PASSED      [ 13%]
tests/test_pawpal.py::test_invalid_priority_raises_error PASSED          [ 20%]
tests/test_pawpal.py::test_sort_by_time_returns_chronological_order PASSED [ 26%]
tests/test_pawpal.py::test_sort_by_time_puts_untimed_tasks_last PASSED   [ 33%]
tests/test_pawpal.py::test_sort_by_priority_orders_high_first PASSED     [ 40%]
tests/test_pawpal.py::test_daily_recurring_task_creates_next_day_instance PASSED [ 46%]
tests/test_pawpal.py::test_weekly_recurring_task_due_in_seven_days PASSED [ 53%]
tests/test_pawpal.py::test_as_needed_task_does_not_recur PASSED          [ 60%]
tests/test_pawpal.py::test_detect_conflicts_flags_overlapping_tasks PASSED [ 66%]
tests/test_pawpal.py::test_detect_conflicts_ignores_non_overlapping_tasks PASSED [ 73%]
tests/test_pawpal.py::test_scheduler_excludes_completed_tasks PASSED     [ 80%]
tests/test_pawpal.py::test_scheduler_respects_available_time PASSED     [ 86%]
tests/test_pawpal.py::test_pet_with_no_tasks_produces_empty_plan PASSED  [ 93%]
tests/test_pawpal.py::test_owner_with_no_pets_produces_empty_plan PASSED [100%]

============================= 15 passed in 0.05s ==============================
```

**Confidence Level: ⭐⭐⭐⭐ (4/5)** — All core behaviors (sorting, filtering, recurrence, conflict detection, time budgeting) are covered by passing tests, including empty-input edge cases. One star held back because conflict detection only covers tasks with manually assigned start times, and the greedy scheduler's behavior with many same-priority tasks competing for limited time hasn't been stress-tested.

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Sort by priority | `Scheduler.sort_by_priority()` | Orders tasks high → medium → low before time-fitting |
| Sort by start time | `Scheduler.sort_by_time()` | Sorts a task list by `HH:MM` start_time; untimed tasks go last |
| Filter by time budget | `Scheduler.filter_by_time()` | Greedy first-fit: includes tasks in priority order until time runs out |
| Filter by pet / status | `Scheduler.filter_tasks()` | Returns `(Task, Pet)` pairs filtered by pet name and/or completion flag |
| Conflict detection | `Scheduler.detect_conflicts()` | Checks tasks with manual `start_time` for overlapping windows; returns warning strings |
| Recurring tasks | `Scheduler.reschedule_recurring()` | Marks a task complete and adds a new copy due tomorrow (daily) or in 7 days (weekly) using `timedelta` |

## 📸 Demo Walkthrough

Describe your app in numbered steps so a reader can follow along without watching a video:

1. <!-- Describe this step -->
2. <!-- Describe this step -->
3. <!-- Describe this step -->
4. <!-- Describe this step -->
5. <!-- Add more steps as needed -->

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
