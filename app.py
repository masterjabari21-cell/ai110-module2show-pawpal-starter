import streamlit as st
from pawpal_system import Task, Pet, Owner, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

CATEGORY_ICONS = {
    "exercise": "🚶", "nutrition": "🍽️", "health": "💊",
    "grooming": "🧼", "enrichment": "🧩", "general": "📌",
}

# ── Session state: persists data across every Streamlit re-run ───────────────
if "owner" not in st.session_state:
    st.session_state.owner = None

# ── Owner setup ───────────────────────────────────────────────────────────────
st.header("Owner Setup")
if st.session_state.owner is None:
    with st.form("owner_form"):
        col1, col2 = st.columns(2)
        owner_name = col1.text_input("Your name", value="Jordan")
        available_minutes = col2.number_input(
            "Available minutes today", min_value=10, max_value=480, value=120, step=10
        )
        if st.form_submit_button("Set owner"):
            st.session_state.owner = Owner(
                name=owner_name, available_minutes=int(available_minutes)
            )
            st.rerun()
else:
    owner = st.session_state.owner
    col1, col2 = st.columns([3, 1])
    col1.success(
        f"Owner: **{owner.name}** | Available time: **{owner.available_minutes} min**"
    )
    if col2.button("Reset all"):
        st.session_state.owner = None
        st.rerun()

if st.session_state.owner is None:
    st.stop()

owner = st.session_state.owner
scheduler = Scheduler(owner=owner, start_hour=8)

# ── Pets ──────────────────────────────────────────────────────────────────────
st.divider()
st.header("Pets")
with st.expander("➕ Add a new pet"):
    with st.form("add_pet_form"):
        col1, col2, col3 = st.columns(3)
        pet_name = col1.text_input("Pet name", value="Mochi")
        species = col2.selectbox("Species", ["dog", "cat", "rabbit", "bird", "other"])
        age = col3.number_input("Age", min_value=0, max_value=30, value=2)
        special_needs_input = st.text_input("Special needs (comma-separated, optional)")
        if st.form_submit_button("Add pet"):
            needs = [s.strip() for s in special_needs_input.split(",") if s.strip()]
            owner.add_pet(Pet(name=pet_name, species=species, age=int(age), special_needs=needs))
            st.success(f"Added {pet_name} the {species}!")

if owner.list_pets():
    pet_rows = [
        {
            "Pet": p.name,
            "Species": p.species,
            "Age": p.age,
            "Tasks": len(p.list_tasks()),
            "Pending": len(p.pending_tasks()),
            "Special needs": ", ".join(p.special_needs) or "—",
        }
        for p in owner.list_pets()
    ]
    st.table(pet_rows)
else:
    st.info("No pets yet. Add one above.")
    st.stop()

# ── Tasks ─────────────────────────────────────────────────────────────────────
st.divider()
st.header("Tasks")
with st.expander("➕ Add a new task"):
    with st.form("add_task_form"):
        selected_pet_name = st.selectbox("For which pet?", [p.name for p in owner.list_pets()])
        col1, col2, col3 = st.columns(3)
        task_title = col1.text_input("Task title", value="Morning walk")
        duration = col2.number_input("Duration (min)", min_value=1, max_value=240, value=20)
        priority = col3.selectbox("Priority", ["low", "medium", "high"], index=2)
        col4, col5, col6 = st.columns(3)
        category = col4.selectbox("Category", list(CATEGORY_ICONS.keys()))
        frequency = col5.selectbox("Frequency", ["daily", "weekly", "as-needed"])
        start_time = col6.text_input("Start time HH:MM (optional)", value="")
        description = st.text_input("Description (optional)")
        if st.form_submit_button("Add task"):
            target_pet = next(p for p in owner.list_pets() if p.name == selected_pet_name)
            target_pet.add_task(Task(
                title=task_title,
                duration_minutes=int(duration),
                priority=priority,
                category=category,
                description=description,
                frequency=frequency,
                start_time=start_time.strip() or None,
            ))
            st.success(f"Added '{task_title}' to {selected_pet_name}!")

if owner.get_all_tasks():
    st.subheader("All Tasks")
    col1, col2 = st.columns(2)
    filter_pet_name = col1.selectbox(
        "Filter by pet", ["All"] + [p.name for p in owner.list_pets()], key="filter_pet"
    )
    filter_status = col2.radio(
        "Filter by status", ["All", "Pending", "Completed"], horizontal=True
    )
    pet_filter = None if filter_pet_name == "All" else filter_pet_name
    done_filter = None if filter_status == "All" else (filter_status == "Completed")
    filtered = scheduler.filter_tasks(pet_name=pet_filter, completed=done_filter)

    if filtered:
        for i, (task, pet) in enumerate(filtered):
            icon = CATEGORY_ICONS.get(task.category, "📌")
            status = "✅" if task.completed else "⬜"
            time_str = f" @ {task.start_time}" if task.start_time else ""
            col_a, col_b = st.columns([5, 1])
            col_a.markdown(
                f"{status} {icon} **{task.title}** — {pet.name}{time_str} "
                f"({task.duration_minutes} min, {task.priority} priority, {task.frequency})"
            )
            if not task.completed:
                if col_b.button("Done", key=f"done_{i}_{pet.name}_{task.title}"):
                    next_task = scheduler.reschedule_recurring(task, pet)
                    if next_task:
                        st.toast(
                            f"'{task.title}' done! Rescheduled for {next_task.due_date} "
                            f"({task.frequency})."
                        )
                    else:
                        st.toast(f"'{task.title}' done! (as-needed — no repeat scheduled)")
                    st.rerun()
    else:
        st.info("No tasks match the filter.")
else:
    st.info("No tasks yet. Add one above.")

# ── Generate schedule ─────────────────────────────────────────────────────────
st.divider()
st.header("Today's Schedule")
if st.button("Generate schedule", type="primary"):
    if not owner.get_all_tasks():
        st.warning("Add at least one task before generating a schedule.")
    else:
        plan = scheduler.build_plan()

        # Conflict warnings: shown first so the owner can fix times before relying on the plan
        conflicts = scheduler.detect_conflicts(plan)
        for warning in conflicts:
            st.warning(f"⚠️ {warning} — consider moving one of these start times.")

        if plan:
            # Structured table view of the plan
            time_cursor = scheduler.start_hour * 60
            rows = []
            for task, pet in plan:
                hours, mins = divmod(time_cursor, 60)
                rows.append({
                    "Time": f"{hours:02d}:{mins:02d}",
                    "Task": f"{CATEGORY_ICONS.get(task.category, '📌')} {task.title}",
                    "Pet": pet.name,
                    "Duration": f"{task.duration_minutes} min",
                    "Priority": task.priority,
                })
                time_cursor += task.duration_minutes
            st.table(rows)

            total = sum(t.duration_minutes for t, _ in plan)
            st.success(
                f"Scheduled {len(plan)} task(s) totaling {total} min "
                f"of your {owner.available_minutes} min available."
            )
            skipped = len(owner.get_all_tasks()) - len(plan) - sum(
                1 for t in owner.get_all_tasks() if t.completed
            )
            if skipped > 0:
                st.info(
                    f"{skipped} pending task(s) didn't fit today. "
                    "Increase available time or lower a task's duration."
                )

            with st.expander("Plain-text plan (explain_plan output)"):
                st.code(scheduler.explain_plan(plan), language=None)
        else:
            st.warning(scheduler.explain_plan(plan))
else:
    st.caption("Add pets and tasks above, then click Generate schedule.")
