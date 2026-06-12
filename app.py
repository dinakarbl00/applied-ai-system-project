import streamlit as st
from datetime import date, time as dtime
from pawpal_system import Owner, Pet, Task
from ai_advisor import ask_advisor
from evaluate import run_evaluation

# ── PAGE CONFIG ───────────────────────────────────────────────
st.set_page_config(
    page_title="PawPal+ AI Care",
    page_icon="🐾",
    layout="wide",
)

# ── LOAD OWNER DATA ───────────────────────────────────────────
def load_owner() -> Owner:
    owner = Owner.load_from_json("data.json")
    if not owner:
        owner = Owner(name="Demo User")
        demo_pet = Pet(name="Buddy", species="dog", breed="Labrador", age=3)
        owner.add_pet(demo_pet)
        owner.save_to_json("data.json")
    return owner

if "owner" not in st.session_state:
    st.session_state.owner = load_owner()

owner: Owner = st.session_state.owner

# ── HEADER ────────────────────────────────────────────────────
st.title("🐾 PawPal+ AI Care")
st.caption("AI-powered pet care advisor with eval harness, guardrails & confidence scoring")

# ── TABS ──────────────────────────────────────────────────────
tab_advisor, tab_eval, tab_pets = st.tabs([
    "🤖 AI Advisor",
    "📊 Eval Dashboard",
    "🐶 Pet Management",
])

# ══════════════════════════════════════════════════════════════
# TAB 1 — AI ADVISOR
# ══════════════════════════════════════════════════════════════
with tab_advisor:
    st.subheader("AI Pet Care Advisor")
    st.write("Ask any pet care question. The advisor uses your pet's profile to give personalized answers.")

    if not owner.pets:
        st.warning("No pets found. Add a pet in the **Pet Management** tab first.")
    else:
        # Pet selector
        pet_names = [p.name for p in owner.pets]
        selected_name = st.selectbox("Select your pet", pet_names, key="advisor_pet_select")
        selected_pet = next(p for p in owner.pets if p.name == selected_name)

        st.caption(
            f"**{selected_pet.name}** · {selected_pet.species.title()} · "
            f"{selected_pet.breed} · {selected_pet.age} yrs old"
        )

        # Per-pet conversation history in session state
        history_key = f"chat_history_{selected_pet.name}"
        if history_key not in st.session_state:
            st.session_state[history_key] = []

        history = st.session_state[history_key]

        # Clear button
        if st.button("🗑️ Clear conversation", key="clear_chat"):
            st.session_state[history_key] = []
            st.rerun()

        st.divider()

        # Render full history first — always top to bottom
        if not history:
            st.info("No conversation yet. Ask your first question below!")
        else:
            for turn in history:
                if turn["role"] == "user":
                    with st.chat_message("user"):
                        st.write(turn["text"])
                else:
                    with st.chat_message("assistant"):
                        if turn.get("flagged"):
                            st.warning(turn["text"])
                            st.caption("🔴 Guardrail triggered — off-topic or low confidence")
                        else:
                            st.write(turn["text"])
                            conf = turn.get("confidence", 0.5)
                            if conf >= 0.8:
                                badge = f"🟢 Confidence: {conf:.0%}"
                            elif conf >= 0.5:
                                badge = f"🟡 Confidence: {conf:.0%}"
                            else:
                                badge = f"🔴 Confidence: {conf:.0%}"
                            st.caption(badge)

        # Chat input — always renders at bottom
        question = st.chat_input(
            placeholder=f"Ask something about {selected_pet.name}...",
        )

        if question:
            # Build history in ask_advisor format
            advisor_history = [
                {"role": h["role"], "text": h["text"]}
                for h in history
            ]

            with st.spinner("Thinking..."):
                result = ask_advisor(question, selected_pet, history=advisor_history)

            # Append both turns to session state then rerun
            history.append({"role": "user", "text": question})
            history.append({
                "role": "assistant",
                "text": result["answer"],
                "confidence": result["confidence"],
                "flagged": result["flagged"],
            })
            st.session_state[history_key] = history
            st.rerun()


# ══════════════════════════════════════════════════════════════
# TAB 2 — EVAL DASHBOARD
# ══════════════════════════════════════════════════════════════
with tab_eval:
    st.subheader("Evaluation Dashboard")
    st.write(
        "This harness runs 15 predefined test cases through the AI advisor "
        "and measures reliability, confidence calibration, and guardrail behavior."
    )

    if st.button("▶️ Run Evaluation", type="primary"):
        with st.spinner("Running 15 test cases... (~1 minute)"):
            summary = run_evaluation()
        st.session_state["eval_summary"] = summary

    if "eval_summary" in st.session_state:
        summary = st.session_state["eval_summary"]

        st.divider()

        # Metric cards
        m1, m2, m3, m4 = st.columns(4)
        m1.metric(
            "Tests Passed",
            f"{summary['passed']}/{summary['total']}",
            delta="All passing" if summary["failed"] == 0 else f"{summary['failed']} failing",
            delta_color="normal" if summary["failed"] == 0 else "inverse",
        )
        m2.metric("Avg Confidence (Legitimate)", f"{summary['avg_legit_confidence']:.0%}")
        m3.metric("Avg Confidence (All)", f"{summary['avg_confidence']:.0%}")
        m4.metric("Guardrail Trigger Rate", f"{summary['guardrail_trigger_rate']:.0%}")

        st.divider()

        # Category summary row
        st.subheader("Results by Category")
        cat_data = {}
        for row in summary["results"]:
            cat = row["category"]
            if cat not in cat_data:
                cat_data[cat] = {"passed": 0, "total": 0}
            cat_data[cat]["total"] += 1
            if row["passed"]:
                cat_data[cat]["passed"] += 1

        cols = st.columns(len(cat_data))
        for i, (cat, data) in enumerate(cat_data.items()):
            rate = data["passed"] / data["total"]
            emoji = "✅" if rate == 1.0 else "⚠️"
            cols[i].metric(f"{emoji} {cat}", f"{data['passed']}/{data['total']}")

        st.divider()

        # Results table with category filter
        st.subheader("Test Case Results")
        categories = ["All"] + sorted(set(r["category"] for r in summary["results"]))
        selected_cat = st.selectbox("Filter by category", categories, key="eval_filter")

        filtered = (
            summary["results"] if selected_cat == "All"
            else [r for r in summary["results"] if r["category"] == selected_cat]
        )

        for row in filtered:
            status_icon = "✅" if row["passed"] else "❌"
            with st.expander(
                f"{status_icon} [{row['id']}] [{row['category']}] {row['description']}"
            ):
                c1, c2, c3 = st.columns(3)
                c1.metric("Confidence", f"{row['confidence']:.0%}")
                c2.metric("Flagged", str(row["flagged"]))
                c3.metric("Status", "PASS" if row["passed"] else "FAIL")
                st.caption(f"**Question:** {row['question']}")
                if row["answer"]:
                    st.caption(
                        f"**Answer:** {row['answer'][:200]}"
                        f"{'...' if len(row['answer']) > 200 else ''}"
                    )
    else:
        st.info("Click **▶️ Run Evaluation** to run the test suite and see results.")


# ══════════════════════════════════════════════════════════════
# TAB 3 — PET MANAGEMENT
# ══════════════════════════════════════════════════════════════
with tab_pets:
    st.subheader("Your Pets")

    if not owner.pets:
        st.info("No pets yet. Add your first pet below.")
    else:
        for pet in owner.pets:
            with st.expander(f"🐾 {pet.name} — {pet.breed} ({pet.species}, {pet.age} yrs)"):

                # Pending tasks
                pending = pet.get_pending_tasks()
                if pending:
                    st.write("**Pending tasks:**")
                    for task in pending:
                        col_task, col_done = st.columns([5, 1])
                        with col_task:
                            st.write(
                                f"{task.emoji()} {task.priority_emoji()} "
                                f"**{task.description}** — "
                                f"{task.due_date} @ {task.due_time} "
                                f"({task.frequency})"
                            )
                        with col_done:
                            if st.button(
                                "✅ Done",
                                key=f"done_{pet.name}_{task.task_id}"
                            ):
                                task.mark_complete()
                                owner.save_to_json("data.json")
                                st.session_state.owner = owner
                                st.rerun()
                else:
                    st.write("No pending tasks.")

                st.divider()

                # Add task form
                st.write("**Add a task:**")
                task_col1, task_col2 = st.columns(2)
                with task_col1:
                    new_task_desc = st.text_input(
                        "Task description",
                        placeholder="e.g. Evening walk, Flea treatment",
                        key=f"task_input_{pet.name}",
                    )
                    task_date = st.date_input(
                        "Due date",
                        value=date.today(),
                        key=f"task_date_{pet.name}",
                    )
                    task_time = st.time_input(
                        "Due time",
                        value=dtime(8, 0),
                        key=f"task_time_{pet.name}",
                    )
                with task_col2:
                    task_type = st.selectbox(
                        "Task type",
                        ["general", "walk", "feeding", "medication", "vet"],
                        key=f"task_type_{pet.name}",
                    )
                    task_priority = st.selectbox(
                        "Priority",
                        ["medium", "high", "low"],
                        key=f"task_priority_{pet.name}",
                    )
                    task_freq = st.selectbox(
                        "Frequency",
                        ["once", "daily", "weekly"],
                        key=f"task_freq_{pet.name}",
                    )

                if st.button("➕ Add Task", key=f"add_task_{pet.name}"):
                    if new_task_desc.strip():
                        new_task = Task(
                            description=new_task_desc.strip(),
                            due_time=task_time.strftime("%H:%M"),
                            due_date=str(task_date),
                            frequency=task_freq,
                            priority=task_priority,
                            task_type=task_type,
                        )
                        pet.add_task(new_task)
                        owner.save_to_json("data.json")
                        st.session_state.owner = owner
                        st.success(f"✅ Task added to {pet.name}!")
                        st.rerun()
                    else:
                        st.error("Please enter a task description.")

    st.divider()
    st.subheader("Add a New Pet")

    with st.form("add_pet_form"):
        col1, col2 = st.columns(2)
        with col1:
            new_name    = st.text_input("Pet name")
            new_species = st.selectbox("Species", ["dog", "cat", "rabbit", "bird", "other"])
        with col2:
            new_breed = st.text_input("Breed")
            new_age   = st.number_input("Age (years)", min_value=0, max_value=30, value=1)

        submitted = st.form_submit_button("➕ Add Pet")
        if submitted:
            if new_name and new_breed:
                new_pet = Pet(
                    name=new_name,
                    species=new_species,
                    breed=new_breed,
                    age=int(new_age),
                )
                owner.add_pet(new_pet)
                owner.save_to_json("data.json")
                st.session_state.owner = owner
                st.success(f"✅ {new_name} added successfully!")
                st.rerun()
            else:
                st.error("Please fill in both name and breed.")