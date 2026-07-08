from pawpal_system import Task, Pet, Owner, Scheduler

# ── Owner and pets ────────────────────────────────────────────────────────────
jordan = Owner(name="Jordan", available_minutes=90)

mochi = Pet(name="Mochi", species="dog", age=3)
luna = Pet(name="Luna", species="cat", age=5, special_needs=["indoor only"])

# Tasks added OUT of priority order to show sort_by_priority working
mochi.add_task(Task(
    title="Training session",
    duration_minutes=20,
    priority="medium",
    category="enrichment",
    description="Sit, stay, and new trick practice",
    frequency="daily",
    start_time="09:00",
))
mochi.add_task(Task(
    title="Morning walk",
    duration_minutes=30,
    priority="high",
    category="exercise",
    description="Leash walk around the block",
    frequency="daily",
    start_time="08:00",
))
mochi.add_task(Task(
    title="Feeding",
    duration_minutes=10,
    priority="high",
    category="nutrition",
    description="1 cup dry kibble + fresh water",
    frequency="daily",
    start_time="08:30",
))

luna.add_task(Task(
    title="Medication",
    duration_minutes=5,
    priority="high",
    category="health",
    description="Daily allergy pill hidden in a treat",
    frequency="daily",
    start_time="08:40",
))
luna.add_task(Task(
    title="Brush coat",
    duration_minutes=15,
    priority="medium",
    category="grooming",
    description="Prevents matting and reduces hairballs",
    frequency="weekly",
    start_time="09:20",
))
luna.add_task(Task(
    title="Puzzle feeder",
    duration_minutes=10,
    priority="low",
    category="enrichment",
    description="Fill kibble puzzle to keep Luna stimulated",
    frequency="daily",
    start_time="09:35",
))

jordan.add_pet(mochi)
jordan.add_pet(luna)

scheduler = Scheduler(owner=jordan, start_hour=8)

# ── 1. Main schedule (priority-sorted, time-filtered) ─────────────────────────
print("=" * 55)
plan = scheduler.build_plan()
print(scheduler.explain_plan(plan))

# ── 2. sort_by_time: Mochi's tasks in chronological order ────────────────────
print("\n" + "=" * 55)
print("Mochi's tasks sorted by start_time:")
for task in scheduler.sort_by_time(mochi.list_tasks()):
    print(f"  {task.start_time}  {task.title} ({task.duration_minutes} min)")

# ── 3. filter_tasks: only pending tasks across all pets ──────────────────────
print("\n" + "=" * 55)
print("Pending tasks across all pets:")
for task, pet in scheduler.filter_tasks(completed=False):
    print(f"  [{pet.name}] {task.title} ({task.priority} priority)")

# ── 4. detect_conflicts: overlapping manual start_times ──────────────────────
print("\n" + "=" * 55)
print("Conflict detection demo:")
# Vet call at 09:10 overlaps Training session (09:00-09:20)
mochi.add_task(Task(
    title="Vet call",
    duration_minutes=15,
    priority="high",
    category="health",
    start_time="09:10",
))
conflict_plan = scheduler.build_plan()
conflicts = scheduler.detect_conflicts(conflict_plan)
if conflicts:
    for warning in conflicts:
        print(f"  WARNING: {warning}")
else:
    print("  No conflicts detected.")

# ── 5. reschedule_recurring ───────────────────────────────────────────────────
print("\n" + "=" * 55)
print("Recurring task rescheduling demo:")
walk = next(t for t in mochi.list_tasks() if t.title == "Morning walk")
print(f"  Before: '{walk.title}' completed={walk.completed}, "
      f"Mochi task count={len(mochi.list_tasks())}")
next_task = scheduler.reschedule_recurring(walk, mochi)
print(f"  After:  '{walk.title}' completed={walk.completed}")
if next_task:
    print(f"  Rescheduled: '{next_task.title}' due {next_task.due_date}, "
          f"Mochi task count={len(mochi.list_tasks())}")
