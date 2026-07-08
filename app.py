import streamlit as st
from pawpal_system import Task, Pet, Owner, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

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
    st.success(
        f"Owner: **{owner.name}** | Available time: **{owner.available_minutes} min**"
    )
    if st.button("Reset (clears all pets and tasks)"):
        st.session_state.owner = None
        st.rerun()

if st.session_state.owner is None:
    st.stop()

owner = st.session_state.owner

# ── Pets ──────────────────────────────────────────────────────────────────────
st.divider()
st.header("Pets")
with st.expander("Add a new pet"):
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
    for pet in owner.list_pets():
        needs_str = ", ".join(pet.special_needs) if pet.special_needs else "none"
        st.markdown(
            f"- **{pet.name}** ({pet.species}, age {pet.age}) — "
            f"{len(pet.list_tasks())} task(s) | special needs: {needs_str}"
        )
else:
    st.info("No pets yet. Add one above.")
    st.stop()

# ── Tasks ─────────────────────────────────────────────────────────────────────
st.divider()
st.header("Tasks")
with st.expander("Add a new task"):
    with st.form("add_task_form"):
        selected_pet_name = st.selectbox("For which pet?", [p.name for p in owner.list_pets()])
        col1, col2, col3 = st.columns(3)
        task_title = col1.text_input("Task title", value="Morning walk")
        duration = col2.number_input("Duration (min)", min_value=1, max_value=240, value=20)
        priority = col3.selectbox("Priority", ["low", "medium", "high"], index=2)
        col4, col5 = st.columns(2)
        category = col4.text_input("Category", value="exercise")
        frequency = col5.selectbox("Frequency", ["daily", "weekly", "as-needed"])
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
            ))
            st.success(f"Added '{task_title}' to {selected_pet_name}!")

# Task list with filtering
scheduler = Scheduler(owner=owner)
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

    for task, pet in filtered:
        icon = "✅" if task.completed else "⬜"
        st.markdown(
            f"{icon} **{task.title}** — {pet.name} "
            f"({task.duration_minutes} min, {task.priority} priority, {task.frequency})"
        )
    if not filtered:
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
        scheduler = Scheduler(owner=owner, start_hour=8)
        plan = scheduler.build_plan()

        conflicts = scheduler.detect_conflicts(plan)
        for warning in conflicts:
            st.warning(warning)

        st.code(scheduler.explain_plan(plan), language=None)

        total_tasks = len(owner.get_all_tasks())
        if len(plan) < total_tasks:
            st.info(
                f"{total_tasks - len(plan)} task(s) skipped — "
                f"not enough time in {owner.available_minutes} min."
            )
else:
    st.caption("Add pets and tasks above, then click Generate schedule.")
