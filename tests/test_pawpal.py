from datetime import date, timedelta

from pawpal_system import Task, Pet, Owner, Scheduler


# ── Task basics ───────────────────────────────────────────────────────────────

def test_mark_complete_changes_status():
    task = Task(title="Morning walk", duration_minutes=30, priority="high")
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_add_task_increases_pet_task_count():
    pet = Pet(name="Mochi", species="dog", age=3)
    assert len(pet.list_tasks()) == 0
    pet.add_task(Task(title="Feeding", duration_minutes=10, priority="high"))
    pet.add_task(Task(title="Walk", duration_minutes=20, priority="medium"))
    assert len(pet.list_tasks()) == 2


def test_invalid_priority_raises_error():
    try:
        Task(title="Typo task", duration_minutes=10, priority="hig")
        assert False, "Expected ValueError for invalid priority"
    except ValueError:
        pass


# ── Sorting correctness ───────────────────────────────────────────────────────

def test_sort_by_time_returns_chronological_order():
    owner = Owner(name="Jordan")
    scheduler = Scheduler(owner=owner)
    tasks = [
        Task(title="Evening walk", duration_minutes=20, start_time="18:30"),
        Task(title="Morning walk", duration_minutes=30, start_time="08:00"),
        Task(title="Lunch feeding", duration_minutes=10, start_time="12:15"),
    ]
    ordered = scheduler.sort_by_time(tasks)
    assert [t.title for t in ordered] == ["Morning walk", "Lunch feeding", "Evening walk"]


def test_sort_by_time_puts_untimed_tasks_last():
    owner = Owner(name="Jordan")
    scheduler = Scheduler(owner=owner)
    tasks = [
        Task(title="Anytime brushing", duration_minutes=10),  # no start_time
        Task(title="Morning walk", duration_minutes=30, start_time="08:00"),
    ]
    ordered = scheduler.sort_by_time(tasks)
    assert ordered[-1].title == "Anytime brushing"


def test_sort_by_priority_orders_high_first():
    owner = Owner(name="Jordan")
    pet = Pet(name="Mochi", species="dog", age=3)
    scheduler = Scheduler(owner=owner)
    pairs = [
        (Task(title="Puzzle", duration_minutes=10, priority="low"), pet),
        (Task(title="Meds", duration_minutes=5, priority="high"), pet),
        (Task(title="Brush", duration_minutes=15, priority="medium"), pet),
    ]
    ordered = scheduler.sort_by_priority(pairs)
    assert [t.title for t, _ in ordered] == ["Meds", "Brush", "Puzzle"]


# ── Recurrence logic ──────────────────────────────────────────────────────────

def test_daily_recurring_task_creates_next_day_instance():
    pet = Pet(name="Mochi", species="dog", age=3)
    walk = Task(title="Morning walk", duration_minutes=30, frequency="daily")
    pet.add_task(walk)
    owner = Owner(name="Jordan")
    owner.add_pet(pet)
    scheduler = Scheduler(owner=owner)

    new_task = scheduler.reschedule_recurring(walk, pet)

    assert walk.completed is True
    assert new_task is not None
    assert new_task.due_date == date.today() + timedelta(days=1)
    assert new_task.completed is False
    assert len(pet.list_tasks()) == 2


def test_weekly_recurring_task_due_in_seven_days():
    pet = Pet(name="Luna", species="cat", age=5)
    brush = Task(title="Brush coat", duration_minutes=15, frequency="weekly")
    pet.add_task(brush)
    owner = Owner(name="Jordan")
    owner.add_pet(pet)
    scheduler = Scheduler(owner=owner)

    new_task = scheduler.reschedule_recurring(brush, pet)

    assert new_task is not None
    assert new_task.due_date == date.today() + timedelta(weeks=1)


def test_as_needed_task_does_not_recur():
    pet = Pet(name="Luna", species="cat", age=5)
    nail_trim = Task(title="Nail trim", duration_minutes=10, frequency="as-needed")
    pet.add_task(nail_trim)
    owner = Owner(name="Jordan")
    owner.add_pet(pet)
    scheduler = Scheduler(owner=owner)

    new_task = scheduler.reschedule_recurring(nail_trim, pet)

    assert nail_trim.completed is True
    assert new_task is None
    assert len(pet.list_tasks()) == 1  # no new copy added


# ── Conflict detection ────────────────────────────────────────────────────────

def test_detect_conflicts_flags_overlapping_tasks():
    pet = Pet(name="Mochi", species="dog", age=3)
    owner = Owner(name="Jordan", available_minutes=120)
    owner.add_pet(pet)
    training = Task(title="Training", duration_minutes=20, start_time="09:00")
    vet_call = Task(title="Vet call", duration_minutes=15, start_time="09:10")
    pet.add_task(training)
    pet.add_task(vet_call)

    scheduler = Scheduler(owner=owner)
    conflicts = scheduler.detect_conflicts(scheduler.build_plan())

    assert len(conflicts) == 1
    assert "Training" in conflicts[0]
    assert "Vet call" in conflicts[0]


def test_detect_conflicts_ignores_non_overlapping_tasks():
    pet = Pet(name="Mochi", species="dog", age=3)
    owner = Owner(name="Jordan", available_minutes=120)
    owner.add_pet(pet)
    pet.add_task(Task(title="Walk", duration_minutes=30, start_time="08:00"))
    pet.add_task(Task(title="Feeding", duration_minutes=10, start_time="08:30"))

    scheduler = Scheduler(owner=owner)
    conflicts = scheduler.detect_conflicts(scheduler.build_plan())

    assert conflicts == []


# ── Scheduler edge cases ──────────────────────────────────────────────────────

def test_scheduler_excludes_completed_tasks():
    pet = Pet(name="Luna", species="cat", age=5)
    done = Task(title="Medication", duration_minutes=5, priority="high")
    done.mark_complete()
    pending = Task(title="Brush coat", duration_minutes=15, priority="medium")
    pet.add_task(done)
    pet.add_task(pending)

    owner = Owner(name="Jordan", available_minutes=60)
    owner.add_pet(pet)
    scheduler = Scheduler(owner=owner)
    plan = scheduler.build_plan()

    titles = [task.title for task, _ in plan]
    assert "Medication" not in titles
    assert "Brush coat" in titles


def test_scheduler_respects_available_time():
    pet = Pet(name="Mochi", species="dog", age=3)
    pet.add_task(Task(title="Long walk", duration_minutes=50, priority="high"))
    pet.add_task(Task(title="Training", duration_minutes=40, priority="medium"))

    owner = Owner(name="Jordan", available_minutes=60)
    owner.add_pet(pet)
    scheduler = Scheduler(owner=owner)
    plan = scheduler.build_plan()

    total = sum(task.duration_minutes for task, _ in plan)
    assert total <= owner.available_minutes


def test_pet_with_no_tasks_produces_empty_plan():
    owner = Owner(name="Jordan")
    owner.add_pet(Pet(name="Mochi", species="dog", age=3))
    scheduler = Scheduler(owner=owner)

    plan = scheduler.build_plan()

    assert plan == []
    assert "No tasks fit" in scheduler.explain_plan(plan)


def test_owner_with_no_pets_produces_empty_plan():
    owner = Owner(name="Jordan")
    scheduler = Scheduler(owner=owner)
    assert scheduler.build_plan() == []
