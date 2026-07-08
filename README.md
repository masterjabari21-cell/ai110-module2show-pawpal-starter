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
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
============================= test session starts =============================
platform win32 -- Python 3.13.1, pytest-9.1.1
collected 4 items

tests/test_pawpal.py::test_mark_complete_changes_status PASSED           [ 25%]
tests/test_pawpal.py::test_add_task_increases_pet_task_count PASSED      [ 50%]
tests/test_pawpal.py::test_scheduler_excludes_completed_tasks PASSED     [ 75%]
tests/test_pawpal.py::test_scheduler_respects_available_time PASSED      [100%]

============================== 4 passed in 0.03s ==============================
```

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
