from pawpal_system import Task, Pet, Owner, Scheduler


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
