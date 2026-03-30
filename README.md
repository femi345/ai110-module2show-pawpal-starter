# PawPal+

A pet-care management app that helps owners track daily routines — feedings, walks, medications, and more — using object-oriented Python and a Streamlit UI.

Built for CodePath AI110 Module 2.

---

## Demo

<a href="/course_images/ai110/pawpal_screenshot.png" target="_blank"><img src='/course_images/ai110/pawpal_screenshot.png' title='PawPal App' width='' alt='PawPal App' class='center-block' /></a>

---

## Features

| Feature | Description |
|---|---|
| Owner and multi-pet management | Create an owner profile and add any number of pets |
| Task creation | Each task has a description, time (HH:MM), duration, priority, frequency, and due date |
| Chronological sorting | `Scheduler.sort_by_time()` sorts tasks by HH:MM so the schedule reads top-to-bottom |
| Priority sorting | `Scheduler.sort_by_priority()` ranks high to low, using time as a tiebreaker |
| Filtering | Filter by pet name, completion status, or due date |
| Conflict detection | `Scheduler.detect_conflicts()` flags tasks scheduled at the same time |
| Recurring tasks | Completing a daily or weekly task automatically creates the next occurrence via `timedelta` |
| Session persistence | `st.session_state` keeps the Owner object alive across Streamlit re-runs |
| Pet overview | A progress bar per pet shows completed vs total tasks |

---

## Smarter Scheduling

Four algorithmic features beyond a basic task list:

1. **Time sorting** — lambda sort on HH:MM strings gives correct chronological order for 24-hour times.
2. **Priority sorting** — a rank dictionary maps priority strings to integers 0-2 for a two-key sort.
3. **Recurring tasks** — `Task.mark_complete()` returns a new Task with `due_date + timedelta(days=1)` or `+ timedelta(weeks=1)`, which the Scheduler appends to the pet.
4. **Conflict detection** — tasks are grouped by time slot in a dictionary; any slot with more than one entry produces a warning string instead of an exception.

---

## Architecture

See `uml_final.md` for the Mermaid.js class diagram.

```
Owner
 └── Pet (1..*)
      └── Task (0..*)

Scheduler --queries--> Owner
```

`pawpal_system.py` contains all four classes. `app.py` imports them and wires the UI to the logic layer via `st.session_state`.

---

## Getting Started

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python main.py          # CLI demo
streamlit run app.py    # Streamlit UI
```

---

## Testing

```bash
python -m pytest
```

23 tests across the following areas:

| Area | What is tested |
|---|---|
| Task completion | `mark_complete()` sets the flag; returns None for one-off tasks |
| Recurrence | Daily tasks get due_date + 1 day; weekly get + 7 days; attributes are preserved |
| Pet management | Adding and removing tasks changes `task_count()` correctly |
| Owner aggregation | `get_all_tasks()` collects tasks across all pets |
| Sorting | Time-sorted output is chronological; priority sort puts high first |
| Filtering | Pet-name, completion, and due-date filters return correct subsets |
| Conflict detection | Same-time slots trigger one warning; different times trigger none |
| Scheduler recurrence | `mark_task_complete()` appends the follow-up task to the pet |

Confidence: 4/5. All happy paths and key edge cases pass. Gaps: overlapping duration windows, malformed time strings, tasks spanning midnight.

---

## Project Structure

```
pawpal_system.py   all business logic (Owner, Pet, Task, Scheduler)
app.py             Streamlit UI
main.py            CLI demo script
tests/
  test_pawpal.py   pytest suite (23 tests)
uml_final.md       Mermaid.js class diagram
reflection.md      design and AI collaboration reflection
requirements.txt
```
