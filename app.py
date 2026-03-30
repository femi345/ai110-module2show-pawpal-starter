"""
app.py — PawPal+ Streamlit UI

Run with:  streamlit run app.py
"""

from datetime import date

import streamlit as st

from pawpal_system import Owner, Pet, Scheduler, Task

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="wide")

# ---------------------------------------------------------------------------
# Session state bootstrap
# ---------------------------------------------------------------------------

if "owner" not in st.session_state:
    st.session_state.owner = None  # set when owner name is submitted

if "sort_mode" not in st.session_state:
    st.session_state.sort_mode = "time"

# ---------------------------------------------------------------------------
# Sidebar — Owner setup
# ---------------------------------------------------------------------------

with st.sidebar:
    st.image("https://em-content.zobj.net/source/apple/391/paw-prints_1f43e.png", width=60)
    st.title("PawPal+")
    st.caption("Smart pet care, simplified.")
    st.divider()

    # Owner name
    owner_name_input = st.text_input(
        "Your name",
        value=st.session_state.owner.name if st.session_state.owner else "",
        placeholder="e.g. Jordan",
    )
    if st.button("Set owner", use_container_width=True):
        if owner_name_input.strip():
            if st.session_state.owner is None:
                st.session_state.owner = Owner(owner_name_input.strip())
            else:
                st.session_state.owner.name = owner_name_input.strip()
            st.success(f"Welcome, {st.session_state.owner.name}!")
        else:
            st.error("Please enter a name.")

    if st.session_state.owner:
        st.divider()
        st.markdown(f"**Owner:** {st.session_state.owner.name}")
        st.markdown(f"**Pets:** {len(st.session_state.owner.pets)}")

    # ------------------------------------------------------------------ #
    # Add pet
    # ------------------------------------------------------------------ #
    if st.session_state.owner:
        st.divider()
        st.subheader("Add a pet")
        pet_name_input = st.text_input("Pet name", placeholder="e.g. Mochi", key="new_pet_name")
        species_input = st.selectbox("Species", ["dog", "cat", "rabbit", "bird", "other"],
                                     key="new_pet_species")
        if st.button("Add pet", use_container_width=True):
            if pet_name_input.strip():
                existing_names = [p.name.lower() for p in st.session_state.owner.pets]
                if pet_name_input.strip().lower() in existing_names:
                    st.warning("A pet with that name already exists.")
                else:
                    st.session_state.owner.add_pet(Pet(pet_name_input.strip(), species_input))
                    st.success(f"Added {pet_name_input.strip()} 🐾")
            else:
                st.error("Pet name cannot be empty.")

# ---------------------------------------------------------------------------
# Main area
# ---------------------------------------------------------------------------

if st.session_state.owner is None:
    st.title("🐾 Welcome to PawPal+")
    st.info("Enter your name in the sidebar to get started.")
    st.stop()

owner: Owner = st.session_state.owner
scheduler = Scheduler(owner)

st.title(f"🐾 PawPal+  —  {owner.name}'s Dashboard")

# ---------------------------------------------------------------------------
# Add Task
# ---------------------------------------------------------------------------

with st.expander("➕ Add a care task", expanded=not bool(owner.get_all_tasks())):
    if not owner.pets:
        st.warning("Add a pet in the sidebar first.")
    else:
        col_a, col_b = st.columns(2)
        with col_a:
            selected_pet_name = st.selectbox(
                "Pet", [p.name for p in owner.pets], key="task_pet"
            )
            task_desc = st.text_input("Task description", placeholder="e.g. Morning walk",
                                      key="task_desc")
            task_time = st.text_input("Time (HH:MM)", value="08:00", key="task_time")
        with col_b:
            task_duration = st.number_input(
                "Duration (minutes)", min_value=1, max_value=480, value=20, key="task_dur"
            )
            task_priority = st.selectbox(
                "Priority", ["low", "medium", "high"], index=1, key="task_pri"
            )
            task_frequency = st.selectbox(
                "Frequency", ["once", "daily", "weekly"], key="task_freq"
            )
            task_date = st.date_input("Due date", value=date.today(), key="task_date")

        if st.button("Add task", type="primary"):
            if not task_desc.strip():
                st.error("Task description cannot be empty.")
            else:
                # Validate HH:MM
                try:
                    hh, mm = task_time.split(":")
                    assert 0 <= int(hh) <= 23 and 0 <= int(mm) <= 59
                    time_str = f"{int(hh):02d}:{int(mm):02d}"
                except Exception:
                    st.error("Time must be in HH:MM format (e.g. 08:30).")
                    st.stop()

                target_pet = next(p for p in owner.pets if p.name == selected_pet_name)
                target_pet.add_task(Task(
                    description=task_desc.strip(),
                    time=time_str,
                    duration_minutes=int(task_duration),
                    frequency=task_frequency,
                    priority=task_priority,
                    due_date=task_date,
                ))
                st.success(f"Task '{task_desc.strip()}' added to {selected_pet_name}.")

st.divider()

# ---------------------------------------------------------------------------
# Today's Schedule
# ---------------------------------------------------------------------------

st.subheader("📅 Today's Schedule")

if not owner.pets or not owner.get_all_tasks():
    st.info("No tasks yet. Add a pet and some tasks above.")
else:
    # Controls row
    ctrl_col1, ctrl_col2, ctrl_col3 = st.columns([2, 2, 2])
    with ctrl_col1:
        sort_choice = st.radio(
            "Sort by", ["Time", "Priority"], horizontal=True, key="sort_radio"
        )
    with ctrl_col2:
        filter_pet = st.selectbox(
            "Filter by pet", ["All pets"] + [p.name for p in owner.pets],
            key="filter_pet_select"
        )
    with ctrl_col3:
        show_all_dates = st.checkbox("Show all dates (not just today)", key="all_dates")

    # Build task list
    if show_all_dates:
        pairs = scheduler.all_tasks()
    else:
        pairs = scheduler.filter_tasks(completed=False, due_date=date.today())

    if filter_pet != "All pets":
        pairs = [(p, t) for p, t in pairs if p.name == filter_pet]

    if sort_choice == "Priority":
        pairs = scheduler.sort_by_priority(pairs)
    else:
        pairs = scheduler.sort_by_time(pairs)

    # Conflict warnings
    conflicts = scheduler.detect_conflicts()
    for w in conflicts:
        st.warning(w)

    if not pairs:
        st.success("✅ No pending tasks for today!")
    else:
        _PRIORITY_EMOJI = {"high": "🔴", "medium": "🟡", "low": "🟢"}
        _FREQ_LABEL = {"once": "", "daily": "↻ daily", "weekly": "↻ weekly"}

        table_rows = []
        for pet, task in pairs:
            table_rows.append({
                "Time": task.time,
                "Pet": pet.name,
                "Task": task.description,
                "Duration": f"{task.duration_minutes} min",
                "Priority": f"{_PRIORITY_EMOJI[task.priority]} {task.priority}",
                "Repeats": _FREQ_LABEL[task.frequency],
                "Due": str(task.due_date),
                "Done": "✓" if task.completed else "",
            })
        st.table(table_rows)

    # Mark complete
    st.divider()
    st.subheader("✅ Mark a task complete")

    if not owner.get_all_tasks():
        st.info("No tasks to mark complete.")
    else:
        all_incomplete = [(p, t) for p, t in scheduler.all_tasks() if not t.completed]
        if not all_incomplete:
            st.success("All tasks are already done!")
        else:
            task_labels = [
                f"{p.name} — {t.description} ({t.time}, {t.due_date})"
                for p, t in all_incomplete
            ]
            chosen_label = st.selectbox("Select task", task_labels, key="complete_select")
            if st.button("Mark complete"):
                idx = task_labels.index(chosen_label)
                pet, task = all_incomplete[idx]
                next_t = scheduler.mark_task_complete(pet, task)
                st.success(f"'{task.description}' marked complete!")
                if next_t:
                    st.info(
                        f"Next occurrence scheduled for {next_t.due_date} "
                        f"({next_t.frequency} task)."
                    )

# ---------------------------------------------------------------------------
# Pet overview
# ---------------------------------------------------------------------------

st.divider()
st.subheader("🐾 Pet Overview")

if not owner.pets:
    st.info("No pets added yet.")
else:
    cols = st.columns(min(len(owner.pets), 3))
    for i, pet in enumerate(owner.pets):
        with cols[i % 3]:
            total = pet.task_count()
            done = sum(1 for t in pet.tasks if t.completed)
            pct = int(done / total * 100) if total else 0
            st.metric(label=f"{pet.name} ({pet.species})",
                      value=f"{total} tasks",
                      delta=f"{done} completed")
            if total:
                st.progress(pct)

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------

st.divider()
st.caption("PawPal+ · Built with Streamlit · CodePath AI110 Module 2")
