# PawPal+ 🐾

A smart pet-care management app that helps busy owners stay on top of daily routines — feedings, walks, medications, and more — using object-oriented Python and a Streamlit UI.

Built for **CodePath AI110 Module 2**.

---

## 📸 Demo

<a href="/course_images/ai110/pawpal_screenshot.png" target="_blank">
  <img src='/course_images/ai110/pawpal_screenshot.png' title='PawPal App' width='' alt='PawPal App' class='center-block' />
</a>

---

## ✨ Features

| Feature | Description |
|---|---|
| **Owner & multi-pet management** | Create an owner profile and add any number of pets (dog, cat, rabbit, …) |
| **Rich task creation** | Each task carries a description, time (HH:MM), duration, priority (low/medium/high), frequency, and due date |
| **Chronological sorting** | `Scheduler.sort_by_time()` uses a lambda key on HH:MM strings so today's schedule always reads top-to-bottom |
| **Priority sorting** | `Scheduler.sort_by_priority()` ranks high → medium → low, using time as a tiebreaker |
| **Flexible filtering** | Filter by pet name, completion status, or due date — or combine all three |
| **Conflict detection** | `Scheduler.detect_conflicts()` scans all tasks and surfaces `⚠️` warnings for exact time collisions |
| **Recurring tasks** | `mark_complete()` on a daily/weekly task automatically creates the next occurrence via `timedelta` |
| **Session persistence** | `st.session_state` keeps the `Owner` object alive across Streamlit re-runs |
| **Pet overview cards** | A progress bar per pet shows completed vs total tasks at a glance |

---

## 🧠 Smarter Scheduling

PawPal+ implements four algorithmic capabilities beyond a simple list:

1. **Sorting by time** — `sorted(..., key=lambda pt: pt[1].time)` over HH:MM strings gives correct lexicographic chronological order for 24-hour times.
2. **Priority-weighted sorting** — a `_PRIORITY_RANK` lookup dict maps string priorities to integers 0–2, enabling a two-key sort.
3. **Recurring task automation** — `Task.mark_complete()` returns a new `Task` with `due_date + timedelta(days=1)` (daily) or `+ timedelta(weeks=1)` (weekly), which the `Scheduler` immediately appends to the pet's task list.
4. **Conflict detection** — `detect_conflicts()` groups all tasks by time slot using a dictionary and flags any slot with more than one entry, returning human-readable warning strings rather than raising exceptions.

---

## 🏗️ Architecture

See `uml_final.md` for the Mermaid.js class diagram.

```
Owner
 └── Pet (1..*)
      └── Task (0..*)

Scheduler ──queries──> Owner
```

`pawpal_system.py` contains all four classes.
`app.py` imports them and wires the UI to the logic layer via `st.session_state`.

---

## 🚀 Getting Started

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Run the CLI demo
python main.py

# Launch the Streamlit app
streamlit run app.py
```

---

## 🧪 Testing PawPal+

```bash
python -m pytest
```

The test suite (`tests/test_pawpal.py`) covers **23 test cases** across five areas:

| Area | What is tested |
|---|---|
| Task completion | `mark_complete()` sets flag; returns `None` for one-off tasks |
| Recurrence logic | Daily tasks get `due_date + 1 day`; weekly tasks get `+ 7 days`; attributes are preserved |
| Pet management | Adding/removing tasks changes `task_count()` correctly |
| Owner aggregation | `get_all_tasks()` collects across all pets |
| Sorting | Time-sorted output is strictly chronological; priority sort puts high first |
| Filtering | Pet-name, completion, and due-date filters return exact expected subsets |
| Conflict detection | Same-time slots trigger exactly one warning; different times trigger none |
| Scheduler recurrence | `mark_task_complete()` appends the follow-up task to the pet |

**Confidence level: ★★★★☆**
All happy paths and the most important edge cases (empty pet, one-off tasks, three-way conflicts) pass.
Untested edge cases for future iteration: overlapping time *ranges* (not just exact collisions), malformed HH:MM strings, and tasks spanning midnight.

---

## 📂 Project Structure

```
pawpal_system.py   ← all business logic (Owner, Pet, Task, Scheduler)
app.py             ← Streamlit UI
main.py            ← CLI demo / manual testing script
tests/
  test_pawpal.py   ← pytest suite (23 tests)
uml_final.md       ← Mermaid.js class diagram
reflection.md      ← design and AI collaboration reflection
requirements.txt
```
