import streamlit as st
from datetime import date
from pawpal_system import Owner, Pet, Task, Scheduler

# ──────────────────────────────────────────────────────────────
# PAGE CONFIG
# ──────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="PawPal+",
    page_icon="🐾",
    layout="wide",
)

# ──────────────────────────────────────────────────────────────
# SESSION STATE
# ──────────────────────────────────────────────────────────────

if "owner" not in st.session_state:
    loaded = Owner.load_from_json("data.json")
    st.session_state.owner = loaded if loaded else Owner(name="My Household")

owner:     Owner     = st.session_state.owner
scheduler: Scheduler = Scheduler(owner)

# ──────────────────────────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────────────────────────

with st.sidebar:
    st.title("🐾 PawPal+")
    st.caption("Smart Pet Care Manager")
    st.divider()

    # ── ADD A PET ─────────────────────────────────────────────
    st.subheader("➕ Add a New Pet")

    with st.form("add_pet_form", clear_on_submit=True):
        p_name    = st.text_input("Pet Name",    placeholder="e.g. Buddy")
        p_species = st.selectbox("Species",      ["dog", "cat", "rabbit", "bird", "fish", "other"])
        p_breed   = st.text_input("Breed",       placeholder="e.g. Labrador")
        p_age     = st.number_input("Age (yrs)", min_value=0, max_value=30, value=1)

        if st.form_submit_button("Add Pet 🐾"):
            if p_name.strip():
                owner.add_pet(Pet(
                    name=p_name.strip(),
                    species=p_species,
                    breed=p_breed.strip() or "Unknown",
                    age=int(p_age),
                ))
                owner.save_to_json("data.json")
                st.success(f"Added {p_name.strip()}!")
                st.rerun()
            else:
                st.error("Please enter a pet name.")

    st.divider()

    # ── SCHEDULE A TASK ───────────────────────────────────────
    st.subheader("📋 Schedule a Task")

    if not owner.pets:
        st.info("Add a pet first!")
    else:
        with st.form("add_task_form", clear_on_submit=True):
            t_pet      = st.selectbox("For Pet",      [p.name for p in owner.pets])
            t_desc     = st.text_input("Description", placeholder="e.g. Morning walk")
            t_type     = st.selectbox("Task Type",    ["walk", "feeding", "medication", "vet", "general"])
            t_time     = st.time_input("Time")
            t_date     = st.date_input("Date", value=date.today())
            t_freq     = st.selectbox("Frequency",    ["once", "daily", "weekly"])
            t_priority = st.selectbox("Priority",     ["high", "medium", "low"])

            if st.form_submit_button("Add Task ✅"):
                if t_desc.strip() and t_time:
                    pet = owner.get_pet(t_pet)
                    pet.add_task(Task(
                        description=t_desc.strip(),
                        due_time=t_time.strftime("%H:%M"),
                        due_date=str(t_date),
                        frequency=t_freq,
                        priority=t_priority,
                        task_type=t_type,
                    ))
                    owner.save_to_json("data.json")
                    st.success(f"Task added to **{t_pet}**!")
                    st.rerun()
                else:
                    st.error("Please fill in description and time.")

    st.divider()

    # ── SAVE / RESET ──────────────────────────────────────────
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Save 💾"):
            owner.save_to_json("data.json")
            st.success("Saved!")
    with c2:
        if st.button("Reset 🗑️"):
            st.session_state.owner = Owner(name="My Household")
            st.session_state.owner.save_to_json("data.json")
            st.rerun()


# ──────────────────────────────────────────────────────────────
# MAIN AREA
# ──────────────────────────────────────────────────────────────

st.title("🐾 PawPal+ Dashboard")
st.caption(f"Today — {date.today().strftime('%A, %B %d, %Y')}")

# ── SUMMARY METRICS ───────────────────────────────────────────

summary = scheduler.get_summary()
m1, m2, m3, m4 = st.columns(4)
m1.metric("🐾 Pets",          summary["pets"])
m2.metric("📋 Total Tasks",   summary["total"])
m3.metric("⬜ Pending",        summary["pending"])
m4.metric("🔴 High Priority", summary["high_priority_pending"])

# ── CONFLICT WARNINGS ─────────────────────────────────────────

conflicts = scheduler.detect_conflicts()
if conflicts:
    st.divider()
    st.subheader("⚠️ Scheduling Conflicts")
    for c in conflicts:
        st.warning(c)

st.divider()

# ── TABS ──────────────────────────────────────────────────────

tab1, tab2, tab3, tab4 = st.tabs([
    "📅 Today",
    "🗓️ All Tasks",
    "🐾 My Pets",
    "🔍 Tools",
])


# ── TAB 1: TODAY ──────────────────────────────────────────────

with tab1:
    st.subheader("📅 Today's Schedule")
    st.caption("Sorted by priority 🔴 first, then time — powered by Scheduler.get_todays_tasks()")

    todays = scheduler.get_todays_tasks()

    if not todays:
        st.info("No tasks for today. Add some in the sidebar!")
    else:
        for pet_name, task in todays:
            with st.container(border=True):
                cols = st.columns([0.5, 3.5, 1, 1.2, 1.8])
                cols[0].write(f"{task.priority_emoji()} {task.emoji()}")
                cols[1].write(f"**{pet_name}** — {task.description}")
                cols[2].write(f"`{task.due_time}`")
                cols[3].write(task.frequency)

                if not task.completed:
                    key = f"done_{pet_name}_{task.task_id}"
                    if cols[4].button("Mark Done ✅", key=key):
                        msg = scheduler.mark_task_complete_and_reschedule(
                            pet_name, task.description
                        )
                        owner.save_to_json("data.json")
                        st.success(msg)
                        st.rerun()
                else:
                    cols[4].success("Done ✅")


# ── TAB 2: ALL TASKS ──────────────────────────────────────────

with tab2:
    st.subheader("🗓️ All Tasks")

    col_sort, col_pet, col_status = st.columns(3)
    with col_sort:
        sort_by = st.radio("Sort by", ["Priority → Time", "Time only"], horizontal=True)
    with col_pet:
        pet_filter = st.selectbox("Pet", ["All"] + [p.name for p in owner.pets])
    with col_status:
        status_filter = st.selectbox("Status", ["All", "Pending", "Completed"])

    # apply filters
    tasks = (
        scheduler.filter_by_pet(pet_filter)
        if pet_filter != "All"
        else owner.get_all_tasks()
    )
    if status_filter == "Pending":
        tasks = [(n, t) for n, t in tasks if not t.completed]
    elif status_filter == "Completed":
        tasks = [(n, t) for n, t in tasks if t.completed]

    # apply sort
    tasks = (
        scheduler.sort_by_priority_then_time(tasks)
        if sort_by == "Priority → Time"
        else scheduler.sort_by_time(tasks)
    )

    if not tasks:
        st.info("No tasks match your filters.")
    else:
        rows = []
        for pet_name, task in tasks:
            rows.append({
                "Pet":       f"{task.emoji()} {pet_name}",
                "Task":      task.description,
                "Time":      task.due_time,
                "Date":      task.due_date,
                "Priority":  f"{task.priority_emoji()} {task.priority}",
                "Frequency": task.frequency,
                "Status":    "✅ Done" if task.completed else "⬜ Pending",
            })
        st.table(rows)


# ── TAB 3: MY PETS ────────────────────────────────────────────

with tab3:
    st.subheader("🐾 My Pets")

    if not owner.pets:
        st.info("No pets yet. Add one in the sidebar!")
    else:
        cols = st.columns(min(len(owner.pets), 3))
        for i, pet in enumerate(owner.pets):
            with cols[i % 3]:
                with st.container(border=True):
                    st.markdown(f"### {pet.species_emoji()} {pet.name}")
                    st.write(f"**Species:** {pet.species.title()}")
                    st.write(f"**Breed:**   {pet.breed}")
                    st.write(f"**Age:**     {pet.age} yr{'s' if pet.age != 1 else ''}")
                    pending = len(pet.get_pending_tasks())
                    done    = len(pet.get_completed_tasks())
                    st.write(f"**Tasks:**   {pending} pending, {done} done")

                    if pet.tasks:
                        with st.expander("View all tasks"):
                            for task in pet.tasks:
                                status = "✅" if task.completed else "⬜"
                                st.write(
                                    f"{status} {task.priority_emoji()} {task.emoji()} "
                                    f"`{task.due_time}` {task.description}"
                                )

                    if st.button(f"Remove {pet.name} 🗑️", key=f"rm_{pet.name}"):
                        owner.remove_pet(pet.name)
                        owner.save_to_json("data.json")
                        st.rerun()


# ── TAB 4: TOOLS ──────────────────────────────────────────────

with tab4:
    st.subheader("🔍 Smart Tools")

    # Next Available Slot
    st.markdown("#### 🕐 Find Next Available Slot")
    st.caption("Scans booked times and returns the first free 30-minute window.")

    slot_col1, slot_col2 = st.columns(2)
    with slot_col1:
        slot_date  = st.date_input("Date", value=date.today(), key="slot_date")
    with slot_col2:
        slot_start = st.time_input("Search from", key="slot_start")

    if st.button("Find Free Slot 🔍"):
        start_str = slot_start.strftime("%H:%M") if slot_start else "07:00"
        result    = scheduler.find_next_available_slot(str(slot_date), start_str)
        st.success(f"✅ Next free slot on **{slot_date}** from {start_str}: **{result}**")

    st.divider()

    # Priority-Weighted Schedule
    st.markdown("#### ⭐ Priority-Weighted Schedule")
    st.caption(
        "Scores each task: high = 30 pts, medium = 20 pts, low = 10 pts, "
        "+5 bonus for medication. Returns top-ranked pending tasks."
    )

    plan_col1, plan_col2 = st.columns(2)
    with plan_col1:
        plan_date = st.date_input("Date", value=date.today(), key="plan_date")
    with plan_col2:
        max_shown = st.slider("Max tasks", 3, 15, 8)

    plan = scheduler.build_priority_schedule(str(plan_date), max_tasks=max_shown)

    if not plan:
        st.info("No pending tasks on that date.")
    else:
        for i, (pet_name, task) in enumerate(plan, 1):
            bonus = " *(+5 med bonus)*" if task.task_type == "medication" else ""
            st.markdown(
                f"**{i}.** {task.priority_emoji()} {task.emoji()}  "
                f"`{task.due_time}` — **{pet_name}**: {task.description}  "
                f"({task.priority}{bonus})"
            )